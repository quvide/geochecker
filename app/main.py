from flask import Flask, jsonify, render_template

app = Flask(__name__)

DATA = {
    "1": {
        "title": "GC12345",
        "tasks": {
            "1a": 1,
            "1b": 2
        }
    }
}

@app.route("/<course>")
def index(course):
    course = DATA[course]
    print(course)
    return render_template("course.j2", title=course["title"], tasks=course["tasks"].keys())

@app.route("/<course>/<task>")
def task(course, task):
    return "TODO"

if __name__ == "__main__":
    app.run()
