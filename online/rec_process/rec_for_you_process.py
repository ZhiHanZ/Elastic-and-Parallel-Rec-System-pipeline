from data_manager.data_manager import DataManager
from data_manager.redis_client import RedisClient
from util.config import Config
from util.utility import Utility


def get_rec_list(user_id: int, size: int, model: str):
    user = DataManager.get_instance().get_user_by_id(user_id)
    if user is None:
        return list()
    CANDIDATE_SIZE = 800
    candiadtes = DataManager.get_instance().get_movies(CANDIDATE_SIZE, "rating")

    if Config.EMB_DATA_SOURCE == Config.DATA_SOURCE_REDIS:
        user_emb_key = "uEmb:" + str(user_id)
        user_emb = RedisClient.get_instance().get(user_emb_key)
        if user_emb is not None:
            user.set_emb(Utility.parse_emb_str(user_emb))

    ranked_list = ranker(user, candiadtes, model)

    if len(ranked_list) > size:
        return ranked_list[:size]
    return ranked_list


def ranker(user, candidates, model):
    candidate_score_dict = dict()
    for candidate in candidates:
        if model == "emb":
            similarity = calculate_emb_similar_score(user, candidate)
        else:
            similarity = calculate_emb_similar_score(user, candidate)
        candidate_score_dict[candidate] = similarity
    ranked_list = [item[0] for item in sorted(candidate_score_dict.items(), key=lambda x: x[1])]
    return ranked_list


def calculate_emb_similar_score(user, candidate):
    if user is None or candidate is None or user.get_emb() is None:
        return -1
    return user.get_emb().calculate_similarity(candidate.get_emb())
