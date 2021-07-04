import os
from sqlite3.dbapi2 import connect
from threading import current_thread

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session, sessions, jsonify
from flask_session import Session
from flask_cors import CORS, cross_origin
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, lookup, usd

# Configure application
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    response.headers['Access-Control-Allow-Credentials'] = True
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configuring the SQLite database
def sql_connection():
    try:
        con = sqlite3.connect('reactbank.db',  check_same_thread=False)
        con.row_factory = sqlite3.Row
        return con
    except sqlite3.Error:
        print(sqlite3.Error)

def sql_table(con):
    temp_db = con.cursor()
    
    temp_db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT NOT NULL, lastName TEXT NOT NULL, email TEXT NOT NULL, password TEXT NOT NULL, balance NUMERIC NOT NULL DEFAULT 1000.00, PRIMARY KEY(id));')
    temp_db.execute('CREATE UNIQUE INDEX IF NOT EXISTS email ON users (email);')
    temp_db.execute('CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, amount NUMERIC NOT NULL, type TEXT NOT NULL, description TEXT NOT NULL, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id));')
    con.commit()

con = sql_connection()
sql_table(con)

db = con.cursor()

# checks if tables exists on current db

# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")

# api index for help / docs
@app.route("/")
def index():
    return render_template('index.html', title='ReactBank API')

@app.route("/help")
def help():
    return render_template('help.html', title='ReactBank API > Help')

# api routes 
@app.route("/api")
def api_check():
    return jsonify(msg='All systems are operational.'), 200

@app.route('/api/register', methods=['POST'])
def register():
    # check for name input
    if not request.form.get('name'):
        return jsonify(msg="Must provide name"), 400
    
    # check for last name input
    if not request.form.get('lastName'):
        return jsonify(msg="Must provide last name"), 400
    
    # check for email input
    if not request.form.get('email'):
        return jsonify(msg="Must provide a valid email"), 403

    # check for password input
    if not request.form.get('password'):
        return jsonify(msg="Must provide password"), 403

    # check for password match
    if request.form.get('password') != request.form.get('confirmation'):
        return jsonify(msg="Passwords do not match"), 403

    # checks if email in the db already exists
    new_user_email = request.form.get('email')
    new_user_password = request.form.get('password')

    rows = db.execute('SELECT * FROM users WHERE email = ?;', [request.form.get('email')]).fetchall()

    if len(rows) != 0:
        return jsonify(msg="User already exists"), 403
    else:
        db.execute('INSERT INTO users(name, lastName, email, password) VALUES ( ?, ?, ?, ?);', (request.form.get('name'), request.form.get('lastName'), new_user_email, generate_password_hash(new_user_password)))
        con.commit()
        return jsonify(msg = 'User created'), 200

@app.route('/api/login', methods=['POST'])
def login():
    # Forget any previous user_id
    session.clear()

    # Ensure email was submitted
    if not request.form.get("email"):
        return jsonify(msg="Must provide email"), 403

    # Ensure password was submitted
    elif not request.form.get("password"):
        return jsonify(msg="Must provide password"), 403

    # Query database for email
    rows = db.execute("SELECT * FROM users WHERE email = ?;", [request.form.get('email')]).fetchall()

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
        return jsonify(msg="User or password incorrect."), 403

    # Remember which user has logged in
    session["user_id"] = rows[0]["id"]

    # response with successfull login
    return jsonify(msg='User Logged In', token=rows[0]["id"]), 200

@app.route('/api/account', methods=['POST'])
@login_required
def account():
    # checks for active sessions
    get_user_data = db.execute('SELECT * FROM users WHERE id = ?', [session["user_id"]]).fetchone()

    user_data = {
        'name' : get_user_data['name'],
        'lastName' : get_user_data['lastName'],
        'email' : get_user_data['email'],
        'balance' : usd(get_user_data['balance'])
    }

    return jsonify(msg='User data', userData = user_data), 200


@app.route("/api/logout", methods=['GET', 'POST'])
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return jsonify(msg="User is now Logged Out")

# creates an error page
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html",name = e.name, code = e.code), e.code

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)