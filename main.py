from aiogram import Bot, Dispatcher
import asyncio  # для асинхронного запуска бота
import asyncpg  # для подключения к БД
import logging  # для настройки логгирования
from pathlib import Path
from logging.handlers import RotatingFileHandler  # для ротации логов
from core.settings import settings, param
from core.handlers.basic import router
from core.middlewares.db_middleware import DbSession
from core.utils.db_requests import Request
from core import admin

Path("logs").mkdir(exist_ok=True)


async def create_pool():  # создадим пул соединений с БД
    return await asyncpg.pool.create_pool(user=param.db.user, password=param.db.password,
                                          database=param.db.database, host=param.db.host, port=param.db.port,
                                          command_timeout=60, max_size=15)


async def start():
    handler = RotatingFileHandler('logs/bot.log', maxBytes=2 * 1024 * 1024, backupCount=3)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[handler,  # запись в файл
                                  logging.StreamHandler()])             # вывод в консоль

    bot = Bot(settings.bots.bot_token)  # создает объект класса бот
    pool_connect = await create_pool()
    scheduler_request = Request(pool_connect)  # создает один экземпляр Request специально для scheduler
    dp = Dispatcher()  # создает объект класса диспетчер

    # регистрируем middleware
    dp.update.middleware.register(DbSession(pool_connect))  # создает новый экземпляр Request для каждого update

    dp.include_router(router)  # регистрируем роутеры

    @dp.startup()  # регистрация функции, которая вызывается при статрте бота
    async def on_startup():
        await admin.start_bot(bot, scheduler_request)

    @dp.shutdown()  # регистрация функции, которая вызывается при остановке бота
    async def on_shutdown():
        await admin.stop_bot(bot, scheduler_request)

    try:
        # удаляет все обновления, которые произошли после последнего завершения бота
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)  # запустим поллинг
    finally:
        await bot.session.close()  # закрыть сессию бота

if __name__ == '__main__':
    asyncio.run(start())
