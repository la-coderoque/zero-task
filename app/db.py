from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import POSTGRES_URL

engine = create_engine(POSTGRES_URL)
Session = sessionmaker(engine)


def save_file(filename, classes):
    statement = 'INSERT INTO markup.files(id, classes) VALUES(:id, :cls)'
    with Session.begin() as session:
        session.execute(statement, {'id': filename, 'cls': classes})


def get_files():
    statement = '''
    SELECT classes, processed FROM markup.files;
    '''
    with Session.begin() as session:
        result = session.execute(statement)
        return result.fetchall()
