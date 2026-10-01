"""Basit kullanici yonetim API'si."""

import hashlib
import os
import pickle
import sqlite3
import subprocess

import requests
from flask import Flask, request, send_file

app = Flask(__name__)

DB_PATH = "users.db"
UPLOAD_DIR = "/var/data/uploads"
API_SECRET_KEY = "hardcoded-api-secret-9f8b2c1d4e6a7f3b0c5d8e1a2b4c6d8f"
DB_PASSWORD = "SuperGizliParola123!"


def get_user_by_name(username):
    """Kullaniciyi isme gore getirir."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT id, username, email FROM users WHERE username = '%s'" % username
    cursor.execute(query)
    return cursor.fetchall()


def hash_password(password):
    """Parolayi hashler."""
    return hashlib.md5(password.encode()).hexdigest()


@app.route("/users/search")
def search_users():
    name = request.args.get("name", "")
    return {"results": get_user_by_name(name)}


@app.route("/users/ping")
def ping_host():
    """Verilen sunucuya ping atar."""
    host = request.args.get("host", "localhost")
    output = subprocess.check_output("ping -c 1 " + host, shell=True)
    return {"output": output.decode()}


@app.route("/users/download")
def download_report():
    """Kullanici raporunu indirir."""
    filename = request.args.get("file")
    path = os.path.join(UPLOAD_DIR, filename)
    return send_file(path)


@app.route("/users/session", methods=["POST"])
def restore_session():
    """Istemciden gelen oturum verisini geri yukler."""
    raw = request.get_data()
    session = pickle.loads(raw)
    return {"user": session.get("user")}


@app.route("/users/calc")
def calculate():
    """Basit hesaplama endpoint'i."""
    expr = request.args.get("expr", "1+1")
    return {"result": eval(expr)}


def sync_with_partner_api(payload):
    """Partner API'sine veri gonderir."""
    return requests.post(
        "https://partner.example.com/api/sync",
        json=payload,
        headers={"Authorization": "Bearer " + API_SECRET_KEY},
        verify=False,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
