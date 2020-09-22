"""
Insta485 explore view.

URLs include:
/explore/
"""
import flask
from flask import request, session
import insta485

@insta485.app.route('/explore/')
def show_explore():
    # Connect to database
    connection = insta485.model.get_db()

    # TODO: logged in username
    if "user" in flask.session:
        user = flask.session["user"]
        logname = user

    if request.method == "POST":
        # follow user that logname is not following
        if 'follow' in request.form:
            followed_user = request.form['username']

            connection.execute("""
                INSERT INTO following(username1, username2)
                VALUES(?, ?)
            """, [logname, followed_user]
            )


    # Query database
    # TODO: idk if this is right
    # want to select rows in "users" of people that logname is not following
    cur = connection.execute("""
        SELECT DISTINCT username FROM users
        WHERE NOT EXISTS (SELECT * FROM following
                            WHERE following.username1 = ?)
        AND following.username2 = users.username
    """, [logname]
    )
    not_following = cur.fetchall()


    context = {"not_following": not_following}
    return flask.render_template("explore.html", **context, logname=logname) # TODO: logname
