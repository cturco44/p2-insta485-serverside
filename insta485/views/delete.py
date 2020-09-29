import os
import flask
from flask import request, send_from_directory, redirect, abort
import insta485
from insta485.config import UPLOAD_FOLDER
import pdb
import pathlib
import uuid

@insta485.app.route('/accounts/delete/', methods=['POST', 'GET'])
def delete_account():
    if "username" not in flask.session:
        return redirect('/accounts/create/')
    else:
        user = flask.session['username']
    if request.method == "POST":
        if 'delete' in request.form:
            delete_user(user)
            del flask.session['username']
            return redirect("/accounts/create")
    return flask.render_template("delete.html", logname=user)
    
def delete_user(user):
    connection = insta485.model.get_db()
    cur = connection.execute("""
        SELECT filename FROM posts
        WHERE owner = ?
        """,[user]
    )
    filenames = cur.fetchall()
    delete_images(filenames)

    cur = connection.execute("""
        SELECT filename FROM users
        WHERE username = ?
        """,[user]
    )
    profile_pic = cur.fetchall()
    delete_images(profile_pic)

    connection.execute("""
        DELETE FROM users
        WHERE username = ?
        """,[user]
    )
def delete_images(list):
    for item in list:
        os.remove(str(UPLOAD_FOLDER/item['filename']))


    
