import random
import re
import string
import requests
from flask import request


def generate_session_token(db):
    token = ''.join(random.choice(string.ascii_letters + string.punctuation) for _ in range(512))
    while db.website.find_one({"token": token}):
        token = ''.join(random.choice(string.ascii_letters + string.punctuation) for _ in range(512))
    return token


def is_pass_secure(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\\-]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True


def exchange(code):
    response = requests.post("https://discord.com/api/v10/oauth2/token", data={
        "grant_type": "authorization_code", "code": code,
        "client_id": 1147160689878777989, "client_secret": "2aN7ZJOFbo4_qZ9BENxxRIPRlPt8dbOK",
        "redirect_uri": f"{request.root_url}account"})
    return response.json()


def get_access_token(refresh_token):
    response = requests.post("https://discord.com/api/v10/oauth2/token", data={
        "grant_type": "refresh_token", "refresh_token": refresh_token,
        "client_id": 1147160689878777989, "client_secret": "2aN7ZJOFbo4_qZ9BENxxRIPRlPt8dbOK"})
    return response.json()


def fetch_identity(access_token):
    response = requests.get("https://discord.com/api/v10/users/@me",
                            headers={"Authorization": f"Bearer {access_token}"})
    return response.json()
