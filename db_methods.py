from classes import User

def create_pool_conn_from_conn(conn):
    return conn.get_connection()

def create_cursor_from_pool_conn(pool_conn):
    return pool_conn.cursor(dictionary = True)

def get_user_from_login(conn, user_details):
    pool_conn = create_pool_conn_from_conn(conn)
    cursor = create_cursor_from_pool_conn(pool_conn)

    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (user_details["email"], user_details["password"]))
    user_data = cursor.fetchall()

    cursor.close()
    pool_conn.commit()
    pool_conn.close()

    if user_data:
        user_data = user_data[0]
        user = User(["username"], user_data["password"], user_data["uuid"], user_data["email"], user_data["school"], user_data["grade"], user_data["section"], user_data["dob"], user_data["role"], user_data["teaching_classes"])
        return user

    return None

def get_user_from_uuid(conn, uuid):
    pool_conn = create_pool_conn_from_conn(conn)
    cursor = create_cursor_from_pool_conn(pool_conn)

    cursor.execute("SELECT * FROM users WHERE uuid = %s", [uuid])
    user_data = cursor.fetchall()
    
    cursor.close()
    pool_conn.commit()
    pool_conn.close()

    if user_data:
        user_data = user_data[0]
        user = User(user_data["username"], user_data["password"], user_data["uuid"], user_data["email"], user_data["school"], user_data["grade"], user_data["section"], user_data["dob"], user_data["role"], user_data["teaching_classes"])
        return user

    return None

def get_assignments_from_class_details(conn, class_details):
    grade = class_details["grade"]
    section = class_details["section"]
    school = class_details["school"]
    assert grade, "A grade must be supplied to fetch assignments from the database."
    assert school, "A school name must be supplied to fetch the assignments for students for that school from the database."

    if section == None:
        section = "*"

    pool_conn = create_pool_conn_from_conn(conn)
    cursor = create_cursor_from_pool_conn(pool_conn)

    cursor.execute("SELECT * FROM assignments WHERE grade = %s AND section = %s AND school = %s", (grade, section, school))
    assignments = cursor.fetchall()

    cursor.close()
    pool_conn.commit()
    pool_conn.close()

    return assignments if assignments != [] else None

def get_latest_uaid_for_school(conn, school):
    assert school, "A school must be specified to get an assignment for."

    pool_conn = create_pool_conn_from_conn(conn)
    cursor = create_cursor_from_pool_conn(pool_conn)

    cursor.execute("SELECT uaid FROM assignments WHERE school = %s", [school])
    uaid = cursor.fetchall()

    cursor.close()
    pool_conn.commit()
    pool_conn.close()

    if len(uaid) == 0:
        return 1
    
    return uaid[-1]["uaid"]

def add_assignment(conn, assignment_details):
    assert assignment_details["school"], "A school must be specified to assign an assignment to."
    assert assignment_details["grade"], "A grade must be specified to assign an assignment to."
    assert assignment_details["section"], "A section must be specified to assign an assignment to."

    pool_conn = create_pool_conn_from_conn(conn)
    cursor = create_cursor_from_pool_conn(pool_conn)

    try:
        cursor.execute("INSERT INTO assignments(subject, startdate, enddate, grade, section, school) values(%s, %s, %s, %s, %s, %s)", (assignment_details["subject"], assignment_details["startdate"], assignment_details["enddate"], assignment_details["grade"], assignment_details["section"], assignment_details["school"]))
    except:
        return -1

    cursor.close()
    pool_conn.commit()
    pool_conn.close()

    return 0

def get_tests_from_uuid(conn, uuid):
    assert uuid, "The uuid of the person must be provided."

    user = get_user_from_uuid(conn, uuid)

    pool_conn = create_pool_conn_from_conn(conn)
    cursor = create_cursor_from_pool_conn(pool_conn)

    cursor.execute("SELECT * FROM tests WHERE school = %s AND class = %s", (user.school, f"{user.grade}{user.section}"))
    tests = cursor.fetchall()

    cursor.close()
    pool_conn.commit()
    pool_conn.close()

    if len(tests) == 0:
        return None

    return tests

def get_test_from_utid(conn, utid):
    assert utid, "The utid of the test must be provided."
    pool_conn = create_pool_conn_from_conn(conn)
    cursor = create_cursor_from_pool_conn(pool_conn)

    cursor.execute("SELECT * FROM tests WHERE utid = %s", (utid,))
    test = cursor.fetchall()

    cursor.close()
    pool_conn.commit()
    pool_conn.close()

    if len(test) == 0:
        return None
    
    return test[0]
    
def add_test(conn, metadata, question_data, school, uuid):
    assert school, "A school must be specified to create a test for."
    assert uuid, "The uuid of the person who assigned this test must be provided."
    assert metadata["subject"], "A subject must be specified to create a test for."
    assert metadata["startdatetime"], "A start date and time must be provided to create a test."
    assert metadata["enddatetime"], "An end date and time must be provided to create a test."
    assert metadata["testduration"], "The duration of the test must be set to create a test."
    assert metadata["class"], "The class to which the test will be assigned must be specified."
    assert len(question_data) > 0, "The test must have atleast one question."

    startdate, starttime = metadata["startdatetime"].split("T")
    enddate, endtime = metadata["enddatetime"].split("T")
    # Add date and time validation

    pool_conn = create_pool_conn_from_conn(conn)
    cursor = create_cursor_from_pool_conn(pool_conn)

    try:
        cursor.execute("INSERT INTO tests(subject, school, startdate, starttime, enddate, endtime, testduration, class, assigner_uuid, question_json) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (metadata["subject"], school, startdate, starttime, enddate, endtime, metadata["testduration"], metadata["class"], uuid, str(question_data)))
    except:
        return -1

    cursor.close()
    pool_conn.commit()
    pool_conn.close()

    return 0

def add_test_score(conn, utid, uuid, score):
    assert utid, "The utid of the test must be provided."
    assert uuid, "The uuid of the person must be provided."
    assert score >= 0, "The score of the test must be provided."
    assert type(score) == int, "Score must be provided in int datatype."

    pool_conn = create_pool_conn_from_conn(conn)
    cursor = create_cursor_from_pool_conn(pool_conn)

    try:
        cursor.execute("INSERT INTO test_scores(utid, uuid, score) VALUES(%s, %s, %s)", (utid, uuid, score))
    except:
        return -1
    
    cursor.close()
    pool_conn.commit()
    pool_conn.close()

    return 0

def get_test_score(conn, utid, uuid):
    assert utid, "The utid of the test must be provided."
    assert uuid, "The uuid of the person must be provided."

    pool_conn = create_pool_conn_from_conn(conn)
    cursor = create_cursor_from_pool_conn(pool_conn)

    cursor.execute("SELECT * FROM test_scores WHERE utid = %s, uuid = %s", (utid, uuid))
    score = cursor.fetchall()
    
    cursor.close()
    pool_conn.commit()
    pool_conn.close()

    if len(score) == 0:
        return None

    return score[0]

def get_test_scores_from_uuid(conn, uuid):
    assert uuid, "The uuid of the person must be provided."

    pool_conn = create_pool_conn_from_conn(conn)
    cursor = create_cursor_from_pool_conn(pool_conn)

    cursor.execute("SELECT * FROM test_scores WHERE uuid = %s", (uuid,))
    scores = cursor.fetchall()
    
    cursor.close()
    pool_conn.commit()
    pool_conn.close()

    return scores