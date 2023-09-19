import os

from flask import Flask, render_template

os.system("npx tailwindcss -i static/css/input.css -o static/css/style.css --minify")

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/signin')
def signin():
    return render_template("signin.html")


app.run(host="0.0.0.0", port=5439)
