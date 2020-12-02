import jsonpickle
from rec_process import similiar_movie_process


class SimilarMovieService:
    @classmethod
    def do_get(self, movie_id: int, size: int, model: str):
        movies = similiar_movie_process.get_rec_list(movie_id, size, model)
        return jsonpickle.encode(movies, unpicklable=False)