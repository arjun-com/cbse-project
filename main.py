from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import jwt
import json
import os
import sys
from db_connection import init_conn
from db_methods import *
from hash_utils import hash_password

# from classes import User

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
        return (class_[ : 2], class_[2 : ])
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
        "grade": user.grade,
        "section": user.section,
        "school": user.school
    }
    
    assignments = get_assignments_from_class_details(conn, class_details)
    if assignments == None:
        return "No assignments."

    return render_template("student/assignments.html", user = user, token = jwt_token, len_assignments = len(assignments), assignments = assignments)

@app.get("/api_download_assignment")
def download_assignment():
    # Does not check if the user is logged in or not, because assignments do not really have any harm if it is accessed by someone who is not a user of the site.
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

    try:
        user_login_details = {
            "email": user_data["email"],
            "password": hash_password(user_data["password"])
        }
    except:
        return "Invalid creds"

    user = get_user_from_login(conn, user_login_details)
    if user == None:
        return "Invalid creds"

    jwt_token = jwt.encode({"uuid": user.uuid, "exp": datetime.utcnow() + timedelta(days = 1)}, jwt_secret_key, algorithm = "HS256")

    return redirect("/api_dashboard?token=" + jwt_token, code = 302)

@app.get("/api_dashboard")
def get_dashboard():
    jwt_token = request.args.get("token")
    if jwt_token == None:
        return "No token in url."

    uuid = validate_and_get_uuid_jwt_token(jwt_token)
    if uuid == None:
        return "Invalid token supplied."

    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "Invalid token supplied."

    if user.role == "student":
        return render_template("student/dashboard.html", token = jwt_token, user = user)

    elif user.role == "teacher":
        return render_template("teacher/dashboard.html", token = jwt_token, user = user)

    else:
        return "A dashboard for this user role has not been created yet."

@app.get("/api_create_assignment")
def get_assignment_creator():
    jwt_token = request.args.get("token")
    if jwt_token == None:
        return "No token in url."

    uuid = validate_and_get_uuid_jwt_token(jwt_token)
    if uuid == None:
        return "Invalid token supplied."
    
    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "Invalid token supplied"

    if user.role != "teacher":
        return "You cannot access this feature."
    
    print(user.teaching_classes)

    return render_template("teacher/assignment_creator.html", user = user, token = jwt_token)

@app.post("/api_create_assignment")
def create_assignment():
    jwt_token = request.args.get("token")
    if jwt_token == None:
        return "No token in url."

    uuid = validate_and_get_uuid_jwt_token(jwt_token)
    if uuid == None:
        return "Invalid token supplied."
    
    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "Invalid jwt token supplied"

    if user.teaching_classes != None and request.form["class"] not in user.teaching_classes:
        return "You cannot publish an assignment to that class."

    file = request.files["file"]
    if file.filename == "" or file.filename == None:
        return "No file selected. Refresh the page."

    if not("." in file.filename and file.filename.rsplit(".")[1].lower() in ALLOWED_ASSIGNMENTS_EXTENSIONS):
        return "File has an invalid extension, upload only pdf files. Refresh the page."

    if request.form["class"] == "":
        return "Choose a class to assign the assignment to. Refresh the page."

    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "This user does not exist."

    school = user.school
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

    print(assignment_details)

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

@app.get("/api_create_test")
def get_test_creator():
    jwt_token = request.args.get("token")
    if jwt_token == None:
        return "No token in url."

    uuid = validate_and_get_uuid_jwt_token(jwt_token)
    if uuid == None:
        return "Invalid token supplied."
    
    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "Invalid jwt token supplied."

    if user.role != "teacher":
        return "You cannot access this feature."

    if user.teaching_classes == None:
        return "You do not teach any classes currently you cannot assign any tests."
    
    return render_template("teacher/test_creator.html", user = user, token = jwt_token)

@app.post("/api_create_test")
def create_test():
    jwt_token = request.args.get("token")
    if jwt_token == None:
        return "No token in url.", 400

    uuid = validate_and_get_uuid_jwt_token(jwt_token)
    if uuid == None:
        return "Invalid token supplied.", 400

    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "Invalid jwt token supplied", 400

    try:
        data = request.get_json(force = True)
    except:
        return "Invalid formmating of test data.", 400
    
    # TODO: validate test questions and format.

    data["metadata"]["grade"], data["metadata"]["section"] = class_to_grade_and_section(data["metadata"]["class"])
    del(data["metadata"]["class"])

    startdatetime = datetime.strptime(data["metadata"]["startdatetime"], "%Y-%m-%dT%H:%M")
    startdatetime_sqlf = startdatetime.strftime("%Y-%m-%d %H:%M:%S")
    data["metadata"]["startdatetime"] = startdatetime_sqlf

    enddatetime = datetime.strptime(data["metadata"]["enddatetime"], "%Y-%m-%dT%H:%M")
    enddatetime_sqlf = enddatetime.strftime("%Y-%m-%d %H:%M:%S")
    data["metadata"]["enddatetime"] = enddatetime_sqlf

    resp_code = add_test(conn, data["metadata"], json.dumps(data["questions"]), user.school, uuid)
    if resp_code == 0:
        return "Successfully published test to students."

    return "An error occurred while publishing the test. Try again later.", 503

