import os
from functools import wraps

from flask import Flask, render_template, request, redirect
from pymongo.mongo_client import MongoClient

import account_util
import util

uri = "mongodb+srv://tomclient:sXGqdZcGnP8wRcGP@cluster0.7kb54la.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["tomclient"]

os.system("npx tailwindcss -i static/css/input.css -o static/css/style.css --minify")
app = Flask(__name__)


def login_required(f):
    @wraps(f)
    def wrap():
        cookie = request.cookies.get("session")
        if not cookie:
            return redirect(f"/signin?next={request.url.split(request.root_url)[1]}")
        user = db.website.find_one({"tokens": {"$in": [cookie]}})
        if not user:
            return redirect(f"/signin?next={request.url.split(request.root_url)[1]}")
        return f(user)
    return wrap


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/account')
@login_required
def account(user):
    if len(request.url.split("?code=")) > 1:
        code = request.url.split("?code=")[1]
        if account_util.link_discord(db, code):
            discord_profile = account_util.get_discord_profile(db)
            print(discord_profile)
            return render_template("account.html", username=user["email"].split("@")[0], isDiscordLinked="true",
                                   discordProfilePicture=discord_profile[1],
                                   discordUsername=discord_profile[0])
    return render_template("account.html", username=user["email"].split("@")[0], texttt="NIG")


@app.route('/signout')
def signout():
    return account_util.signout(db)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    if request.method == "POST":
        return account_util.signup(db)


@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("signin.html")
    if request.method == "POST":
        return account_util.signin(db)


app.run(host="0.0.0.0", port=5439)
