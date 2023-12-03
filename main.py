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

def validate_and_get_uuid_jwt_token(token):
    try:
        data = jwt.decode(token, jwt_secret_key, algorithms = ["HS256"])
        uuid = data["uuid"]
    except:
        return None

    return uuid

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api_get_assignments")
def get_assignments():
    jwt_token = request.args.get("token")
    if jwt_token == None:
        return "No token in url."

    uuid = validate_and_get_uuid_jwt_token(jwt_token)
    if uuid == None:
        return "Invalid token supplied."
    
    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "Invalid jwt token supplied"

    class_details = {
        "grade": user[3], # 2, 3, 4 are the indices as per the database columns for the assignments table.
        "section": user[4],
        "school": user[2]
    }

    assignments = get_assignments_from_class_details(conn, class_details)
    if assignments == None:
        return "No assignments."

    return render_template("partials/assignments.html", token = jwt_token, len_assignments = len(assignments), assignments = assignments)

@app.get("/api_download_assignment")
def download_assignment():
    # I will not check if the user is logged in or not, because assignments do not really have any harm if it is accessed by someone who is not a user of the site.
    assignment_id = request.args.get("assignment_id")
    if assignment_id == None:
        return "No assignment id supplied."
    
    if not assignment_id.isdigit():
        return "Invalid assignment id supplied."

    try:
        with open(f"{__file__.replace('main.py', '')}static/user_content/assignments/{assignment_id}.pdf", "rb") as file:
            contentBytes = file.read()
            return contentBytes
    except:
        return "Invalid assignment id supplied."

@app.get("/api_user_profile")
def get_user_profile():
    jwt_token = request.args.get("token")
    if jwt_token == None:
        return "No token in url."

    uuid = validate_and_get_uuid_jwt_token(jwt_token)
    if uuid == None:
        return "Invalid token supplied."
    
    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "Invalid jwt token supplied"

    return render_template("profile.html", token = jwt_token, user = user)


@app.post("/api_login")
def login():
    user_data = request.form

    user_login_details = {
        "email": user_data["email"],
        "password": hash_password(user_data["password"])
    }

    user_details = get_user_from_login(conn, user_login_details)
    if user_details == None:
        return "Invalid creds"

    jwt_token = jwt.encode({"uuid": user_details[-1], "exp": datetime.datetime.utcnow() + datetime.timedelta(days = 1)}, jwt_secret_key, algorithm = "HS256")

    user_details = list(user_details)
    user_details.pop(1) # To remove password hash before transferring all other data to client.

    return render_template("dashboard.html", token = jwt_token, user = user_details)
    
app.run(debug = True, host = "0.0.0.0", port = 8080)
