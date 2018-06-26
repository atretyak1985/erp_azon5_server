import configparser
from app import create_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.database import db

config = configparser.ConfigParser()
config.read('config.ini')

app = create_app()

manager = Manager(app)
migrate = Migrate(app, db, 'migrations')
manager.add_command('db', MigrateCommand)

import logging
logging.basicConfig()

if __name__ == '__main__':
    manager.run()
    #app.run(port=config.getint('DEFAULT', 'APP_PORT'), debug=config['DEFAULT'].getboolean('APP_DEBUG'))
