from flask import Flask, render_template, request, session, redirect
from flask_session import Session
from db_config import db_cursor, mydb, Error

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def insert_user(username):
    try:
        db_cursor.execute("INSERT INTO `chat_users`(`username`) VALUES (%s)", (username,))
        mydb.commit()
    except Error as err:
        return "[ERROR] ", err, "occured while inserting new anonymous/guest user into database."
    
def find_user(username):
    db_cursor.execute("SELECT user_id, uuid, username, active FROM `chat_users` WHERE username=%s", (username,))
    user = db_cursor.fetchone()

    return user

def mark_user_active(username, active=True):
    active_value = bool(active)
    
    try:
        db_cursor.execute(f"UPDATE `chat_users` SET `active`={active_value} WHERE  `username`='{username}'")
        mydb.commit()

        return db_cursor.rowcount != 0
    except Error as err:
        return "[ERROR] ", err, "occured while inserting new anonymous/guest user into database." 


@app.route("/")
def index():
    logged_in = False

    try:
        logged_in = bool(session['logged_in'])
    except:
        logged_in = False
    
    if logged_in:
        usernames = []
    
        db_cursor.execute("SELECT name FROM chat_users")

        users = db_cursor.fetchall()

        for username in users:
            usernames.append(username[0])

        return render_template("index.html", usernames=usernames)
    else:
        return redirect("/login")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login_action", methods=['POST', 'GET'])
def login_action():
    if request.method == "POST":
        username = request.form.get('username')

        found_user_by_form_value = bool(find_user(username))
        if not found_user_by_form_value:
            insert_user(username)

        # Creating sessions
        session['logged_in'] = True
        session['username'] = username
        
        username_from_session = session['username']
        user_by_session_value = find_user(username_from_session)[2]

        found_user_by_session_value = bool(user_by_session_value)
        if found_user_by_session_value:
            mark_user_active(username_from_session, True)
            return redirect("/")

@app.route("/logout")
def logout():
    username_from_session = session['username']

    # Updating user information as inactive to the database
    mark_user_active(username_from_session, False)

    # Reset session values
    session['logged_in'] = False
    session['username'] = None
    
    return redirect('/login')

# @app.route("/<route_username>")
# def userchat(route_username):
#     usernames = []
    
#     db_cursor.execute("SELECT name FROM chat_users")

#     users = db_cursor.fetchall()

#     for username in users:
#         usernames.append(username[0])
        
#     return render_template("index.html", usernames=usernames, current_username=route_username)


if __name__ == "__main__":
    app.run(debug=True)
