from classes import User

def create_cursor_from_conn(conn):
    return conn.cursor(dictionary = True)

def get_user_from_login(conn, user_details):
    assert conn.is_connected(), "Connection to database has not been established."

    cursor = create_cursor_from_conn(conn)
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s;", (user_details["email"], user_details["password"]))
    user_data = cursor.fetchall()[0]

    user = User(["username"], user_data["password"], user_data["uuid"], user_data["email"], user_data["school"], user_data["grade"], user_data["section"], user_data["dob"], user_data["role"], user_data["teaching_classes"])

    return user if user_data != None else None

def get_user_from_uuid(conn, uuid):
    assert conn.is_connected(), "Connection to database has not been established."

    cursor = create_cursor_from_conn(conn)
    cursor.execute("SELECT * FROM users WHERE uuid = %s;", [uuid])
    user_data = (cursor.fetchall())[0]
    
    user = User(user_data["username"], user_data["password"], user_data["uuid"], user_data["email"], user_data["school"], user_data["grade"], user_data["section"], user_data["dob"], user_data["role"], user_data["teaching_classes"])

    return user if user_data != None else None

def get_assignments_from_class_details(conn, class_details):
    assert conn.is_connected(), "Connection to database has not been established."

    grade = class_details["grade"]
    section = class_details["section"]
    school = class_details["school"]
    assert grade, "A grade must be supplied to fetch assignments from the database."
    assert school, "A school name must be supplied to fetch the assignments for students for that school from the database."

    if section == None:
        section = "*"

    cursor = create_cursor_from_conn(conn)
    cursor.execute("SELECT * FROM assignments WHERE grade = %s AND section = %s AND school = %s;", (grade, section, school))
    assignments = cursor.fetchall()

    return assignments if assignments != [] else None

def get_latest_uaid_for_school(conn, school):
    assert conn.is_connected(), "Connection to database has not been established."
    assert school, "A school must be specified to get an assignment for."

    cursor = create_cursor_from_conn(conn)
    cursor.execute("SELECT uaid FROM assignments WHERE school = %s", [school])
    uaid = (cursor.fetchall()[-1])["uaid"]

    return uaid

def add_assignment(conn, assignment_details):
    assert conn.is_connected(), "Connection to database has not been established."
    assert assignment_details["school"], "A school must be specified to assign an assignment to."
    assert assignment_details["grade"], "A grade must be specified to assign an assignment to."
    assert assignment_details["section"], "A section must be specified to assign an assignment to."

    cursor = create_cursor_from_conn(conn)
    try:
        cursor.execute("INSERT INTO assignments(subject, startdate, enddate, grade, section, school) values(%s, %s, %s, %s, %s, %s);", (assignment_details["subject"], assignment_details["startdate"], assignment_details["enddate"], assignment_details["grade"], assignment_details["section"], assignment_details["school"]))
    except:
        return -1

    conn.commit()
    return 0


