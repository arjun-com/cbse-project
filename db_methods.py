def get_user_from_login(conn, user_details):
    assert conn.is_connected(), "Connection to database has not been established."

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s;", (user_details["email"], user_details["password"]))
    valid_users = cursor.fetchall()

    return valid_users[0] if valid_users != [] else None

def get_user_from_uuid(conn, uuid):
    assert conn.is_connected(), "Connection to database has not been established."

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE uuid = %s;", [uuid])
    user_data = cursor.fetchall()

    return user_data[0] if user_data != [] else None

def get_assignments_from_class_details(conn, class_details):
    assert conn.is_connected(), "Connection to database has not been established."

    grade = class_details["grade"]
    section = class_details["section"]
    school = class_details["school"]
    assert grade, "A grade must be supplied to fetch assignments from the database."
    assert school, "A school name must be supplied to fetch the assignments for students for that school from the database."

    if section == None:
        section = "*"

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assignments WHERE grade = %s AND section = %s AND school = %s;", (grade, section, school))
    assignments = cursor.fetchall()

    return assignments if assignments != [] else None
