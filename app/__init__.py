import os
import datetime, configparser

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt import JWT
from flask_cors import CORS

from .database import db

from app.resources.user import UserRegister
from app.resources.messages import Message, MessageList
from app.resources.stats import Stats

from security import authenticate, identity as identity_function

def create_app():
    app = configureApp()
    api = configureJwt(app)

    configureResource(api)
    initDataBase(app)
    configLog(app)

    if app.debug == True:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            toolbar = DebugToolbarExtension(app)
        except:
            pass

    return app

def initDataBase(app):
    db.init_app(app)
    with app.test_request_context():
        db.create_all()


def configureApp():
    app = Flask(__name__)
    config = configparser.ConfigParser()
    config.read('config.ini')

    app.config['APP_SETTINGS'] = config['DEFAULT']['APP_SETTINGS']

    #app.config['SQLALCHEMY_DATABASE_URI'] = config['DEFAULT']['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config['DEFAULT']['SQLALCHEMY_TRACK_MODIFICATIONS']

    app.config['JWT_AUTH_URL_RULE'] = config['DEFAULT']['JWT_AUTH_URL_RULE']
    app.config['JWT_AUTH_USERNAME_KEY'] = config['DEFAULT']['JWT_AUTH_USERNAME_KEY']
    app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=config.getint('DEFAULT', 'JWT_EXPIRATION_DELTA'))

    app.secret_key = config['DEFAULT']['SECRET_KEY']

    return app

def configLog(app):
    # if not app.debug and os.environ.get('HEROKU') is None:
    #     import logging
    #     from logging.handlers import RotatingFileHandler
    #     file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
    #     file_handler.setLevel(logging.INFO)
    #     file_handler.setFormatter(
    #         logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    #     app.logger.addHandler(file_handler)
    #     app.logger.setLevel(logging.INFO)
    #     app.logger.info('microblog startup')
    #
    # if os.environ.get('HEROKU') is not None:
    #     import logging
    #     stream_handler = logging.StreamHandler()
    #     app.logger.addHandler(stream_handler)
    #     app.logger.setLevel(logging.INFO)
    #     app.logger.info('microblog startup')
    pass

def configureJwt(app):
    CORS(app)
    api = Api(app)
    jwt = JWT(app, authenticate, identity_function)

    @jwt.auth_response_handler
    def customized_response_handler(access_token, identity):
        return jsonify({
            'data':
                {
                    'token': access_token.decode('utf-8'),
                    '_id': identity.id,
                    'email': identity.email
                }
        })
    return api

def configureResource(api):
    api.add_resource(Stats, '/stats/<string:type>')
    api.add_resource(Message, '/message/<string:name>')
    api.add_resource(MessageList, '/messages')
    api.add_resource(UserRegister, '/user/register')
