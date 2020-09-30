"""
Insta485 password view.

URLs include:
/u/<user_url_slug>/followers/
"""
import flask
import insta485
from flask import request, abort
from insta485.views.user import execute_query
from insta485.views.following import check_user_url_slug_exists, get_profile_image, follow, unfollow, check_login_following
@insta485.app.route('/u/<user_url_slug>/followers/', methods=['POST', 'GET'])
def followers(user_url_slug):
    if 'username' in flask.session:
        logname = flask.session['username']
    else:
        return flask.redirect('/accounts/login/')
    if not check_user_url_slug_exists(user_url_slug):
        abort(404)
    if request.method == "POST":
        if "unfollow" in request.form:
            unfollow(logname, request.form["username"])
        elif "follow" in request.form:
            follow(logname, request.form["username"])
    follower_names = get_followers(user_url_slug)
    all_followers = []
    for follower in follower_names:
        icon_filename =  get_profile_image(follower['username1'])
        follower_name = follower['username1']
        login_following = check_login_following(logname, follower_name)
        print((icon_filename, follower_name, login_following))
        all_followers.append((icon_filename, follower_name, login_following))
    return flask.render_template('followers.html', all_followers=all_followers,
    logname=logname, user_url_slug=user_url_slug)



def get_followers(owner):
    cur = execute_query(
    """
    SELECT username1 FROM following
    WHERE username2 = ?
    """, (owner,)
    )
    followers = cur.fetchall()
    return followers
