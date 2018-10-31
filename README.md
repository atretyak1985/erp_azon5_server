## Setup

```
git clone https://git.heroku.com/azon5-server.git
cd flask-app-structure-example
virtualenv -p python3 env
source env/bin/activate
pip freeze > requirements.txt
pip install -r requirements.txt
export APP_SETTINGS="config.DevelopmentConfig"
# DBUSERNAME, DBPASSWORD ? DBNAME ?????????? ???????? ?? ???? ????????? ??????? ? ??
export DATABASE_URL='postgresql://atretyak:welcome123@localhost/rpm_db'
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
python manage.py runserver
```