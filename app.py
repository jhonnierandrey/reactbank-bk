import os
from sqlite3.dbapi2 import connect
from threading import current_thread

import sqlite3
from flask import Flask, flash, json, redirect, render_template, request, session, sessions, jsonify
from flask_session import Session
from flask_cors import CORS, cross_origin
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, usd

# Configure application
app = Flask(__name__)

CORS(app)
# CORS(app, supports_credentials=True, resources={r"/*"}, origins=["http://localhost:3000"])
app.config['CORS_HEADERS'] = 'Content-Type'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    origins_list = ['http://localhost:3000', 'https://reactbank-front-end.netlify.app']
    if request.headers['Origin'] in origins_list:
        response.headers['Access-Control-Allow-Origin'] = request.headers['Origin'] 
        response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers["Access-Control-Allow-Credentials"] = 'true'
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    # response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    # response.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization"
    # response.headers["Access-Control-Allow-Origin"] = 'http://localhost:3000'
    
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SECURE"] = True
# app.config["SESSION_COOKIE_HTTPONLY"] = False
app.config['SESSION_COOKIE_SAMESITE'] = "None"
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
    
    # checks if tables exists on current db
    temp_db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT NOT NULL, lastName TEXT NOT NULL, email TEXT NOT NULL, password TEXT NOT NULL, balance NUMERIC NOT NULL DEFAULT 1000.00, PRIMARY KEY(id));')
    temp_db.execute('CREATE UNIQUE INDEX IF NOT EXISTS email ON users (email);')
    temp_db.execute('CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, amount NUMERIC NOT NULL, type TEXT NOT NULL, description TEXT NOT NULL, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id));')
    con.commit()

con = sql_connection()
sql_table(con)

db = con.cursor()

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

@app.route('/api/account/transactions', methods=['POST'])
@login_required
def transactions():
    # checks for active sessions
    get_user_transactions = db.execute('SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC', [session["user_id"]]).fetchall()

    user_transactions = []

    for row in get_user_transactions:
        user_transactions.append({
            'id' : row['id'],
            'type' : row['type'],
            'description' : row['description'],
            'amount' : usd(row['amount']),
            'time' : row['time'],
        })

    return jsonify(msg='User transactions', userTransactions = user_transactions), 200

@app.route('/api/account/wdw', methods=['POST'])
@login_required
def withdrawal():
    # checks for active sessions
    get_user_data = db.execute('SELECT * FROM users WHERE id = ?', [session["user_id"]]).fetchone()

    # check user input for withdrawal amount
    if not request.form.get('withdrawal'):
        return jsonify(mgs = 'Missing amount to withdrawal'), 400

    # checks shares = positive int
    elif not request.form.get('withdrawal').isdigit() or int(request.form.get('withdrawal')) < 0:
        return jsonify(mgs = 'Invalid amount to withdrawal'), 400

    if get_user_data['balance'] >= int(request.form.get('withdrawal')):
        # update current user cash
        db.execute('UPDATE users SET balance = ? WHERE id = ?', (get_user_data['balance'] - int(request.form.get('withdrawal')), session["user_id"]))

        # create the new transaction
        db.execute('INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)', (session["user_id"], int(request.form.get('withdrawal')), 'Debit', 'Withdrawal from account'))
        con.commit()

        # get updated user data and return it
        get_user_data = db.execute('SELECT * FROM users WHERE id = ?', [session["user_id"]]).fetchone()
        
        user_data = {
            'name' : get_user_data['name'],
            'lastName' : get_user_data['lastName'],
            'email' : get_user_data['email'],
            'balance' : usd(get_user_data['balance'])
        }

        return jsonify(msg='Withdrawal completed', userData = user_data), 200
    else:
        return jsonify(msg='Not enough money'), 400

