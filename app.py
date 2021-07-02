import os
from threading import current_thread

# from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, sessions, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///finance.db")

# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


@app.route("/")
def index():
    """Show portfolio of stocks"""
    return render_template('index.html', title='ReactBank API')

@app.route("/help")
def help():
    """Show portfolio of stocks"""
    return render_template('help.html', title='ReactBank API > Help')

@app.route("/api")
def api_check():
    """Show portfolio of stocks"""
    return jsonify(status=200, msg='All systems are operational.')
    


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template(name = e.name, code = e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)