"""
Insta485 Login view.

URLs include:
/accounts/login/
"""

import flask
import insta485
from flask import session, redirect,request, abort
from insta485.views.password import hash_password

@insta485.app.route('/accounts/login/', methods=['POST', 'GET'])
def login():
    if 'username' in session:
        return redirect('/')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not user_exists(username):
            abort(403)
        if not check_credentials(username, password):
            abort(403)
        session['username'] = username
        return redirect('/')
    return flask.render_template("login.html")




def user_exists(username):
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT COUNT(*) FROM users
        WHERE username = ?
    """, [username]
    )
    num_as_string = cur.fetchall()
    return int(num_as_string[0]['COUNT(*)']) == 1

def check_credentials(username, password):
    connection = insta485.model.get_db()
    hashed_password = hash_password(password)
    cur = connection.execute(
    """
    SELECT password FROM users
    WHERE username = ? AND password = ?
    """,(username, hashed_password)
    )
    check = cur.fetchall()
    return check != None
