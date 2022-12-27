import os
from sqlalchemy.engine import URL

BOT_TOKEN = os.getenv('BOT_TOKEN')
UPLOAD_FOLDER = '/app/upload'

POSTGRES_URL = URL.create(
    'postgresql+asyncpg',
    username=os.getenv('DB_USER'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    port=os.getenv('DB_PORT'),
    password=os.getenv('DB_PASS'),
)
