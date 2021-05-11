import sqlite3

CREATE_USERS_TABLE = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, fname TEXT, lname TEXT, uname TEXT, pwd TEXT);"
INSERT_USER = "INSERT INTO users (fname, lname, uname, pwd) VALUES (?, ?, ?, ?);"
UNIQUE_CHECK = "SELECT uname FROM users WHERE uname = ?"
LOGIN = "SELECT uname FROM users WHERE uname = ? AND pwd = ?"
CREATE_FRIEND_REQUEST_TABLE = "CREATE TABLE IF NOT EXISTS friends_request(user_id int, requester_id int);"
CREATE_FRIEND_TABLE = "CREATE TABLE IF NOT EXISTS friends(user_id int, friend_id int);"
def connect():
    return sqlite3.connect("users.db")

def create_tables(connection):
    with connection:
        c = connection.cursor()
        c.execute(CREATE_USERS_TABLE)
        c.execute(CREATE_FRIEND_REQUEST_TABLE)
        c.execute(CREATE_FRIEND_TABLE)
        

def add_user(connection, fname, lname, uname, pwd):
    with connection:
        c = connection.cursor()
        
        #print(uname)
        verified = c.execute(UNIQUE_CHECK, (uname,)).fetchall()
        if len(verified) == 0:
            c.execute(INSERT_USER, (fname, lname, uname, pwd,))
            return True
        else:
            return False
    
def verify_user(connection, uname, pwd):
    with connection:
        c = connection.cursor()
        #print(c.execute("SELECT * FROM users").fetchall())
        vname = c.execute(LOGIN, (uname, pwd)).fetchall()
        if len(vname) == 0:
            return False
        else:
            return True
            
