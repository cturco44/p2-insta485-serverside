"""
Insta485 edit view.

URLs include:
/accounts/edit/
"""
import pathlib
import uuid
import os
import flask
from flask import request, redirect, url_for
import insta485


@insta485.app.route('/accounts/edit/', methods=['POST', 'GET'])
def show_edit():
    """For /accounts/edit/ page."""
    # Connect to database
    connection = insta485.model.get_db()

    # TODO: initialize to blank
    logname = "michjc"
    flask.session['username'] = 'michjc'

    cur = connection.execute("""
        SELECT filename, fullname, email FROM users
        WHERE username = ?
    """, [logname]
    )
    user_obj = cur.fetchall()
    logname_filename = user_obj[0]['filename']
    logname_fullname = user_obj[0]['fullname']
    logname_email = user_obj[0]['email']

    if "username" in flask.session:
        logname = flask.session["username"]

        cur = connection.execute("""
            SELECT filename, fullname, email FROM users
            WHERE username = ?
        """, [logname]
        )
        user_obj = cur.fetchall()
        logname_filename = cur.fetchall()[0]['filename']
        logname_fullname = cur.fetchall()[0]['fullname']
        logname_email = cur.fetchall()[0]['email']
    else:
        return redirect("/accounts/login") # TODO: use url_for

    if request.method == "POST":
        if 'update' in request.form:
            # if photo file included
            if request.files['file'].filename != "":
                # Unpack flask object
                fileobj = flask.request.files["file"]
                filename = fileobj.filename

                # Compute base name (filename without directory).
                uuid_basename = "{stem}{suffix}".format(
                    stem=uuid.uuid4().hex,
                    suffix=pathlib.Path(filename).suffix
                )

                # Save to disk
                path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
                fileobj.save(path)

                # Delete old photo
                del_pth = insta485.app.config["UPLOAD_FOLDER"]/logname_filename
                os.unlink(del_pth)

                # Update info
                logname_filename = uuid_basename
                logname_fullname = request.form['fullname']
                logname_email = request.form['email']

                connection.execute("""
                    UPDATE users
                    SET filename = ?,
                    fullname = ?,
                    email = ?
                    WHERE username = ?
                """, [uuid_basename, request.form['fullname'],
                      request.form['email'], logname]
                )

            else:
                connection.execute("""
                    UPDATE users
                    SET fullname = ?,
                    email = ?
                    WHERE username = ?
                """, [request.form['fullname'], request.form['email'], logname]
                )

                # Update info
                logname_fullname = request.form['fullname']
                logname_email = request.form['email']

    return flask.render_template("edit.html", logname=logname,
                                 logname_filename=logname_filename,
                                 logname_fullname=logname_fullname,
                                 logname_email=logname_email)
