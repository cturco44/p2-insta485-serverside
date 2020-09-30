"""
Insta485 index (main) view.

URLs include:
/
"""
import os
import arrow
import flask
from flask import request, send_from_directory, redirect, abort, url_for
import insta485
from insta485.views.post import like_post, unlike_post, comment
import pdb


@insta485.app.route('/', methods=['POST', 'GET'])
def show_index():
    """Display / route."""
    # Connect to database
    connection = insta485.model.get_db()



    if "username" in flask.session:
        logname = flask.session["username"]
    else:
        return redirect("/accounts/login")


    if request.method == "POST":
        if 'like' in request.form:
            like_post(logname, request.form['postid'])
        elif 'unlike' in request.form:
            unlike_post(logname, request.form['postid'])
        elif 'comment' in request.form:
            comment(logname, request.form['postid'], request.form['text'])
        return redirect('/')

    # ALL USERS logname follows
    cur = connection.execute("""
        SELECT username2 FROM following
        WHERE username1 = ?
    """, [logname]
    )

    # Generate SQL query for posts in order
    following = cur.fetchall()

    query = "SELECT * FROM posts\nWHERE"
    if following:

        for i, item in enumerate(following):
            if i == 0:
                query += (" owner = " + "\'" + item['username2'] + "\'")
            else:
                query += (" OR owner = " + "\'" + item['username2'] + "\'")
        query += "\nORDER BY postID DESC"
        cur = connection.execute(query)
        posts = cur.fetchall()
    else:
        posts = []

    for i in posts:
        # Humanize timestamps
        arrow_obj = arrow.get(i['created'])
        timestamp = arrow_obj.humanize()
        i['created'] = timestamp

        # add comments
        i['comments'] = list_comments(i['postid'])

        # add num_likes
        i['num_likes'] = num_likes(i['postid'])

        # add_owner_liked bool
        i['logname_liked'] = logname_liked(i['postid'], logname)

        # add profile_pic
        i['owner_pic'] = owner_profile_pic(i['owner'])

    return flask.render_template("index.html", posts=posts, logname=logname)


def list_comments(post_id):
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT * FROM comments
        WHERE postid = ?
        ORDER BY commentID ASC
    """, [post_id]
    )
    comments = cur.fetchall()
    for i in comments:
        arrow_obj = arrow.get(i['created'])
        timestamp = arrow_obj.humanize()
        i['created'] = timestamp
    return comments


def num_likes(post_id):
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT COUNT(*) FROM likes
        WHERE postid = ?
    """, [post_id]
    )
    num_as_string = cur.fetchall()
    return int(num_as_string[0]['COUNT(*)'])


def logname_liked(post_id, logname):
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT COUNT(*) FROM likes
        WHERE postid = ? AND owner = ?
    """, [post_id, logname]
    )
    num_as_string = cur.fetchall()
    return int(num_as_string[0]['COUNT(*)']) == 1


def owner_profile_pic(owner):
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT filename FROM users
        WHERE username = ?
    """, [owner]
    )
    filename = cur.fetchall()
    return filename[0]['filename']
