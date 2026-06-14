import os
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
local_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', basedir), 'IARA')
os.makedirs(local_data_dir, exist_ok=True)

SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL',
    'sqlite:///' + os.path.join(local_data_dir, 'iara_database.db')
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'replace-this-secret-in-production')

# small helper used by models default values
def now_date_str():
    return datetime.utcnow().strftime('%Y-%m-%d')
