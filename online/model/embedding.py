from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional


class Embedding(object):
    def __init__(self, emb_vector: Optional[List[float]] = None):
        if emb_vector is None:
            emb_vector = []
        self._emb_vector = emb_vector  # type: List[float]

    def add_dim(self, element: float):
        self._emb_vector.append(element)

    @property
    def emb_vector(self):
        return self._emb_vector

    @emb_vector.setter
    def emb_vector(self, emb_vector: List[float]):
        self._emb_vector = emb_vector

    # Calculates cosine similarity with other embedding
    # other is None or an instance of Embedding
    def calculate_similarity(self, other) -> float:
        if self._emb_vector is None or \
                other is None or other.emb_vector is None or \
                len(self._emb_vector) != len(other.emb_vector):
            return -1
        return cosine_similarity([self.emb_vector], [other.emb_vector])[0]
