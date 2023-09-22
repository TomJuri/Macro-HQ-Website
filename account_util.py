from flask import request, jsonify, make_response, redirect
from passlib.hash import pbkdf2_sha256

from util import is_pass_secure, generate_session_token, exchange, fetch_identity, get_access_token


def account_exists(email, db):
    return db.website.find_one({"email": email})


def get_account(db):
    cookie = request.cookies.get("session")
    if not cookie:
        return False
    return db.website.find_one({"tokens": {"$in": [cookie]}})


def signin(db):
    if get_account(db):
        return redirect("/")
    email = request.form.get("email")
    password = request.form.get("password")
    user = account_exists(email, db)
    if not user or not pbkdf2_sha256.verify(password, user["password"]):
        return jsonify({"error": "Invalid credentials"}), 401
    token = generate_session_token(db)
    user["tokens"] = user["tokens"] + [token]
    db.website.update_one({"email": email}, {"$set": user})
    resp = make_response()
    resp.set_cookie("session", token, 2628288, "Fri, 31 Dec 9999 23:59:59 GMT", samesite="Lax")
    return resp


def signup(db):
    email = request.form.get("email")
    password = request.form.get("password")
    if account_exists(email, db):
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


def signout(db):
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


def link_discord(db, code):
    user = get_account(db)
    exchanged = exchange(code)
    if "refresh_token" in exchanged:
        refresh_token = exchanged["refresh_token"]
        access_token = exchanged["access_token"]
        user_data = fetch_identity(access_token)
        user["discord_id"] = user_data["id"]
        user["discord_refresh_token"] = refresh_token
        db.website.update_one({"email": user["email"]}, {"$set": user})
        return True
    return False


def get_discord_profile(db):
    user = get_account(db)
    if user["discord_refresh_token"] == "":
        return None
    access_token = get_access_token(user["discord_refresh_token"])
    if "access_token" not in access_token:
        return None
    user_data = fetch_identity(access_token["access_token"])
    return user_data["username"], f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}"
