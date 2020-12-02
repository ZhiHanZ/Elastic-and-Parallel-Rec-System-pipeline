from typing import List, Optional
from data_manager.rating import Rating
from model.embedding import Embedding


class User(object):
    def __init__(self):
        self._user_id = -1
        self._avg_rating = 0.0
        self._highest_rating = 0.0
        self._lowest_rating = 5.0
        self._rating_count = 0

        # @JsonSerialize(using = RatingListSerializer.class)
        self._ratings = []  # type: List[Rating]

        # embedding of user's preference
        # @JsonIgnore
        self._emb = None  # type: Optional[Embedding]

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: int):
        self._user_id = user_id

    @property
    def ratings(self):
        return self._ratings

    @ratings.setter
    def ratings(self, ratings: List[Rating]):
        self._ratings = ratings

    def add_rating(self, rating: Rating):
        self._avg_rating = (self._avg_rating * self.n_ratings + rating.score) / (self.n_ratings + 1)
        self._ratings.append(rating)
        self._rating_count += 1
        if rating.score > self._highest_rating:
            self._highest_rating = rating.score
        if rating.score < self._lowest_rating:
            self._lowest_rating = rating.score

    @property
    def avg_rating(self):
        return self._avg_rating

    @property
    def highest_rating(self):
        if self.n_ratings == 0:
            return -1
        return self._highest_rating

    @property
    def lowest_rating(self):
        if self.n_ratings == 0:
            return -1
        return self._lowest_rating

    @property
    def n_ratings(self):
        return len(self._ratings)

    @property
    def emb(self):
        return self._emb

    @emb.setter
    def emb(self, emb: Embedding):
        self._emb = emb
