from typing import List, Tuple, Optional
from data_manager.rating import Rating
from model.embedding import Embedding
import heapq


class Movie(object):
    def __init__(self):
        self._movie_id = -1
        self._title = ''
        self._release_year = 0
        self._imdb_id = ''
        self._tmdb_id = ''
        self._genres = []  # type: List[str]
        self._rating_number = 0
        self._avg_rating = 0.0

        # embedding of the movie
        # @JsonIgnore
        self._emb = None  # type: Optional[Embedding]

        self.TOP_RATING_SIZE = 10

        # all rating scores list
        # @JsonIgnore
        self._ratings = []  # type: List[Rating]

        # @JsonSerialize(using = RatingListSerializer.class)
        self._top_ratings = []  # type: List[Tuple[float, Rating]]

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_emb"]
        del state["_ratings"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    @property
    def movie_id(self):
        return self._movie_id

    @movie_id.setter
    def movie_id(self, movie_id: int):
        self._movie_id = movie_id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = title

    @property
    def release_year(self):
        return self._release_year

    @release_year.setter
    def release_year(self, release_year: int):
        self._release_year = release_year

    @property
    def genres(self):
        return self._genres

    def add_genre(self, genre: str):
        self._genres.append(genre)

    @genres.setter
    def genres(self, genres: List[str]):
        self._genres = genres.copy()

    @property
    def ratings(self):
        return self._ratings

    def add_rating(self, rating: Rating):
        self._avg_rating = (self._avg_rating * self.rating_number + rating.score) / (self.rating_number + 1)
        self._rating_number += 1
        self._ratings.append(rating)
        self.add_top_rating(rating)

    def add_top_rating(self, rating: Rating):
        heapq.heappush(self._top_ratings, (rating.score, rating))
        if len(self._top_ratings) > self.TOP_RATING_SIZE:
            heapq.heappop(self._top_ratings)

    @property
    def imdb_id(self):
        return self._imdb_id

    @imdb_id.setter
    def imdb_id(self, imdb_id: str):
        self._imdb_id = imdb_id

    @property
    def tmdb_id(self):
        return self._tmdb_id

    @tmdb_id.setter
    def tmdb_id(self, tmdb_id: str):
        self._tmdb_id = tmdb_id

    @property
    def rating_number(self):
        return self._rating_number

    @property
    def avg_rating(self):
        return self._avg_rating

    @property
    def emb(self):
        return self._emb

    @emb.setter
    def emb(self, emb: Embedding):
        self._emb = emb
