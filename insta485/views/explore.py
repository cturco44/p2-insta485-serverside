"""
Insta485 explore view.

URLs include:
/explore/
"""
import flask
from flask import request, redirect, url_for
import insta485


@insta485.app.route('/explore/', methods=['POST', 'GET'])
def show_explore():
    """For /explore/ page."""
    # Connect to database
    connection = insta485.model.get_db()

    # TODO: delete this once we've got the users done and shit
    logname = "michjc"
    flask.session['user'] = 'michjc'

    if "user" in flask.session:
        logname = flask.session["user"]
    #else:
        #return redirect("/accounts/login")

    if request.method == "POST":
        # follow user that logname is not following
        follow_user(logname, request.form['username'])

    # Query database
    # want to select rows in "users" of people that logname is not following
    cur = connection.execute("""
        SELECT DISTINCT username, filename FROM users
        WHERE NOT EXISTS (SELECT * FROM following
                            WHERE following.username1 = ?
                            AND following.username2 = users.username)
    """, [logname]
    )
    not_following = cur.fetchall()
    context = {"not_following": not_following}
    return flask.render_template("explore.html", **context, logname=logname)


@insta485.app.route('/follow/<logname>/<username>/',
                    methods=["POST", "GET"])
def follow_user(logname, username):
    """For following a user."""
    connection = insta485.model.get_db()

    connection.execute("""
        INSERT INTO following(username1, username2)
        VALUES(?, ?)
    """, [logname, username]
    )
