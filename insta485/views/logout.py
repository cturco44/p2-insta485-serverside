"""
Insta485 Logout view.

URLs include:
/accounts/logout/
"""

import flask
import insta485
from flask import url_for


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    flask.session.pop('username', None)
    return flask.redirect(url_for('login'))
