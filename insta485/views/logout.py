"""
Insta485 Logout view.

URLs include:
/accounts/logout/
"""

import flask
import insta485

@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    flask.session.pop('username', None)
    return flask.redirect('/accounts/login/')
