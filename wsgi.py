import sys

sys.path.insert(0, '/var/www/erp_azon5_server')


from app import app as application

application.secret_key = 'New secret key. Change it on server'

application.config['SQLALCHEMY_DATABASE_URI'] = ('postgresql://atretyak:welcome123@localhost/rpm_db')