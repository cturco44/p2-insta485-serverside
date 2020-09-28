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
    if not check_post_exists(postid):
        abort(404)

    # Connect to database
    connection = insta485.model.get_db()

    # TODO: delete later
    logname = "awdeorio"
    flask.session['user'] = 'awdeorio'

    if "user" in flask.session:
        logname = flask.session["user"]
    #else:
        #return redirect("/accounts/login")

    if request.method == "POST":
        if 'uncomment' in request.form:
            if check_user_comment(request.form['commentid']):
                if not check_comment_exists(request.form['commentid']):
                    abort(404)
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
                if not check_post_exists(deleted_postid):
                    abort (404)

                delete_post(deleted_postid)

                return redirect("/u/" + logname + "/") # TODO: url_for
            else:
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
    """
    connection = insta485.model.get_db()
    # See if the file is an uploaded post
    cur = connection.execute(" #TODO: TRIPLE QUOTES
        SELECT owner FROM posts
        WHERE filename = ?
    ", [filename]
    )
    owner = cur.fetchall()

    # If not a post, check if it's a profile pic
    if len(owner) < 1:
        cur = connection.execute(" #TODO: TRIPLE QUOTES
            SELECT username FROM users
            WHERE filename = ?
        ", [filename]
        )
        owner=cur.fetchall()

        # Still not found, then abort
        if len(owner) < 1:
            abort(403)
        else:
            user = owner[0]['username']
    else:
        user = owner[0]['owner']

    if ("user" not in flask.login) or (user != flask.login['user']):
        abort(403)
    """
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
    if "user" not in flask.session:
        return False

    logname = flask.session["user"]
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
    if "user" not in flask.session:
        return False

    logname = flask.session["user"]
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT owner FROM comments
        WHERE commentid = ?
    """, [commentid]
    )
    comment_owner = cur.fetchall()[0]['owner']

    return comment_owner == logname


def check_comment_exists(commentid):
    """Returns whether comment exists."""
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT owner FROM comments
        WHERE commentid = ?
    """, [commentid]
    )
    comment = cur.fetchall()

    return len(comment) > 0


def check_post_exists(postid):
    """Returns whether post exists."""
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT owner FROM posts
        WHERE postid = ?
    """, [postid]
    )
    post = cur.fetchall()

    return len(post) > 0
