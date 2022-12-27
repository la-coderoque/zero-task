from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.orm import sessionmaker

from db import get_tg_user, new_tg_user


async def _check_or_write(event: Message, data: Dict[str, Any]):
    session_maker: sessionmaker = data['session_maker']
    user_id = event.from_user.id
    user = await get_tg_user(user_id, session_maker)
    if not user:
        await new_tg_user(user_id, session_maker)


class NewUser(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message) and event.chat.type == 'private':
            await _check_or_write(event, data)
        return await handler(event, data)
