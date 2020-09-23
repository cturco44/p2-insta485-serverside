"""
Insta485 edit view.

URLs include:
/accounts/edit/
"""
import flask
from flask import request, session
import insta485
import pathlib
import uuid
import insta485

@insta485.app.route('/accounts/edit/', methods=['POST', 'GET'])
def show_edit():
    # Connect to database
    connection = insta485.model.get_db()

    #TODO: initialize to blank
    logname = "michjc"
    logname_filename = '5ecde7677b83304132cb2871516ea50032ff7a4f.jpg'
    logname_fullname = 'Michael Cafarella'
    logname_email = 'michjc@umich.edu'

    if "user" in flask.session:
        logname = flask.session["user"]
        logname_filename = flask.session["filename"]
        logname_fullname = flask.session["fullname"]
        logname_email = flask.sesion["email"]

    if request.method == "POST":
        if 'update' in request.form:
            if request.files['file'].filename != "":
                # Unpack flask object
                fileobj = flask.request.files["file"]
                filename = fileobj.filename

                # Compute base name (filename without directory).  We use a UUID to avoid
                # clashes with existing files, and ensure that the name is compatible with the
                # filesystem.
                uuid_basename = "{stem}{suffix}".format(
                    stem=uuid.uuid4().hex,
                    suffix=pathlib.Path(filename).suffix
                )

                # Save to disk
                path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
                fileobj.save(path)

                # Delete old photo
                delete_path = insta485.app.config["UPLOAD_FOLDER"]/logname_filename
                unlink(delete_path)

                connection.execute("""
                    UPDATE users
                    SET filename = ?
                    WHERE username = ?
                """, [filename, logname]
                )
            
            connection.execute("""
                UPDATE users
                SET fullname = ?,
                email = ?
                WHERE username = ?
            """, [request.form['fullname'], request.form['email'], logname]
            )


    return flask.render_template("edit.html", logname=logname, logname_filename=logname_filename,
                                    logname_fullname=logname_fullname, logname_email=logname_email)
                                    