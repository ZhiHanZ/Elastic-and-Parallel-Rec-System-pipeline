import jsonpickle
from data_manager.data_manager import DataManager


class MovieService:
    @classmethod
    def do_get(self, movie_id: int):
        movie = DataManager.get_instance().get_movie_by_id(movie_id)

        if movie is not None:
            return jsonpickle.encode(movie, unpicklable=False)
        return ""