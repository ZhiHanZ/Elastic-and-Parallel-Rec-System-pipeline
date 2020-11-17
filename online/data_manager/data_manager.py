from collections import defaultdict
from typing import Dict, List, Set, Optional
from .movie import Movie
from .user import User
from .rating import Rating
from .redis_client import RedisClient
from ..util.config import Config
from ..util.utility import Utility
import threading


class DataManager(object):
    # singleton instance
    _instance = None  # type: DataManager
    _instance_lock = threading.Lock()

    def __init__(self):
        self.movie_map = {}  # type: Dict[int, Movie]
        self.user_map = {}  # type: Dict[int, User]
        # genre reverse index for quick querying all movies in a genre
        self.genre_reverse_index_map = defaultdict(list)  # type: Dict[str, List[Movie]]

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = DataManager()
        return cls._instance

    # load data from file system including movie, rating, link data and model data like embedding vectors.
    # throws Exception in Java
    def load_data(self, movie_data_path: str,
                  link_data_path: str, rating_data_path: str,
                  movie_emb_path: str, user_emb_path: str,
                  movie_redis_key: str, user_redis_key: str):
        self._load_movie_data(movie_data_path)
        self._load_link_data(link_data_path)
        self._load_rating_data(rating_data_path)
        self._load_movie_emb(movie_emb_path, movie_redis_key)
        self._load_user_emb(user_emb_path, user_redis_key)

    # load movie data from movies.csv
    # throws Exception in Java
    def _load_movie_data(self, movie_data_path: str):
        print("Loading movie data from %s ..." % movie_data_path)
        skip_first_line = True
        with open(movie_data_path) as f:
            for movie_raw_data in f:
                if skip_first_line:
                    skip_first_line = False
                    continue
                movie_data = movie_raw_data.split(",")
                if len(movie_data) == 3:
                    id_str = movie_data[0]
                    title_str = movie_data[1].strip()
                    genres_str = movie_data[2].strip()
                    movie = Movie()
                    movie.movie_id = int(id_str)
                    release_year = self._parse_release_year(title_str)
                    if release_year == -1:
                        movie.title = movie_data[1].strip()
                    else:
                        movie.release_year = release_year
                        movie.title = title_str[:-6].strip()
                    if len(genres_str) > 0:
                        genres = genres_str.split("|")
                        for genre in genres:
                            movie.add_genre(genre)
                            self._add_movie_to_genre_index(genre, movie)
                    self.movie_map[movie.movie_id] = movie
        print("Loading movie data completed. %d movies in total." % len(self.movie_map))

    # load movie embedding
    # throws Exception in Java
    def _load_movie_emb(self, movie_emb_path: str, emb_key: str):
        if Config.EMB_DATA_SOURCE == Config.DATA_SOURCE_FILE:
            print("Loading movie embedding from %s ..." % movie_emb_path)
            valid_emb_count = 0
            with open(movie_emb_path) as f:
                for movie_raw_emb_data in f:
                    movie_emb_data = movie_raw_emb_data.split(":")
                    if len(movie_emb_data) == 2:
                        m = self.get_movie_by_id(int(movie_emb_data[0]))
                        if m is None:
                            continue
                        m.emb = Utility.parse_emb_str(movie_emb_data[1])
                        valid_emb_count += 1
            print("Loading movie embedding completed. %d movie embeddings in total." % valid_emb_count)
        else:
            print("Loading movie embedding from Redis ...")
            movie_emb_keys = RedisClient.get_instance().keys(emb_key + "*")  # type: Set[str]
            valid_emb_count = 0
            for movieEmbKey in movie_emb_keys:
                movie_id = movieEmbKey.split(":")[1]
                m = self.get_movie_by_id(int(movie_id))
                if m is None:
                    continue
                m.emb = Utility.parse_emb_str(RedisClient.get_instance().get(movieEmbKey))
                valid_emb_count += 1
            print("Loading movie embedding completed. %d movie embeddings in total." % valid_emb_count)

    # load user embedding
    # throws Exception in Java
    def _load_user_emb(self, user_emb_path: str, emb_key: str):
        if Config.EMB_DATA_SOURCE == Config.DATA_SOURCE_FILE:
            print("Loading user embedding from %s ..." % user_emb_path)
            valid_emb_count = 0
            with open(user_emb_path) as f:
                for user_raw_emb_data in f:
                    user_emb_data = user_raw_emb_data.split(":")
                    if len(user_emb_data) == 2:
                        u = self.get_user_by_id(int(user_emb_data[0]))
                        if u is None:
                            continue
                        u.emb = Utility.parse_emb_str(user_emb_data[1])
                        valid_emb_count += 1
            print("Loading user embedding completed. %d user embeddings in total." % valid_emb_count)

    # parse release year
    def _parse_release_year(self, raw_title: Optional[str]):
        if raw_title is None or len(raw_title.strip()) < 6:
            return -1
        else:
            year_str = raw_title.strip()[-5:-1]
            try:
                return int(year_str)
            except ValueError:
                return -1

    # load links data from links.csv
    # throws Exception in Java
    def _load_link_data(self, link_data_path: str):
        print("Loading link data from %s ..." % link_data_path)
        count = 0
        skip_first_line = True
        with open(link_data_path) as f:
            for link_raw_data in f:
                if skip_first_line:
                    skip_first_line = False
                    continue
                link_data = link_raw_data.split(",")
                if len(link_data) == 3:
                    movie_id = int(link_data[0])
                    movie = self.get_movie_by_id(movie_id)
                    if movie is not None:
                        count += 1
                        movie.imdb_id = link_data[1].strip()
                        movie.tmdb_id = link_data[2].strip()
        print("Loading link data completed. %d links in total." % count)
        
    # load ratings data from ratings.csv
    # throws Exception in Java
    def _load_rating_data(self, rating_data_path: str):
        print("Loading rating data from %s ..." % rating_data_path)
        skip_first_line = True
        count = 0
        with open(rating_data_path) as f:
            for rating_raw_data in f:
                if skip_first_line:
                    skip_first_line = False
                    continue
                rating_data = rating_raw_data.split(",")
                if len(rating_data) == 4:
                    count += 1
                    rating = Rating()
                    rating.user_id = int(rating_data[0])
                    rating.movie_id = int(rating_data[1])
                    rating.score = float(rating_data[2])
                    rating.timestamp = int(rating_data[3])
                    movie = self.get_movie_by_id(rating.movie_id)
                    if movie is not None:
                        movie.add_rating(rating)
                    if rating.user_id not in self.user_map:
                        user = User()
                        user.user_id = rating.user_id
                        self.user_map[user.user_id] = user
                    self.user_map[rating.user_id].add_rating(rating)

        print("Loading rating data completed. %d ratings in total." % count)

    # add movie to genre reversed index
    def _add_movie_to_genre_index(self, genre: str, movie: Movie):
        self.genre_reverse_index_map[genre].append(movie)

    # get movies by genre, and order the movies by sort_by method
    def get_movies_by_genre(self, genre: Optional[str], size: int, sort_by: str) -> List[Movie]:
        if genre is not None:
            movies = self.genre_reverse_index_map[genre].copy()
            if sort_by == "rating":
                movies.sort(key=lambda m: m.avg_rating)
            elif sort_by == "release_year":
                movies.sort(key=lambda m: m.release_year)
            return movies[:size]
        return []

    # get top N movies order by sort_by method
    def get_movies(self, size: int, sort_by: str) -> List[Movie]:
        movies = list(self.movie_map.values())
        if sort_by == "rating":
            movies.sort(key=lambda m: m.avg_rating)
        elif sort_by == "release_year":
            movies.sort(key=lambda m: m.release_year)
        return movies[:size]

    # get movie object by movie id
    def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        return self.movie_map.get(movie_id, None)

    # get user object by user id
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.user_map.get(user_id, None)
