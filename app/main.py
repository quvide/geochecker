from flask import Flask, jsonify, render_template, request, abort, Blueprint, g
from redis import StrictRedis as Redis
import requests
import ruamel.yaml as yaml
from collections import deque

from redislimiter import RedisLimiter

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)
    DATA = CONFIG["data"]

    if not CONFIG or not DATA:
        exit("Missing configuration file or it is invalid!")

redis = Redis(CONFIG["redis_host"], decode_responses=True)

def get_ratelimit():
    key = "{}/rate-limit/{}".format(request.environ["REMOTE_ADDR"], g.course)
    max_requests = g.coursedata["limits"]["req"]
    time = g.coursedata["limits"]["time"]
    return RedisLimiter(redis, max_requests, time, key)

def get_stats():
    solved = redis.get("{}/solved".format(g.course))
    failed = redis.get("{}/failed".format(g.course))

    if not solved:
        solved = 0
    if not failed:
        failed = 0

    return {
        "solved": int(solved),
        "failed": int(failed)
    }


app = Flask(__name__)
course = Blueprint("course", __name__, url_prefix="/<course>")

@course.url_value_preprocessor
def pull_course(endpoint, values):
    course = values.pop("course")
    if course in DATA:
        g.coursedata = DATA[course]
        g.course = course
    else:
        abort(404)

@course.route("/")
def index():
    return render_template("course.j2", title=g.coursedata["title"],
                tasks=g.coursedata["tasks"], captcha_key=CONFIG["captcha"]["key"])


@course.route("/check", methods=["POST"])
def check():
    data = request.form.to_dict()
    ratelimit = get_ratelimit()
    res = {}

    # captcha
    url = "https://www.google.com/recaptcha/api/siteverify"
    response = data["g-recaptcha-response"]

    r = requests.post(url, data={"secret": CONFIG["captcha"]["secret"],
             "response": response}).json()
    if r["success"] and ratelimit.request_available():
        res["fields"] = {}

        wrong = False
        for key, val in g.coursedata["tasks"].items():
            if key in data and data[key] and int(data[key]) == val["val"]:
                res["fields"][key] = "ok"
            else:
                res["fields"][key] = "wrong"
                wrong = True

        if not wrong:
            redis.incr("{}/solved".format(g.course))
            res["coordinates"] = g.coursedata["coordinates"]
        else:
            redis.incr("{}/failed".format(g.course))
            # don't count correct answers to rate limit
            ratelimit.add()

    res["captcha_success"] = r["success"]

    return jsonify(res)

@course.route("/rate", methods=["POST"])
def rate():
    ratelimit = get_ratelimit()
    stats = get_stats()

    res = {
        "available_requests": ratelimit.available_requests(),
        "max_requests": ratelimit.max_requests,
        "time": ratelimit.time,
        "next_available_request": int(ratelimit.next_available_request()),
        "correct_counter": stats["solved"],
        "incorrect_counter": stats["failed"]
    }

    return jsonify(res)

app.register_blueprint(course)
