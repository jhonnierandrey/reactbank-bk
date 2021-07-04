import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session, jsonify
from functools import wraps

# acting as middleware
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return jsonify(msg="Please login to access your information."), 403
        return f(*args, **kwargs)
    return decorated_function

# return any value as usd$ format
def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
