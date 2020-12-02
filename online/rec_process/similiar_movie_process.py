from data_manager.data_manager import DataManager


def get_rec_list(movie_id: int, size: int, model: str):
    movie = DataManager.get_instance().get_movie_by_id(movie_id)
    if movie is None:
        return list()
    candidates = candidate_generator(movie)
    ranked_list = ranker(movie, candidates, model)

    if len(ranked_list) > size:
        return ranked_list[:size]
    return ranked_list


def candidate_generator(movie):
    candidate_dict = dict()
    for genre in movie.genres:
        one_candidates = DataManager.get_instance().get_movies_by_genre(genre, 100, "rating")
        for candidate in one_candidates:
            candidate_dict[candidate.movie_id] = candidate
    del candidate_dict[movie.movie_id]
    return candidate_dict.values()


def ranker(movie, candidates, model):
    candidate_score_dict = dict()
    for candidate in candidates:
        if model == "emb":
            similarity = calculate_emb_similar_score(movie, candidate)
        else:
            similarity = calculate_similar_score(movie, candidate)
        candidate_score_dict[candidate] = similarity
    ranked_list = [item[0] for item in sorted(candidate_score_dict.items(), key=lambda x: x[1], reverse=True)]
    return ranked_list


def calculate_similar_score(movie, candidate):
    same_genre_count = 0
    for genre in movie.get_genres():
        if genre in candidate.get_genres():
            same_genre_count += 1

    genre_similarity = same_genre_count / (len(movie.get_genres()) + len(candidate.get_genres())) / 2
    rating_score = candidate.get_average_rating() / 5

    similarity_weight = 0.7
    rating_score_weight = 0.3

    return genre_similarity * similarity_weight + rating_score * rating_score_weight


def calculate_emb_similar_score(movie, candidate):
    if movie is None or candidate is None:
        return -1
    return movie.emb.calculate_similarity(candidate.emb)
