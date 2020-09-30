"""
Insta485 Logout view.

URLs include:
/accounts/logout/
"""

from flask import url_for
import flask
import insta485


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Logout flask function."""
    flask.session.pop('username', None)
    return flask.redirect(url_for('login'))
