from functools import total_ordering


@total_ordering
class Rating(object):
    def __init__(self):
        self._movie_id = -1  # type: int
        self._user_id = -1  # type: int
        self._score = 0.0  # type: float
        self._timestamp = 0  # type: int

    @property
    def movie_id(self):
        return self._movie_id

    @movie_id.setter
    def movie_id(self, movie_id: int):
        self._movie_id = movie_id

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: int):
        self._user_id = user_id

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score: float):
        self._score = score

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: int):
        self._timestamp = timestamp

    def __eq__(self, other):
        return self._score == other.score

    def __lt__(self, other):
        return self._score < other.score
