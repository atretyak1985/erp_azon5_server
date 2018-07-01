import configparser
from app import app as application
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.database import db
from app import app as application

config = configparser.ConfigParser()
config.read('app/config.ini')

manager = Manager(application)
migrate = Migrate(application, db, 'migrations')
manager.add_command('db', MigrateCommand)

import logging
logging.basicConfig()

if __name__ == '__main__':
    #manager.run()
    #application.run()
    application.run(port=config.getint('DEFAULT', 'APP_PORT'), debug=True)
