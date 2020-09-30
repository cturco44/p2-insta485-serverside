import os
import flask
from flask import request, send_from_directory, redirect, abort
import insta485
import pdb


@insta485.app.route('/u/<user_url_slug>/following/', methods=['POST', 'GET'])
def show_following(user_url_slug):
    if not check_user_url_slug_exists(user_url_slug):
        abort(404)

    # Connect to database
    connection = insta485.model.get_db()

    user = "michjc"
    flask.session['username'] = user

    """
    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        return redirect("/accounts/login")
    """

    # IF Post
    if request.method == "POST":
        if "unfollow" in request.form:
            unfollow(user, request.form["username"])
        elif "follow" in request.form:
            follow(user, request.form["username"])
    # GET
    cur = connection.execute("""
        SELECT username2 FROM following
        WHERE username1 = ?
    """, [user_url_slug]
    )
    test = cur.fetchall()
    list = []
    for item in test:
        pair = (item["username2"], check_login_following(
            user, item["username2"]), get_profile_image(item["username2"]))
        list.append(pair)
    # pdb.set_trace()
    context = {"list": list}
    return flask.render_template("following.html", **context, logname=user, slug=user_url_slug)


def check_user_url_slug_exists(user_url_slug):
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT COUNT(*) FROM users
        WHERE username = ?
    """, [user_url_slug]
    )
    num_as_string = cur.fetchall()
    # pdb.set_trace()
    return int(num_as_string[0]['COUNT(*)']) == 1


def unfollow(logged_in, following):
    connection = insta485.model.get_db()

    connection.execute("""
        DELETE FROM following
        WHERE username1 = ? AND username2 = ?
        """, [logged_in, following]
    )


def follow(logged_in, follow):
    connection = insta485.model.get_db()
    connection.execute("""
        INSERT INTO following (username1, username2)
        VALUES (?, ?)
        """, [logged_in, follow]
    )


def check_login_following(logname, user):
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT COUNT(*) FROM following
        WHERE username1 = ? AND username2 = ?
    """, [logname, user]
    )
    num_as_string = cur.fetchall()
    return int(num_as_string[0]['COUNT(*)']) == 1


def get_profile_image(user):
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT filename FROM users
        WHERE username = ? 
    """, [user]
    )
    img = cur.fetchall()
    return img[0]["filename"]
