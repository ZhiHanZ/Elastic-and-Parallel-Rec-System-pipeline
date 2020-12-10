from typing import List, Optional
from data_manager.rating import Rating
from model.embedding import Embedding


class User(object):
    def __init__(self):
        self.userId = -1
        self.avgRating = 0.0
        self.highestRating = 0.0
        self.lowestRating = 5.0
        self.ratingCount = 0

        # @JsonSerialize(using = RatingListSerializer.class)
        self.ratings = []  # type: List[Rating]

        # embedding of user's preference
        # @JsonIgnore
        self.emb = None  # type: Optional[Embedding]

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["emb"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def add_rating(self, rating: Rating):
        self.avgRating = (self.avgRating * self.n_ratings + rating.score) / (self.n_ratings + 1)
        self.ratings.append(rating)
        self.ratingCount += 1
        if rating.score > self.highestRating:
            self.highestRating = rating.score
        if rating.score < self.lowestRating:
            self.lowestRating = rating.score

    @property
    def lowest_rating(self):
        if self.n_ratings == 0:
            return -1
        return self.lowestRating

    @property
    def n_ratings(self):
        return len(self.ratings)

    def get_emb(self):
        return self.emb

