from typing import List, Tuple, Optional
from data_manager.rating import Rating
from model.embedding import Embedding
import heapq


class Movie(object):
    def __init__(self):
        self.movieId = -1
        self.title = ''
        self.releaseYear = 0
        self.imdbId = ''
        self.tmdbId = ''
        self.genres = []  # type: List[str]
        self.ratingNumber = 0
        self.avgRating = 0.0

        # embedding of the movie
        # @JsonIgnore
        self.emb = None  # type: Optional[Embedding]

        self.TOP_RATING_SIZE = 10

        # all rating scores list
        # @JsonIgnore
        self.ratings = []  # type: List[Rating]

        # @JsonSerialize(using = RatingListSerializer.class)
        self.topRatings = []  # type: List[Tuple[float, Rating]]

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["emb"]
        del state["ratings"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def add_genre(self, genre):
        self.genres.append(genre)

    def add_rating(self, rating: Rating):
        self.avgRating = (self.avgRating * self.ratingNumber + rating.score) / (self.ratingNumber + 1)
        self.ratingNumber += 1
        self.ratings.append(rating)
        self.add_top_rating(rating)

    def add_top_rating(self, rating: Rating):
        heapq.heappush(self.topRatings, (rating.score, rating))
        if len(self.topRatings) > self.TOP_RATING_SIZE:
            heapq.heappop(self.topRatings)

    def get_emb(self):
        return self.emb


