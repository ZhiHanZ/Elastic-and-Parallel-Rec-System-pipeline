from os.path import *
from pyspark.sql import SparkSession, Row
from pyspark import SparkConf
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.mllib.feature import Word2Vec, Word2VecModel
from pyspark.ml.feature import BucketedRandomProjectionLSH
from pyspark.ml.linalg import Vectors
import redis
import logging
import random
import numpy as np
import pandas as pd
from typing import List

params = ()


class Embedding:
    def __init__(self):
        self.redisEndpoint = "localhost"
        self.redisPort = 6379

    def process_item_sequence(self, spark_session: SparkSession, raw_sample_data_path: str):
        """
        process item sequence, integrate movieId into movieStr
        :param spark_session:
        :param raw_sample_data_path:
        :return:
        """
        root_dir = dirname(dirname(dirname(abspath(__file__))))
        rating_resource_path = join(root_dir, "resources", raw_sample_data_path)

        rating_samples = spark_session.read.format("csv").option("header", "true").load(rating_resource_path)

        schema = StructType([
            StructField("userId", StringType()),
            # StructField("timestamp", StringType()),
            # StructField("rating", StringType()),
            StructField("movieIds", ArrayType(StringType()))
        ])

        @pandas_udf(schema, functionType=PandasUDFType.GROUPED_MAP)
        def udf_sort(df):
            result = df.drop(columns=["rating"])
            result = result.groupby(by="userId").apply(lambda x: x.sort_values(["timestamp"]))
            result = result.drop(columns=["timestamp"]).reset_index(drop=True)
            result = result.groupby(by="userId").agg(lambda x: tuple(x)).applymap(list).reset_index()
            result = result.rename(columns={"movieId": "movieIds"})
            return result

        rating_samples.show(10)
        user_sequence = rating_samples. \
            where("rating >= 3.5"). \
            groupBy("userId"). \
            apply(udf_sort). \
            withColumn("movieIdStr", array_join(col("movieIds"), " "))

        user_sequence.select("userId", "movieIdStr").show(10, truncate=False)
        result = user_sequence.select("movieIdStr").rdd.map(lambda x: x["movieIdStr"].split(" "))

        return result

    def embedding_lsh(self, spark_session: SparkSession, movie_emb_map):
        movie_emb_seq = []
        for movieId, vector in movie_emb_map.items():
            movie_emb_seq.append((movieId, Vectors.dense(vector)))
        movie_emb_df = spark.createDataFrame(movie_emb_seq).toDF("movieId", "emb")

        bucket_projection_lsh = BucketedRandomProjectionLSH().setBucketLength(0.1).setNumHashTables(3).setInputCol("emb").\
            setOutputCol("bucketId")
        bucket_model = bucket_projection_lsh.fit(movie_emb_df)

        emb_bucket_result = bucket_model.transform(movie_emb_df)

        print("movieId, emb, bucketId schema:")
        emb_bucket_result.printSchema()
        print("movieId, emb, bucketId data result:")
        emb_bucket_result.show(10, truncate=False)

        print("Approximately searching for 5 nearest neighbors of the sample embedding:")
        sampleEmb = Vectors.dense(0.795, 0.583, 1.120, 0.850, 0.174, -0.839, -0.0633, 0.249, 0.673, -0.237)
        bucket_model.approxNearestNeighbors(movie_emb_df, sampleEmb, 5).show(truncate=False)

    def train_item_to_vec(self, spark_session: SparkSession, samples, emb_length: int, emb_output_file_name: str,
                      save_to_redis: bool, redis_key_prefix: str):
        """
        train a word2vec model based on movie samples
        :param spark_session:
        :param samples:
        :param emb_length:
        :param emb_output_file_name:
        :param save_to_redis:
        :param redis_key_prefix:
        :return:
        """
        word2vec = Word2Vec().setVectorSize(emb_length).setWindowSize(5).setNumIterations(10)
        model = word2vec.fit(samples)
        synonyms = model.findSynonyms("158", 20)
        for synonym, cosine_sim in synonyms:
            print(synonym, cosine_sim)

        root_dir = dirname(dirname(dirname(abspath(__file__))))
        rating_resource_path = join(root_dir, "resources", "webroot/modeldata/")

        file = open(join(rating_resource_path, emb_output_file_name), "w")

        for movieId, vector in model.getVectors().items():
            file.write(movieId + ":" + " ".join([str(num) for num in vector]) + "\n")

        if save_to_redis:
            redis_client = redis.Redis(host=self.redisEndpoint, port=self.redisPort)
            for movieId, vector in model.getVectors().items():
                redis_client.set(redis_key_prefix + ":" + movieId, " ".join([str(num) for num in vector]), ex=60*60*24)
            redis_client.close()
        self.embedding_lsh(spark_session, model.getVectors())
        return model

    def generate_transition_matrix(self, samples):
        def flat_func(sample):
            pair_seq = []
            previous_item = None
            for element in sample:
                if previous_item is not None:
                    pair_seq.append((previous_item, element))
                previous_item = element
            return pair_seq

        pair_samples = samples.flatMap(flat_func)

        pair_count_map = pair_samples.countByValue()
        pair_total_count = 0
        transition_count_matrix = dict()
        item_count_map = dict()

        for pair_items, count in pair_count_map.items():
            if pair_items[0] not in transition_count_matrix:
                transition_count_matrix[pair_items[0]] = dict()
            transition_count_matrix[pair_items[0]][pair_items[1]] = count
            item_count_map[pair_items[0]] = item_count_map.get(pair_items[0], 0) + count
            pair_total_count = pair_total_count + count

        transition_matrix = dict()
        item_distribution = dict()

        for item_a_id, transition_map in transition_count_matrix.items():
            transition_matrix[item_a_id] = dict()
            for item_b_id, transition_count in transition_map.items():
                transition_matrix[item_a_id][item_b_id] = float(transition_count) / item_count_map[item_a_id]

        for item_id, item_count in item_count_map.items():
            item_distribution[item_id] = float(item_count) / pair_total_count

        return transition_matrix, item_distribution

    def one_random_walk(self, transition_matrix, item_distribution, sample_length: int):
        sample = []
        random_double = random.random()
        first_item = ""
        accumulate_prob = 0
        for item, prob in item_distribution.items():
            accumulate_prob += prob
            if accumulate_prob >= random_double:
                first_item = item
                break
        sample.append(first_item)
        cur_element = first_item
        for _ in range(sample_length):
            if cur_element not in item_distribution or cur_element not in transition_matrix:
                break
            prob_distribution = transition_matrix[cur_element]
            random_double = random.random()
            for item, prob in prob_distribution.items():
                if random_double >= prob:
                    cur_element = item
                    break
            sample.append(cur_element)
        return sample

    def random_walk(self, transition_matrix, item_distribution, sample_count: int, sample_length: int):
        samples = []
        for _ in range(sample_count):
            samples.append(self.one_random_walk(transition_matrix, item_distribution, sample_length))
        return samples

    def graph_emb(self, samples, spark_session: SparkSession, emb_length: int, emb_output_file_name: str,
                  save_to_redis: bool, redis_key_prefix: str):
        transition_matrix, item_distribution = self.generate_transition_matrix(samples)

        print(len(transition_matrix))
        print(len(item_distribution))

        sampleCount = 20000
        sampleLength = 10

        new_samples = self.random_walk(transition_matrix, item_distribution, sampleCount, sampleLength)
        rdd_samples = spark_session.sparkContext.parallelize(new_samples)

        return self.train_item_to_vec(spark_session, rdd_samples, emb_length, emb_output_file_name, save_to_redis,
                                      redis_key_prefix)

    def generate_user_emb(self, spark_session: SparkSession, raw_sample_data_path: str, word2vec_model: Word2VecModel,
                          emb_length: int, emb_output_file_name: str, save_to_redis: bool, redis_key_prefix: str):
        """
        generate user embedding which is constructed by related movie embeddings
        :param spark_session:
        :param raw_sample_data_path:
        :param word2vec_model:
        :param emb_length:
        :param emb_output_file_name:
        :param save_to_redis:
        :param redis_key_prefix:
        :return:
        """
        root_dir = dirname(dirname(dirname(abspath(__file__))))
        rating_resource_path = join(root_dir, "resources", raw_sample_data_path)

        rating_samples = spark_session.read.format("csv").option("header", "true").load(rating_resource_path)

        rating_samples.show(10, truncate=False)

        user_embeddings_dict = dict()
        movie_keys = word2vec_model.getVectors().keys()

        for row in rating_samples.collect():
            user_id = row["userId"]
            movie_id = row["movieId"]
            if movie_id not in movie_keys:
                movie_emb = np.zeros(emb_length)
            else:
                movie_emb = word2vec_model.transform(movie_id).toArray()
            if user_id in user_embeddings_dict:
                user_embeddings_dict[user_id] += np.copy(movie_emb)
            else:
                user_embeddings_dict[user_id] = np.copy(movie_emb)

        root_dir = dirname(dirname(dirname(abspath(__file__))))
        rating_resource_path = join(root_dir, "resources", "webroot/modeldata/")

        file = open(join(rating_resource_path, emb_output_file_name), "w")

        for user_id, user_emb in user_embeddings_dict.items():
            file.write(user_id + ":" + " ".join([str(num) for num in user_emb]) + "\n")

        if save_to_redis:
            redis_client = redis.Redis(host=self.redisEndpoint, port=self.redisPort)
            for user_id, user_emb in user_embeddings_dict.items():
                redis_client.set(redis_key_prefix + ":" + user_id, " ".join([str(num) for num in user_emb]), ex=60*60*24)
            redis_client.close()


if __name__ == "__main__":
    logging.getLogger("org").setLevel(logging.ERROR)
    conf = SparkConf().setMaster("local").setAppName("ctrModel").set("spark.submit.deployMode", "client")

    spark = SparkSession.builder.config(conf=conf).getOrCreate()

    raw_sample_data_path = "webroot/sampledata/ratings.csv"

    emb_length = 10

    embedding = Embedding()

    samples = embedding.process_item_sequence(spark, raw_sample_data_path)

    model = embedding.train_item_to_vec(spark, samples, emb_length, "item2vecEmb.csv", False, "i2vEmb")
    # embedding.graph_emb(samples, spark, emb_length, "itemGraphEmb.csv", True, "graphEmb")
    embedding.generate_user_emb(spark, raw_sample_data_path, model, emb_length, "userEmb.csv", False, "uEmb")
