from flask import Flask, render_template, request
import jwt
import json
import datetime
import os
from db_connection import init_conn
from db_methods import *
from hash_utils import hash_password

ASSIGNMENTS_DIR = "./static/user_content/assignments/"
ALLOWED_ASSIGNMENTS_EXTENSIONS = ["pdf"]

conn = init_conn()

try:
    jwt_secret_key = json.load(open("./jwt_config.json", "r"))["secret_key"]
except:
    raise Exception("Could not retrieve secret jwt key.\nServer cannot start without token.")
assert jwt_secret_key != "" and jwt_secret_key != None, "secret jwt key must have a valid value."

app = Flask(__name__)



def class_to_grade_and_section(class_):
    # Named as class_ as class is a reserved keyword.
    if len(class_) == 2:
        return (class_[ : 1], class_[1 : ])
    if len(class_) == 3:
        return (class_[ : 2], class_[2 :])
    return (None, None)

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
        "grade": user["grade"], # 2, 3, 4 are the indices as per the database columns for the assignments table.
        "section": user["section"],
        "school": user["school"]
    }

    assignments = get_assignments_from_class_details(conn, class_details)
    if assignments == None:
        return "No assignments."

    return render_template("partials/student_assignments.html", token = jwt_token, len_assignments = len(assignments), assignments = assignments)

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

    jwt_token = jwt.encode({"uuid": user_details["uuid"], "exp": datetime.datetime.utcnow() + datetime.timedelta(days = 1)}, jwt_secret_key, algorithm = "HS256")

    if user_details["role"] == "student":
        return render_template("student_dashboard.html", token = jwt_token, user = user_details)

    elif user_details["role"] == "teacher":    
        teaching_classes = user_details["teaching_classes"]
        if teaching_classes != None:
            teaching_classes =  [ _.strip() for _ in user_details["teaching_classes"].split(",") ]
        return render_template("teacher_dashboard.html", token = jwt_token, user = user_details, teaching_classes = teaching_classes)

    else:
        return "A dashboard for this user role has not been created yet."
    
@app.post("/api_upload_assignment")
def upload_assignment():
    jwt_token = request.args.get("token")
    if jwt_token == None:
        return "No token in url."

    uuid = validate_and_get_uuid_jwt_token(jwt_token)
    if uuid == None:
        return "Invalid token supplied."
    
    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "Invalid jwt token supplied"

    if request.form["class"] not in user["teaching_classes"]:
        return "You cannot publish an assignment to that class."

    file = request.files["file"]
    if file.filename == "":
        return "No file selected. Refresh the page."

    if not("." in file.filename and file.filename.rsplit(".")[1].lower() in ALLOWED_ASSIGNMENTS_EXTENSIONS):
        return "File has an invalid extension, upload only pdf files. Refresh the page."

    if request.form["class"] == "":
        return "Choose a class to assign the assignment to. Refresh the page."

    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "This user does not exist."

    school = user["school"]
    grade, section = class_to_grade_and_section(request.form["class"])
    if grade == None or section == None:
        return "Invalid class selected. Refresh the page"

    assignment_details = {
        "school": school,
        "grade": grade,
        "section": section,
        "startdate": request.form["startdate"],
        "enddate": request.form["enddate"],
        "subject": request.form["subject"]
    }

    uaid = get_latest_uaid_for_school(conn, school) + 1
    try:
        file.save(os.path.join(ASSIGNMENTS_DIR, f"{uaid}.pdf"))
    except:
        return("An error occurred while storing the file. Refresh the page.")

    db_resp_code = add_assignment(conn, assignment_details)
    if db_resp_code == 0:
        return "Successfully published assignment. Refresh the page."
    else:
        return "An error occurred while publishing the assignment. Refresh the page."
        
app.run(debug = True, host = "0.0.0.0", port = 8080)
