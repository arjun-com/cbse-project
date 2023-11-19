def get_user_details(conn, user):
    assert conn.is_connected(), "Connection to database has not been established."

    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = %s AND password = %s AND school = %s;", (user.username, user.password, user.school))
    valid_users = cursor.fetchall()
    if(len(valid_users) > 0):
        return valid_users[0]
    else:
        return None


