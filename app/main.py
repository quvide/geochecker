from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

DATA = {
    "test": {
        "title": "GC12345",
        "tasks": {
            "1a": {"val": 1, "unit": "kertaa"},
            "1b": {"val": 2, "unit": "%"},
            "2": {"val": 3}
        },
        "coordinates": "N61°09'47.7\" E24°05'39.1\""
    }
}

@app.route("/<course>", methods=["GET", "POST"])
def index(course):
    course = DATA[course]

    if request.method == "GET":
        return render_template("course.j2", title=course["title"], tasks=course["tasks"])

    else:
        data = request.form.to_dict()
        res = {"fields": {}}

        wrong = False

        for key, val in course["tasks"].items():
            if key in data and data[key] and int(data[key]) == val["val"]:
                res["fields"][key] = "ok"
            else:
                res["fields"][key] = "wrong"
                wrong = True

        if not wrong:
            res["coordinates"] = course["coordinates"]

        return jsonify(res)
