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
    """Specific post's page"""
    # Connect to database
    connection = insta485.model.get_db()

    if request.method == "POST":
        # delete own comment
        if 'uncomment' in request.form:
            deleted_commentid = request.form['commentid']

            connection.execute("""
                DELETE FROM comments
                WHERE commentid = ?
            """, [deleted_commentid]
            )

        # like the post
        elif 'liker-user' in request.form:
            liker_user = request.form['liker-user']
            liked_postid = request.form['postid']

            connection.execute("""
                INSERT OR IGNORE INTO likes(owner, postid)
                VALUES(?, ?)
            """, [liker_user, liked_postid]
            )

        # post new comment
        elif 'commenter-user' in request.form:
            new_comment = request.form['comment-text']
            commenter_user = request.form['commenter-user']
            comment_postid = request.form['postid']
            
            curr_comment_count = connection.execute("SELECT COUNT(*) FROM comments")
            new_commentid = curr_comment_count + 1

            connection.execute(""" 
                INSERT INTO comments(commentid, owner, postid, text)
                VALUES(?, ?, ?, ?)
            """, [new_commentid, commenter_user, comment_postid, new_comment]
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

    #TODO: session['username']
    logname="placeholder"

    # Add database info to context
    context = {"post": post, "likes": likes, "comments": comments}
    return flask.render_template("post.html", **context, timestamp=timestamp, logname=logname) # TODO: fix logname


@insta485.app.route('/uploads/<path:post_filename>')
def download_file(filename):
    return send_from_directory(app.config['/var/uploads/'], post_filename, as_attachment=False)