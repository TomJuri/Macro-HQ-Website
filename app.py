import os
from functools import wraps

from flask import Flask, render_template, request, jsonify, make_response, redirect
from passlib.hash import pbkdf2_sha256
from pymongo.mongo_client import MongoClient

import util
from util import is_pass_secure, generate_session_token

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
        exchanged = util.exchange(code)
        if exchanged["refresh_token"] is not None:
            refresh_token = exchanged["refresh_token"]
            user["discord_refresh_token"] = refresh_token
            db.website.update_one({"email": user["email"]}, {"$set": user})
        return render_template("account.html", username=user["email"].split("@")[0], texttt=util.fetch_identity(util.exchange(request.url.split("?code=")[1])["access_token"]))
    return render_template("account.html", username=user["email"].split("@")[0], texttt="NIG")


@app.route('/signout')
def signout():
    cookie = request.cookies.get("session")
    if not cookie:
        return redirect("/")
    user = db.website.find_one({"tokens": {"$in": [cookie]}})
    if not user:
        return redirect("/")
    user["tokens"].remove(cookie)
    db.website.update_one({"email": user["email"]}, {"$set": user})
    resp = redirect("/")
    resp.set_cookie("session", "", 0, "Fri, 31 Dec 9999 23:59:59 GMT", samesite="Lax")
    return resp


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if db.website.find_one({"email": email}):
            return jsonify({"error": "Email already in use"}), 400
        if not is_pass_secure(password):
            return jsonify({"error": "Your password must be at least 8 characters, contain a number, "
                                     "special character and an upper- and lowercase letter"}), 400
        token = generate_session_token(db)
        user = {
            "email": email,
            "password": pbkdf2_sha256.encrypt(password),
            "tokens": [token],
            "macros": [],
            "hwid": "",
            "discord_id": "",
            "discord_refresh_token": ""
        }
        db.website.insert_one(user)
        resp = make_response()
        resp.set_cookie("session", token, 2628288, "Fri, 31 Dec 9999 23:59:59 GMT", samesite="Lax")
        return resp, 200


@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("signin.html")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = db.website.find_one({"email": email})
        if not user or not pbkdf2_sha256.verify(password, user["password"]):
            return jsonify({"error": "Invalid credentials"}), 401
        token = generate_session_token(db)
        user["tokens"] = user["tokens"] + [token]
        db.website.update_one({"email": email}, {"$set": user})
        resp = make_response()
        resp.set_cookie("session", token, 2628288, "Fri, 31 Dec 9999 23:59:59 GMT", samesite="Lax")
        return resp


app.run(host="0.0.0.0", port=5439)
