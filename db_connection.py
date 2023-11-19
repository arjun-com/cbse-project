from mysql.connector import Error, errorcode, connection
import json

def init_conn():
    try:
        db_config_file = open("./db_config.json")
    except:
        raise Exception("Database configuration file was not found.\nMake sure to place 'db_config.json' in the same directory as main.py.")

    try:
        db_config = json.load(db_config_file)
    except:
        raise Exception("Invalid formatting of db_config.js file.")

    try:
        conn = connection.MySQLConnection(
            user = db_config["username"],
            password = db_config["password"],
            database = db_config["database"],
            host = db_config["host"]
        )
    except Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise Exception("Invalid credentials supplied in database configuration file.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise Exception("The database supplied in the database configuration file does not exist.")
        raise Exception("An error occured while trying to establish a connection with the mysql database.\nPlease check the values provided in the database configuration file.")
    
    return conn

