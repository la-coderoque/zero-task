import os
from sqlalchemy.engine import URL

ADMIN_LOGIN = os.getenv('ADMIN_LOGIN')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

UPLOAD_FOLDER = '/app/upload'

POSTGRES_URL = URL.create(
    'postgresql+psycopg2',
    username=os.getenv('DB_USER'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    port=os.getenv('DB_PORT'),
    password=os.getenv('DB_PASS'),
)
