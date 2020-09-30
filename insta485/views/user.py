"""
Insta485 password view.

URLs include:
/u/<user_url_slug>/
"""

import flask
import insta485
import pathlib
import uuid
import insta485
from flask import request, render_template
from insta485.views.create import upload_file
from insta485.views.following import check_user_url_slug_exists, check_login_following, unfollow, follow
@insta485.app.route('/u/<user_url_slug>/', methods=['POST', 'GET'])
def user(user_url_slug):
    if not check_user_url_slug_exists(user_url_slug):
        flask.abort(404)
    if 'username' in flask.session:
        logname = flask.session['username']
    else:
        return flask.redirect('/accounts/login/')
    edit = False
    following = 2
    if request.method == 'POST':
        if user_url_slug == flask.session.get('username'):#user's own page
            edit = True
            if 'file' in request.files:
                fileobj = request.files['file']
                filename = upload_file(fileobj)
                add_post(filename, user_url_slug)
        else:#other's page
            if check_login_following(flask.session['username'], user_url_slug):
                following = 1
                if 'unfollow' in request.form:
                    unfollow(flask.session['username'], user_url_slug)
            else:
                following = 0
                if 'follow' in request.form:
                    follow(flask.session['username'], user_url_slug)
    total_posts = post_count(user_url_slug)
    total_followers = follower_count(user_url_slug)
    total_following = following_count(user_url_slug)
    fullname = get_fullname(user_url_slug)
    posts = get_posts(user_url_slug)

    return render_template('user.html', edit=edit, following=following,
    total_posts=total_posts, total_followers=total_followers,
    total_following=total_following,
    fullanme=fullname, posts=posts, logname=logname,username=user_url_slug)
'''
@insta485.app.route('/uploads/<filename>/')
def get_pic(filename):
    return flask.send_from_directory('/uploads/<filename>/')
'''
def execute_query(query, parameters=None):
    connection = insta485.model.get_db()
    if not parameters:
        cur = connection.execute(query)
    else:
        cur = connection.execute(query, parameters)
    return cur
def add_post(filename, owner):
    cur = execute_query(
    """
    SELECT COUNT(*) FROM posts
    """
    )
    post_count = int(cur.fetchall()[0]['COUNT(*)'])
    post_id = postcount + 1
    post_filename = filename
    post_owner = owner
    execute_query(
    """
    INSERT INTO posts(postid, filename, owner)
    VALUES(?, ?, ?);
    """, (postid, post_filename, post_owner)
    )
def post_count(owner):
    cur = execute_query(
    """
    SELECT COUNT(*) FROM posts
    WHERE owner = ?
    """, (owner,)
    )
    post_count = int(cur.fetchall()[0]['COUNT(*)'])
    return post_count

def follower_count(owner):
    cur = execute_query(
    """
    SELECT COUNT(*)FROM following
    WHERE username2 = ?
    """, (owner,)
    )

    followers = cur.fetchall()[0]['COUNT(*)']
    return followers

def following_count(owner):
    cur = execute_query(
    """
    SELECT COUNT(*) FROM following
    WHERE username1 = ?
    """, (owner,)
    )
    following = cur.fetchall()[0]['COUNT(*)']
    return following

def get_fullname(owner):
    cur = execute_query(
    """
    SELECT fullname FROM users
    WHERE username = ?
    """, (owner,)
    )
    fullname = cur.fetchall()[0]['fullname']
    return fullname

def get_posts(owner):
    cur = execute_query(
    """
    SELECT postid, filename FROM posts
    WHERE owner = ?
    ORDER BY postid
    """, (owner,)
    )
    posts = cur.fetchall()
    return posts
