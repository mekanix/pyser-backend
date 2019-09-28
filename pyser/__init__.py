from flask import Blueprint, Flask, send_file
from flask_collect import Collect
from flask_jwt_extended import JWTManager
from flask_security import PeeweeUserDatastore, Security

from .api import create_api
from .db import db


def create_app(config, app=None):
    class Result(object):
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    if app is None:
        app = Flask(__name__)
        app.config.from_object(config)

    @app.route('/media/<path:path>')
    def send_media(path):
        fullPath = f"../{app.config['MEDIA_PATH']}/{path}"
        try:
            return send_file(fullPath)
        except FileNotFoundError:
            return 'No such file', 404

    app.collect = Collect(app)
    db.init_app(app)
    app.db = db

    from .models.auth import User, Role, UserRoles
    app.user_datastore = PeeweeUserDatastore(
        app.db,
        User,
        Role,
        UserRoles,
    )
    app.security = Security(app, app.user_datastore)
    app.jwt = JWTManager(app)
    create_api(app)

    return app
