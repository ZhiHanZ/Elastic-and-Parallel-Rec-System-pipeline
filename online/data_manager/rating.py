from functools import total_ordering


@total_ordering
class Rating(object):
    def __init__(self):
        self.movieId = -1  # type: int
        self.userId = -1  # type: int
        self.score = 0.0  # type: float
        self.timestamp = 0  # type: int

    def __eq__(self, other):
        return self.score == other.score

    def __lt__(self, other):
        return self.score < other.score
