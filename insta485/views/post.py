"""
Insta485 post view.

URLs include:
/p/<postid_url_slug>/
"""
import os
import arrow
import flask
from flask import request, send_from_directory, redirect, abort, url_for
import insta485


@insta485.app.route('/p/<int:postid>/', methods=['POST', 'GET'])
def show_post(postid):
    """For /p/<postid_url_slug/ page."""
    check_post_exists(postid)

    # Connect to database
    connection = insta485.model.get_db()

    # TODO: uncomment for testing
    """
    logname = "awdeorio"
    flask.session['username'] = 'awdeorio'
    """

    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        return redirect("/accounts/login/")


    if request.method == "POST":
        if 'uncomment' in request.form:
            if check_user_comment(request.form['commentid']):
                check_comment_exists(request.form['commentid'])
                uncomment(request.form['commentid'])
            else:
                abort(403)

        elif 'like' in request.form:
            like_post(logname, request.form['postid'])

        elif 'unlike' in request.form:
            unlike_post(logname, request.form['postid'])

        elif 'comment' in request.form:
            comment(logname, request.form['postid'], request.form['text'])

        elif 'delete' in request.form:
            deleted_postid = request.form['postid']
            if check_user_post(deleted_postid):
                check_post_exists(deleted_postid)
                delete_post(deleted_postid)

                return redirect("/u/" + logname + "/")  # TODO: url_for

            abort(403)

    # Query database
    cur = connection.execute("""
        SELECT *
        FROM posts
        WHERE postid = ?
    """, [postid]
    )
    post = cur.fetchall()

    cur = connection.execute("""
        SELECT *
        FROM likes
        WHERE postid = ?
    """, [postid]
    )
    likes = cur.fetchall()

    cur = connection.execute("""
        SELECT *
        FROM comments
        WHERE postid = ?
    """, [postid]
    )
    comments = cur.fetchall()

    cur = connection.execute("""
        SELECT filename, username FROM users
        WHERE EXISTS (SELECT * FROM posts
                        WHERE users.username = posts.owner
                        AND posts.postid = ?)
    """, [postid]
    )
    owner = cur.fetchall()

    cur = connection.execute("""
        SELECT owner FROM likes
        WHERE postid = ?
        AND owner = ?
    """, [postid, logname]
    )
    owner_like = cur.fetchall()

    arrow_obj = arrow.get(post[0]['created'])
    timestamp = arrow_obj.humanize()

    # Add database info to context
    context = {"post": post, "likes": likes, "comments": comments,
               "owner": owner, "owner_like": owner_like}
    return flask.render_template("post.html", **context,
                                 timestamp=timestamp,
                                 logname=logname)


@insta485.app.route('/uploads/<path:filename>')
def download_file(filename):
    """For showing images on pages."""
    if "username" not in flask.session:
        abort(403)

    return send_from_directory(insta485.app.config["UPLOAD_FOLDER"],
                               filename, as_attachment=False)


def uncomment(commentid):
    """Delete comment."""
    connection = insta485.model.get_db()
    connection.execute("""
        DELETE FROM comments
        WHERE commentid = ?
    """, [commentid]
    )


def like_post(logname, postid):
    """Like a post."""
    connection = insta485.model.get_db()
    connection.execute("""
        INSERT OR IGNORE INTO likes(owner, postid)
        VALUES(?, ?)
    """, [logname, postid]
    )


def unlike_post(logname, postid):
    """Unlike a post."""
    connection = insta485.model.get_db()
    connection.execute("""
        DELETE FROM likes
        WHERE postid = ? AND owner = ?
    """, [postid, logname]
    )


def comment(logname, postid, comment_text):
    """Make a comment on a post."""
    connection = insta485.model.get_db()
    connection.execute("""
        INSERT OR IGNORE INTO comments(owner, postid, text)
        VALUES(?, ?, ?)
    """, [logname, postid, comment_text]
    )


def delete_from_database(postid):
    """Delete post from database only."""
    connection = insta485.model.get_db()
    connection.execute("""
        DELETE FROM posts
        WHERE postid = ?
    """, [postid]
    )


def delete_post(postid):
    """Delete a post's source image and from the database."""
    # find filename
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT filename from posts
        WHERE postid = ?
    """, [postid]
    )
    deleted_filename = cur.fetchall()[0]['filename']

    # delete from database
    delete_from_database(postid)

    # delete file
    delete_path = insta485.app.config["UPLOAD_FOLDER"]/deleted_filename
    os.unlink(delete_path)


def check_user_post(postid):
    """Return if user is owner of post."""
    if "username" not in flask.session:
        return False

    logname = flask.session["username"]
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT owner FROM posts
        WHERE postid = ?
    """, [postid]
    )
    post_owner = cur.fetchall()[0]['owner']

    return post_owner == logname


def check_user_comment(commentid):
    """Return if user is owner of comment."""
    if "username" not in flask.session:
        return False

    logname = flask.session["username"]
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT owner FROM comments
        WHERE commentid = ?
    """, [commentid]
    )
    comment_owner = cur.fetchall()[0]['owner']

    return comment_owner == logname


def check_comment_exists(commentid):
    """Return whether comment exists."""
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT owner FROM comments
        WHERE commentid = ?
    """, [commentid]
    )
    comment_obj = cur.fetchall()

    if len(comment_obj) < 1:
        abort(404)


def check_post_exists(postid):
    """Return whether post exists."""
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT owner FROM posts
        WHERE postid = ?
    """, [postid]
    )
    post_obj = cur.fetchall()

    if len(post_obj) < 1:
        abort(404)
