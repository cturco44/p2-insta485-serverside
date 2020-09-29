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
from insta485.views.create import upload_file
from insta485.views.following import check_user_url_slug_exists, check_login_following, unfollow, follow
@insta485.app.route('/u/<user_url_slug>/', methods=['POST', 'GET'])
def user(user_url_slug):
    if not check_user_url_slug_exists(user_url_slug):
        abort(404)
    if request.method == 'POST':
        edit = False
        if user_url_slug == flask.session.get('username'):#user's own page
            edit = True
            following = 2
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
        posts = get_posts(owner)
        img_folder = insta485.app.config["UPLOAD_FOLDER"]
    return render_template('user.html', edit, following, username=user_url_slug,
    total_posts, total_followers, total_following, fullname, posts, img_folder)

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
    """, (post_id, post_filename, post_owner)
    )
def post_count(owner):
    cur = execute_query(
    """
    SELECT COUNT(*) FROM posts
    WHERE owner = ?
    """, (owner)
    )
    post_count = int(cur.fetchall()[0]['COUNT(*)'])
    return post_count

def follower_count(owner):
    cur = execute_query(
    """
    SELECT COUNT(*)FROM following
    WHERE username2 = ?
    """, (owner)
    )

    followers = cur.fetchall()[0]['COUNT(*)']
    return followers

def following_count(owner):
    cur = execute_query(
    """
    SELECT COUNT(*) FROM following
    WHERE username1 = ?
    """, (owner)
    )
    following = cur.fetchall()[0]['COUNT(*)']
    return following

def get_fullname(owner):
    cur = execute_query(
    """
    SELECT fullname FROM user
    WHERE username = ?
    """, (owner)
    )
    fullname = cur.fetchall()[0]['fullname']
    return fullname

def get_posts(owner):
    cur = execute_query(
    """
    SELECT post_id, filename FROM posts
    WHERE owner = ?
    ORDER BY post_id
    """, (owner)
    )
    posts = cur.fetchall()
    return posts
