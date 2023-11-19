from flask import Flask, render_template, request
import jwt
import json
import datetime

from classes import User
from db_connection import init_conn
from db_methods import *

try:
    jwt_secret_key = json.load(open("./jwt_config.json", "r"))["secret_key"]
except:
    raise Exception("Could not retrieve secret jwt key.\nServer cannot start without token.")
assert jwt_secret_key != "" and jwt_secret_key != None, "secret jwt key must have a valid value."

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api_login")
def login():
    user_data = request.form

    # Implement user validity check here.

    jwt_token = jwt.encode({"username": user_data["user_id"], "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)}, jwt_secret_key, algorithm = "HS256")

    return render_template("dashboard.html", token = jwt_token)

app.run(debug = True, host = "0.0.0.0", port = 8080)
