from sklearn.metrics.pairwise import cosine_similarity

class Embedding:
    def __init__(self, emb_vector=None):
        if emb_vector is None:
            emb_vector = list()
        self.emb_vector = emb_vector

    def add_dim(self, element):
        self.emb_vector.append(element)

    def get_emb_vector(self):
        return self.emb_vector

    def set_emb_vector(self, emb_vector):
        self.emb_vector = emb_vector

    def calculate_similarity(self, other_embedding):
        return cosine_similarity(self.emb_vector, other_embedding.emb_vector)