from flask import Flask, jsonify, render_template, request, abort, Blueprint, g
from redis import Redis
import requests
import ruamel.yaml as yaml
import time
from collections import deque

class Limiter:
    def __init__(self, max_requests, time):
        self.max_requests = max_requests
        self.time = time
        self.history = deque()

    def __refresh(self):
        now = time.time()
        while len(self.history) > 0 and self.history[0] < now:
            self.history.popleft()

    def add(self):
        self.history.append(time.time() + self.time)

    def request_available(self):
        self.__refresh()
        return len(self.history) < self.max_requests

    def available_requests(self):
        self.__refresh()
        return self.max_requests - len(self.history)

    def __repr__(self):
        return "max_requests {}, time {}, history {}".format(self.max_requests, self.time, repr(self.history))

limits = {}

def get_ratelimit():
    ratelimit_key = str(request.remote_addr)
    if not ratelimit_key in limits:
        limits[ratelimit_key] = Limiter(g.coursedata["limits"]["req"], g.coursedata["limits"]["time"])
    return limits[ratelimit_key]


app = Flask(__name__)
redis = Redis()
course = Blueprint("course", __name__, url_prefix="/<course>")

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)
    DATA = CONFIG["data"]

if not CONFIG or not DATA:
    exit("Missing configuration file or it is invalid!")

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
            res["coordinates"] = g.coursedata["coordinates"]
        else:
            # don't count correct answers to rate limit
            ratelimit.add()

    res["captcha_success"] = r["success"]

    return jsonify(res)

@course.route("/rate", methods=["POST"])
def rate():
    ratelimit = get_ratelimit()
    res = {
        "available_requests": ratelimit.available_requests(),
        "max_requests": ratelimit.max_requests,
        "time": ratelimit.time
    }

    return jsonify(res)

app.register_blueprint(course)
