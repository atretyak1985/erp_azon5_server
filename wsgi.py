import sys

sys.path.insert(0, '/var/www/catalog')


from erp_azon5_server import app as application

application.secret_key = 'New secret key. Change it on server'

application.config['SQLALCHEMY_DATABASE_URI'] = ('postgresql://atretyak:welcome123@localhost/rpm_db')