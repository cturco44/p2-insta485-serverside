"""
Insta485 post view.

URLs include:
/p/<postid_url_slug>/
"""
import flask
from flask import request, session
import insta485
import arrow


@insta485.app.route('/p/<int:postid>/', methods=['POST', 'GET'])
def show_post(postid):
    # Connect to database
    connection = insta485.model.get_db()

    # TODO: else ?
    if "user" in flask.session:
        user = flask.session["user"]
        logname = user
    
    # TODO: delete this once we've got the users done and shit
    logname="placeholder"

    if request.method == "POST":
        # delete own comment
        if 'uncomment' in request.form:
            deleted_commentid = request.form['commentid']

            connection.execute("""
                DELETE FROM comments
                WHERE commentid = ?
            """, [deleted_commentid]
            )

        # TODO: like/dislike buttons in template
        elif 'like' in request.form:
            liked_postid = request.form['postid']

            connection.execute("""
                INSERT OR IGNORE INTO likes(owner, postid)
                VALUES(?, ?)
            """, [logname, liked_postid]
            )

        elif 'unlike' in request.form:
            unliked_postid = request.form['postid']

            connection.execute("""
                DELETE FROM likes
                WHERE postid = ? AND owner = ?
            """, [unliked_postid, logname]
            )

        # post new comment
        elif 'comment' in request.form:
            comment_text = request.form['text']
            comment_postid = request.form['postid']

            connection.execute(""" 
                INSERT INTO comments(owner, postid, text)
                VALUES(?, ?, ?, ?)
            """, [logname, comment_postid, comment_text]
            )

        # delete own post
        elif 'delete' in request.form:
            deleted_postid = request.form['postid']

            connection.execute("""
                DELETE FROM posts
                WHERE postid = ?
            """, [deleted_postid]
            )

            # TODO: also delete comments and likes with this postid?


    # Query database
    cur = connection.execute("""
        SELECT * 
        FROM posts
        WHERE postid = ?
    """, [postid]
    )
    post = cur.fetchall()

    # Query database
    cur = connection.execute("""
        SELECT * 
        FROM likes
        WHERE postid = ?
    """, [postid]
    )
    likes = cur.fetchall()

    # Query database
    cur = connection.execute("""
        SELECT * 
        FROM comments
        WHERE postid = ?
    """, [postid]
    )
    comments = cur.fetchall()

    arrow_obj = arrow.get(post[0]['created'])
    timestamp = arrow_obj.humanize()

    # Add database info to context
    context = {"post": post, "likes": likes, "comments": comments}
    return flask.render_template("post.html", **context, timestamp=timestamp, logname=logname) # TODO: fix logname


@insta485.app.route('/uploads/<path:post_filename>')
def download_file(filename):
    return send_from_directory(app.config[UPLOAD_FOLDER], post_filename, as_attachment=False) #TODO: UPLOAD_FOLDER was '/var/uploads/'