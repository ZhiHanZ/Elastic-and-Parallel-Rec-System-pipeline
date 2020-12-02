import os
from flask import Flask, request, render_template
from service.user_service import *
from service.movie_service import *
from service.recommendation_service import *
from service.rec_for_you_service import *
from service.similiar_movie_service import *
from data_manager.data_manager import DataManager

resource_path = os.path.abspath("../resources/webroot")

DataManager.get_instance().load_data(os.path.join(resource_path, "sampledata/movies.csv"),
                                     os.path.join(resource_path, "sampledata/links.csv"),
                                     os.path.join(resource_path, "sampledata/ratings.csv"),
                                     os.path.join(resource_path, "modeldata/item2vecEmb.csv"),
                                     os.path.join(resource_path, "modeldata/userEmb.csv"),
                                     "i2vEmb", "uEmb")
app = Flask(__name__, static_url_path="")


@app.route("/")
def home_page():
    return app.send_static_file("index.html")


@app.route("/getmovie", methods=["GET"])
def get_movie():
    id = request.args.get("id")
    return MovieService.do_get(int(id))


@app.route("/getuser", methods=["GET"])
def get_user():
    id = request.args.get("id")
    return UserService.do_get(int(id))


@app.route("/getsimilarmovie", methods=["GET"])
def get_similar_movie():
    id = request.args.get("movie_id")
    size = request.args.get("size")
    model = request.args.get("model")
    return SimilarMovieService.do_get(int(id), int(size), model)


@app.route("/getrecommendation", methods=["GET"])
def get_recommendation():
    genre = request.args.get("genre")
    size = request.args.get("size")
    sortby = request.args.get("sortby")
    return RecommendationService.do_get(genre, int(size), sortby)


@app.route("/getrecforyou", methods=["GET"])
def get_rec_for_you():
    id = request.args.get("id")
    size = request.args.get("size")
    model = request.args.get("model")
    return RecForYouService.do_get(int(id), int(size), model)


if __name__ == "__main__":
    app.run()