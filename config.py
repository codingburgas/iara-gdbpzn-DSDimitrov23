import os
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'iara_database.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# small helper used by models default values
def now_date_str():
    return datetime.utcnow().strftime('%Y-%m-%d')
