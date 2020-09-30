"""
Insta485 Login view.

URLs include:
/accounts/login/
"""

import flask
from flask import session, redirect, request, abort, url_for
import insta485
from insta485.views.password import hash_password, check_password


@insta485.app.route('/accounts/login/', methods=['POST', 'GET'])
def login():
    """Login flask function."""
    if 'username' in session:
        return redirect(url_for('show_index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not user_exists(username):
            abort(403)
        # if not check_credentials(username, password):
        if not check_credentials_pass(username, password):
            abort(403)
        session['username'] = username
        return redirect(url_for('show_index'))
    return flask.render_template("login.html")


def user_exists(username):
    """Check user exists."""
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT COUNT(*) FROM users
        WHERE username = ?
    """, [username]
    )
    num_as_string = cur.fetchall()
    return int(num_as_string[0]['COUNT(*)']) == 1


def check_credentials(username, password):
    """Check credentials."""
    connection = insta485.model.get_db()
    hashed_password = hash_password(password)
    cur = connection.execute(
        """
    SELECT password FROM users
    WHERE username = ? AND password = ?
    """, (username, hashed_password)
    )
    check = cur.fetchall()
    return check is not None


def check_credentials_pass(username, input_pass):
    """Verify the login information."""
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT password FROM users
        WHERE username = ?
    """, [username]
    )
    db_password = cur.fetchall()[0]['password']

    return check_password(db_password, input_pass)
