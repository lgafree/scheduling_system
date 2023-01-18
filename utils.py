from flask import redirect, url_for, flash, session
from functools import wraps


# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("You are not authorized!", "danger")
            return redirect(url_for("index"))

    return decorated_function


# Check if the user is an admin
def check_is_admin(user_id, mysql):
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM admin WHERE user_id = %s"
    result_set = cursor.execute(query, (user_id,))
    cursor.close()
    return True if result_set else False


# Check if the user is a client
def check_is_client(user_id, mysql):
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM client WHERE user_id = %s"
    result_set = cursor.execute(query, (user_id,))
    cursor.close()
    return True if result_set else False
