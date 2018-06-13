import os, datetime, configparser
from flask import Flask
from .database import db

def create_app():
    app = Flask(__name__)
    configureApp(app)

    db.init_app(app)
    with app.test_request_context():
        db.create_all()

    if app.debug == True:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            toolbar = DebugToolbarExtension(app)
        except:
            pass

    import app.entity.controllers as entity
    import app.comment.controllers as comment
    import app.general.controllers as general
    import app.user.controllers as user

    app.register_blueprint(general.module)
    app.register_blueprint(entity.module)
    app.register_blueprint(comment.module)
    app.register_blueprint(user.module)

    return app

def configureApp(app):
    config = configparser.ConfigParser()
    config.read('config.ini')

    app.config.from_object(config['DEFAULT']['APP_SETTINGS'])

    app.config['JWT_AUTH_URL_RULE'] = config['DEFAULT']['JWT_AUTH_URL_RULE']
    app.config['JWT_AUTH_USERNAME_KEY'] = config['DEFAULT']['JWT_AUTH_USERNAME_KEY']
    app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=config.getint('DEFAULT', 'JWT_EXPIRATION_DELTA'))

    app.secret_key = config['DEFAULT']['SECRET_KEY']
