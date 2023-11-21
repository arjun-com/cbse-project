def get_user(conn, user_details):
    assert conn.is_connected(), "Connection to database has not been established."

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s;", (user_details["email"], user_details["password"]))
    valid_users = cursor.fetchall()

    return valid_users[0] if valid_users != [] else None