active_tests = {}

@app.get("/api_take_test")
def take_test():
    jwt_token = request.args.get("token")
    if jwt_token == None:
        return "No token in url.", 400

    uuid = validate_and_get_uuid_jwt_token(jwt_token)
    if uuid == None:
        return "Invalid token supplied.", 400

    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "Invalid jwt token supplied", 400

    tests = get_tests_from_uuid(conn, uuid)
    if tests == None:
        return "No tests to display"
    
    utid = request.args.get("test_id")
    if not utid or not utid.isdigit:
        return "No test was specified."
    
    test = get_test_from_utid(conn, utid)

    if test == None:
        return "You cannot take that test."
    
    datetime_start = test["startdatetime"]
    datetime_end = test["enddatetime"]
    
    if datetime_start > datetime.now() or datetime_end < datetime.now():
        return "This test cannot be taken at the moment."
    
    questions = json.loads(test["question_json"])
    del(test["question_json"])
    # TODO: add check to check if the user has already taken the test.

    active_tests[jwt_token] = {
        "utid": utid,
        "startdatetime": datetime.now(),
        "duration": test["testduration"]
    }
    # TODO: add check for already existing active tests incase a user closed the browser window during a test.

    return render_template("/student/test_taker.html", user = user, token = jwt_token, questions = questions, metadata = test, enumerate = enumerate)

@app.post("/api_submit_test")
def submit_test():
    jwt_token = request.args.get("token")
    if jwt_token == None:
        return "No token in url.", 400

    uuid = validate_and_get_uuid_jwt_token(jwt_token)
    if uuid == None:
        return "Invalid token supplied.", 400

    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "Invalid jwt token supplied", 400
    
    data = request.get_json(force = True)
    # TODO: add validation of answer data.

    try:
        user_test_data = active_tests[jwt_token]
    except:
        return "You cannot access this test.", 400
    
    utid = user_test_data["utid"]
    duration_taken = (datetime.now() - user_test_data["startdatetime"]).total_seconds() / 60
    if duration_taken > user_test_data["duration"]:
        return "You did not submit the test in the stipulated amount of time.", 400
    
    app.logger.info("DURATION TAKEN: ", duration_taken)
    
    test = get_test_from_utid(conn, utid)
    if test == None:
        return "You cannot access this test.", 400
    
    questions = json.loads(test["question_json"])
    correct_answers = [x["correct_option"] for x in questions]

    score = 0

    for answer in data.items():
        if answer[0].isdigit() and type(answer[1]) == int and 0 <= int(answer[0]) < len(correct_answers) and int(answer[1] + 1) == int(correct_answers[int(answer[0])]):
            score += 1

    # TODO: Implement feature to store all answers of user so they can see where they went wrong.
    if add_test_score(conn, utid, uuid, score, len(correct_answers)) != 0:
        return "An error occurred while submitting the test.", 400

    return "Successfully submitted test.", 200
    

@app.get("/api_get_tests")
def get_tests():
    jwt_token = request.args.get("token")
    if jwt_token == None:
        return "No token in url.", 400

    uuid = validate_and_get_uuid_jwt_token(jwt_token)
    if uuid == None:
        return "Invalid token supplied.", 400

    user = get_user_from_uuid(conn, uuid)
    if user == None:
        return "Invalid jwt token supplied", 400

    tests = get_tests_from_uuid(conn, uuid)
    if tests == None:
        return "No tests to display"
    
    taken_tests = get_test_scores_from_uuid(conn, uuid)
    taken_test_utids = []
    taken_test_scores = []
    taken_test_max_scores = []

    for taken_test in taken_tests:
        taken_test_utids.append(taken_test["utid"])
        taken_test_scores.append(taken_test["score"])
        taken_test_max_scores.append(taken_test["max_score"])

    for test in tests:
        if test["utid"] in taken_test_utids:
            test["taken"] = True
            test["score"] = taken_test_scores[taken_test_utids.index(test["utid"])]
            test["max_score"] = taken_test_max_scores[taken_test_utids.index(test["utid"])]
        else:
            test["taken"] = False

    return render_template("student/tests.html", user = user, token = jwt_token, tests = tests, len_tests = len(tests))

app.run(debug = True, host = "localhost", port = 5335, threaded=True)
