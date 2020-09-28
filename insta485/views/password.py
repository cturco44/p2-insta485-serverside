"""
Insta485 password view.

URLs include:
/accounts/password/
"""
import hashlib
import uuid
import flask
from flask import request, abort, redirect, url_for
from insta485.views.edit import show_edit
import insta485


@insta485.app.route('/accounts/password/', methods=['POST', 'GET'])
def show_password():
    """For /accounts/password/ page."""
    # Connect to database
    connection = insta485.model.get_db()

    # TODO: initialize to blank and delete password processing
    logname = "michjc"
    flask.session['username'] = 'michjc'

    cur = connection.execute("""
        SELECT password FROM users
        WHERE username = ?
    """, [logname]
    )
    user_obj = cur.fetchall()
    logname_password = user_obj[0]['password']


    if "username" in flask.session:
        logname = flask.session["username"]

        cur = connection.execute("""
            SELECT password FROM users
            WHERE username = ?
        """, [logname]
        )
        user_obj = cur.fetchall()
        logname_password = user_obj[0]['password']
    else:
        return redirect("/accounts/login") # TODO: use url_for

    if request.method == "POST":
        if 'new_password1' in request.form:
            inputted_password = request.form['password']
            correct_password = check_password(logname_password,
                                              inputted_password)

            if not correct_password:
                abort(403)

            if request.form['new_password1'] != request.form['new_password2']:
                abort(401)

            new_password = hash_password(request.form['new_password1'])

            # update hashed password entry in database
            connection.execute("""
                UPDATE users
                SET password = ?
                WHERE username = ?
            """, [new_password, logname]
            )

            #return redirect("/accounts/edit/")
            return redirect(url_for('show_edit'))
    return flask.render_template("password.html", logname=logname)


def hash_password(password):
    """To hash a password (sha512) then add a salt."""
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string


def check_password(password, input_pass):
    """Check inputted password matches password in the database."""
    # password - password HASH in database
    # input_pass - what the user entered as the password
    shortened_pass = password[7:]
    salt = ""

    for char in shortened_pass:
        if char == '$':
            break
        salt += char

    # hashing inputted password
    algorithm = 'sha512'
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + input_pass
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    return password_db_string == password
