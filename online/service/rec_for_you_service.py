import jsonpickle
from rec_process import rec_for_you_process


class RecForYouService:
    @classmethod
    def do_get(self, id: int, size: int, model: str):
        movies = rec_for_you_process.get_rec_list(id, size, model)
        return jsonpickle.dumps(movies, unpicklable=False)
