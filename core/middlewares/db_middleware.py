from aiogram import BaseMiddleware
from typing import Dict, Any, Callable, Awaitable
import asyncpg
from aiogram.types import TelegramObject
from core.utils.db_requests import Request


class DbSession(BaseMiddleware):
    def __init__(self, connector: asyncpg.pool.Pool):  # передаем в конструктор соединение в БД
        super().__init__()
        self.connector = connector

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with self.connector.acquire() as connect:  # открываем соединение с БД
            data['request'] = Request(connect)  # передаем экземпляр класса Request в словарь data
            return await handler(event, data)  # передаем экземпляр класса Request и TelegramObject в хендлер
