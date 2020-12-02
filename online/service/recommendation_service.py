import jsonpickle
from data_manager.data_manager import DataManager


class RecommendationService:
    @classmethod
    def do_get(self, genre: str, size: int, sortby: str):
        movies = DataManager.get_instance().get_movies_by_genre(genre, size, sortby)
        return jsonpickle.encode(movies, unpicklable=False)