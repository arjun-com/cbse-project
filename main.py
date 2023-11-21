from flask import Flask, render_template, request
import jwt
import json
import datetime

from db_connection import init_conn
from db_methods import *
from hash_utils import hash_password

conn = init_conn()

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

    user_login_details = {
        "email": user_data["email"],
        "password": hash_password(user_data["password"])
    }

    user_details = get_user(conn, user_login_details)
    if user_details == None:
        return "Invalid creds"

    jwt_token = jwt.encode({"uuid": user_details[-1], "exp": datetime.datetime.utcnow() + datetime.timedelta(days = 1)}, jwt_secret_key, algorithm = "HS256")

    user_details = list(user_details)
    user_details.pop(1) # To remove password hash before transferring all other data to client.

    return render_template("dashboard.html", token = jwt_token, user = user_details)

app.run(debug = True, host = "0.0.0.0", port = 8080)
