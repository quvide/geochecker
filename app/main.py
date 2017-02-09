from flask import Flask, jsonify, render_template, request
import requests
import ruamel.yaml as yaml

app = Flask(__name__)

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)
    DATA = CONFIG["data"]

if not CONFIG or not DATA:
    exit("Missing configuration file or it is invalid!")

@app.route("/<course>", methods=["GET", "POST"])
def index(course):
    course = DATA[course]

    if request.method == "GET":
        return render_template("course.j2", title=course["title"], tasks=course["tasks"], captcha_key=CONFIG["captcha"]["key"])

    else:
        data = request.form.to_dict()
        res = dict()

        # captcha
        url = "https://www.google.com/recaptcha/api/siteverify"
        response = data["g-recaptcha-response"]

        r = requests.post(url, data={"secret": CONFIG["captcha"]["secret"], "response": response}).json()
        print(r)
        if r["success"]:
            res = {"fields": {}, "captcha_success": True}

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
            res = {"captcha_success": False}

        return jsonify(res)
