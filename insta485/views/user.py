"""
Insta485 user view.

URLs include:
/u/<user_url_slug>/
"""

from flask import request, render_template, url_for, abort, redirect
import flask
import insta485
from insta485.views.create import upload_file
from insta485.views.following import check_user_url_slug_exists, \
    check_login_following, unfollow, follow


@insta485.app.route('/u/<user_url_slug>/', methods=['POST', 'GET'])
def user(user_url_slug):
    """User func."""
    if 'username' in flask.session:
        logname = flask.session['username']
    else:
        return redirect(url_for('login'))
    if not check_user_url_slug_exists(user_url_slug):
        abort(404)

    edit = False
    following = 2
    if request.method == 'POST':
        if 'file' in request.files:
            fileobj = request.files['file']
            if fileobj.filename == '':
                abort(400)
            filename = upload_file(fileobj)
            add_post(filename, user_url_slug)

        if 'unfollow' in request.form:
            unfollow(flask.session['username'], user_url_slug)
        elif 'follow' in request.form:
            follow(flask.session['username'], user_url_slug)
    if user_url_slug == flask.session.get('username'):  # user's own page
        edit = True
    else:  # other's page
        if check_login_following(flask.session['username'], user_url_slug):
            following = 1
        else:
            following = 0
    total_posts = post_count(user_url_slug)
    total_followers = follower_count(user_url_slug)
    total_following = following_count(user_url_slug)
    fullname = get_fullname(user_url_slug)
    posts = get_posts(user_url_slug)

    return render_template(
        'user.html',
        edit=edit,
        following=following,
        total_posts=total_posts,
        total_followers=total_followers,
        total_following=total_following,
        fullname=fullname,
        posts=posts,
        logname=logname,
        user_url_slug=user_url_slug,
        )


def execute_query(query, parameters=None):
    """Execute query."""
    connection = insta485.model.get_db()
    if not parameters:
        cur = connection.execute(query)
    else:
        cur = connection.execute(query, parameters)
    return cur


def add_post(filename, owner):
    """Add post."""
    cur = execute_query(
        """
    SELECT COUNT(*) FROM posts
    """
    )
    count = int(cur.fetchall()[0]['COUNT(*)'])
    postid = count + 1
    post_filename = filename
    post_owner = owner
    execute_query(
        """
    INSERT INTO posts(postid, filename, owner)
    VALUES(?, ?, ?);
    """, (postid, post_filename, post_owner)
    )


def post_count(owner):
    """Post count."""
    cur = execute_query(
        """
    SELECT COUNT(*) FROM posts
    WHERE owner = ?
    """, (owner,)
    )
    count = int(cur.fetchall()[0]['COUNT(*)'])
    return count


def follower_count(owner):
    """Follower count."""
    cur = execute_query(
        """
    SELECT COUNT(*)FROM following
    WHERE username2 = ?
    """, (owner,)
    )

    followers = cur.fetchall()[0]['COUNT(*)']
    return followers


def following_count(owner):
    """Following count."""
    cur = execute_query(
        """
    SELECT COUNT(*) FROM following
    WHERE username1 = ?
    """, (owner,)
    )
    following = cur.fetchall()[0]['COUNT(*)']
    return following


def get_fullname(owner):
    """Get fullname."""
    cur = execute_query(
        """
    SELECT fullname FROM users
    WHERE username = ?
    """, (owner,)
    )
    fullname = cur.fetchall()[0]['fullname']
    return fullname


def get_posts(owner):
    """Get Posts."""
    cur = execute_query(
        """
    SELECT postid, filename FROM posts
    WHERE owner = ?
    ORDER BY postid DESC
    """, (owner,)
    )
    posts = cur.fetchall()
    return posts