@app.route('/api/account/transfer', methods=['POST'])
@login_required
def transfer():
    # checks for active sessions
    get_user_data = db.execute('SELECT * FROM users WHERE id = ?', [session["user_id"]]).fetchone()

    # check user input for email amount
    if not request.form.get('email'):
        return jsonify(mgs = 'Recipient\'s email address is missing.'), 400
    
    # check user input for transfer amount
    elif not request.form.get('transfer'):
        return jsonify(mgs = 'Missing amount to transfer'), 400

    # checks shares = positive int
    elif not request.form.get('transfer').isdigit() or int(request.form.get('transfer')) < 0:
        return jsonify(mgs = 'Invalid amount to transfer'), 400

    if get_user_data['balance'] >= int(request.form.get('transfer')):
        # verify recipient's account exits
        get_user_receptor = db.execute('SELECT * FROM users WHERE email = ?', [request.form.get('email')]).fetchone()

        if get_user_receptor:
            # update current user balance
            db.execute('UPDATE users SET balance = ? WHERE id = ?', (get_user_data['balance'] - int(request.form.get('transfer')), session["user_id"]))

            # create the new transaction for sender
            description_sender = 'Transfer to ' + request.form.get('email')
            db.execute('INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)', (session["user_id"], int(request.form.get('transfer')), 'Debit', description_sender))
            con.commit()
            
            # update receptor user balance
            db.execute('UPDATE users SET balance = ? WHERE id = ?', (get_user_receptor['balance'] + int(request.form.get('transfer')), get_user_receptor['id']))
            
            # create the new transaction for receptor
            description_receptor = 'Transfer from ' + get_user_data['email']
            db.execute('INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)', (get_user_receptor['id'], int(request.form.get('transfer')), 'Credit', description_receptor))
            con.commit()

            # get updated user data and return it
            get_user_data = db.execute('SELECT * FROM users WHERE id = ?', [session["user_id"]]).fetchone()
            
            # send updated user data
            user_data = {
                'name' : get_user_data['name'],
                'lastName' : get_user_data['lastName'],
                'email' : get_user_data['email'],
                'balance' : usd(get_user_data['balance'])
            }
            
            return jsonify(msg='Transfer completed', userData = user_data), 200
        else:
            return jsonify(msg='User does not exist'), 200
    else:
        return jsonify(msg='Not enough money'), 400
    
@app.route('/api/account/deposit', methods=['POST'])
@login_required
def deposit():
    # checks for active sessions
    get_user_data = db.execute('SELECT * FROM users WHERE id = ?', [session["user_id"]]).fetchone()

    # allow user balance to be updated if is below 250
    if get_user_data['balance'] <= 250:
        # update current user cash
        db.execute('UPDATE users SET balance = ? WHERE id = ?', (get_user_data['balance'] + 1000, session["user_id"]))

        # create the new transaction
        db.execute('INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)', (session["user_id"], 1000, 'Credit', 'Deposit to account'))
        con.commit()

        # get updated user data and return it
        get_user_data = db.execute('SELECT * FROM users WHERE id = ?', [session["user_id"]]).fetchone()
        
        user_data = {
            'name' : get_user_data['name'],
            'lastName' : get_user_data['lastName'],
            'email' : get_user_data['email'],
            'balance' : usd(get_user_data['balance'])
        }

        return jsonify(msg='Balance updated', userData = user_data), 200
    else:
        return jsonify(msg='You can reset your balance when is below $250'), 400

@app.route('/api/account/update', methods=['POST'])
@login_required
def update():

    # Ensure password was submitted
    if not request.form.get("password"):
        return jsonify(msg="Must provide current password"), 403

    # Ensure new password was submitted
    elif not request.form.get("passwordNew"):
        return jsonify(msg="Must provide a new password"), 403

    # check for new password match
    elif request.form.get('passwordNew') != request.form.get('confirmation'):
        return jsonify(msg="Passwords do not match"), 403

    # Query database for user data
    get_user_data = db.execute('SELECT * FROM users WHERE id = ?', [session["user_id"]]).fetchone()

    # Ensure username exists and password is correct
    if not check_password_hash(get_user_data["password"], request.form.get("password")):
        return jsonify(msg="Invalid current password"), 403

    # update user password
    db.execute('UPDATE users SET password = ? WHERE id = ?', (generate_password_hash(request.form.get('passwordNew')), session["user_id"]))
    con.commit()

    # send confirmation
    return jsonify(msg='The password has been updated'), 200

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