from flask import Flask, jsonify, render_template, request, abort
from redis import Redis
import requests
import ruamel.yaml as yaml

app = Flask(__name__)
redis = Redis()

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


with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)
    DATA = CONFIG["data"]

if not CONFIG or not DATA:
    exit("Missing configuration file or it is invalid!")

@app.route("/<course>", methods=["GET", "POST"])
def index(course):
    if not course in DATA:
        abort(404)

    course = DATA[course]

    ratelimit_key = str(request.remote_addr)
    if not ratelimit_key in limits:
        limits[ratelimit_key] = Limiter(course["limits"]["req"], course["limits"]["time"])
    ratelimit = limits[ratelimit_key]

    if request.method == "GET":
        return render_template("course.j2", title=course["title"],
                tasks=course["tasks"], captcha_key=CONFIG["captcha"]["key"], limits=limits[ratelimit_key])

    else:
        data = request.form.to_dict()
        res = {}

        # captcha
        url = "https://www.google.com/recaptcha/api/siteverify"
        response = data["g-recaptcha-response"]

        r = requests.post(url, data={"secret": CONFIG["captcha"]["secret"],
                 "response": response}).json()
        if r["success"] and ratelimit.request_available():
            res["fields"] = {}

            wrong = False
            for key, val in course["tasks"].items():
                if key in data and data[key] and int(data[key]) == val["val"]:
                    res["fields"][key] = "ok"
                else:
                    res["fields"][key] = "wrong"
                    wrong = True

            if not wrong:
                res["coordinates"] = course["coordinates"]
            else:
                # don't count correct answers to rate limit
                ratelimit.add()

        res["captcha_success"] = r["success"]
        res["available_requests"] = ratelimit.available_requests()

        return jsonify(res)
