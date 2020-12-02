from model.embedding import Embedding


class Utility(object):
    @staticmethod
    def parse_emb_str(embs_str: str):
        emb_strs = embs_str.split()
        emb = Embedding()
        for emb_str in emb_strs:
            emb.add_dim(float(emb_str))
        return emb
