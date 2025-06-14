import asyncpg
import logging  # для настройки логгирования


class Request:  # экземпляром класса является соединение с БД
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector
        self.logger = logging.getLogger(__name__)

    async def add_data(self, user_id, user_name, date):  # добавляем данные в таблицу datausers
        query = (f"INSERT INTO datausers(user_id, user_name, status, date) "
                 f"VALUES({user_id}, '{user_name}', 'member', '{date}')"
                 f"ON CONFLICT (user_id) DO UPDATE SET user_name = '{user_name}', status = 'member'")
        await self.connector.execute(query)

    async def update_status(self, status, user_id):  # обновление статуса
        query = f"UPDATE datausers SET status = '{status}' WHERE user_id = {user_id}"
        await self.connector.execute(query)

    async def select_member(self, status) -> list:  # получение списка пользователей с конкретным статусом
        query = f"SELECT user_id FROM datausers WHERE status  = '{status}'"
        return await self.connector.fetch(query)

    async def update_default_status(self):  # возвращает всем пользователям статус default
        query = f"UPDATE datausers SET status = 'default' WHERE status != 'blocked'"
        await self.connector.execute(query)
        self.logger.info(f"Update default status")
