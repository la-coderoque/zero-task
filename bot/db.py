from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


def get_async_engine(url: URL | str) -> AsyncEngine:
    return create_async_engine(
        url=url,
        echo=True,
        encoding='utf-8',
    )


def get_session_maker(engine: AsyncEngine) -> sessionmaker:
    return sessionmaker(engine, class_=AsyncSession)


async def get_tg_user(user_id: int, session_maker: sessionmaker):
    statement = 'SELECT id, authorized_as FROM markup.tg_users WHERE id = (:id);'
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(statement, {'id': user_id})
            return result.one_or_none()


async def new_tg_user(user_id: int, session_maker: sessionmaker):
    statement = 'INSERT INTO markup.tg_users(id) VALUES(:id);'
    async with session_maker() as session:
        async with session.begin():
            await session.execute(statement, {'id': user_id})


async def register_user(username: str, password: str, session_maker: sessionmaker):
    statement = '''
    INSERT INTO markup.users(username, password)
    VALUES(:uname, :pswd);
    '''
    async with session_maker() as session:
        async with session.begin():
            await session.execute(statement, {'uname': username, 'pswd': password})

async def login_user(user_id: int, username: str, session_maker: sessionmaker):
    statement = '''
    UPDATE markup.tg_users
    SET authorized_as = :uname
    WHERE id = :id;
    '''
    async with session_maker() as session:
        async with session.begin():
            await session.execute(statement, {'uname': username, 'id': user_id})


async def logout_user(user_id: int, session_maker: sessionmaker):
    statement = '''
    UPDATE markup.tg_users
    SET authorized_as = null
    WHERE id = :id;
    '''
    async with session_maker() as session:
        async with session.begin():
            await session.execute(statement, {'id': user_id})


async def get_user(username: str, session_maker: sessionmaker):
    statement = 'SELECT username, password FROM markup.users WHERE username = :uname;'
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(statement, {'uname': username})
            return result.one_or_none()


async def get_current_user_file(username: str, session_maker: sessionmaker):
    statement = '''
    SELECT id, classes
    FROM markup.files
    WHERE username = :uname AND processed is null;
    '''
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(statement, {'uname': username})
            return result.one_or_none()


async def set_current_user_file(file_id: str, username: str, session_maker: sessionmaker):
    statement = '''
    UPDATE markup.files
    SET username = :uname
    WHERE id = :id;
    '''
    async with session_maker() as session:
        async with session.begin():
            await session.execute(statement, {'id': file_id, 'uname': username})


async def set_file_processed(file_id: str, processed: str, session_maker: sessionmaker):
    statement = '''
    UPDATE markup.files
    SET processed = :processed
    WHERE id = :id;
    '''
    async with session_maker() as session:
        async with session.begin():
            await session.execute(statement, {'id': file_id, 'processed': processed})


async def get_unmarked_file(session_maker: sessionmaker):
    statement = '''
    SELECT id, classes
    FROM markup.files
    WHERE processed is null and username is null
    LIMIT 1;
    '''
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(statement)
            return result.one_or_none()
