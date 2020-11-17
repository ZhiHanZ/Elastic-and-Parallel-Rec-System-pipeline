from typing import List, Optional
import math


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
        dot_product = 0
        denom1 = 0
        denom2 = 0
        for i in range(len(self._emb_vector)):
            val1 = self._emb_vector[i]
            val2 = other.emb_vector[i]
            dot_product += val1 * val2
            denom1 += val1 * val1
            denom2 += val2 * val2
        if denom1 == 0 or denom2 == 0:
            return 0
        return dot_product / math.sqrt(denom1 * denom2)
