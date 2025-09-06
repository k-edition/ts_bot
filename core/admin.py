from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # планировщик задач
from core.utils.commands import set_commands
from core.settings import settings
from core.handlers import scheduler
from core.utils.db_requests import Request
import data  # файл с участниками рассылки
from datetime import datetime, timedelta

apscheduler = AsyncIOScheduler(timezone='Europe/Moscow')  # объект расписания


async def start_bot(bot: Bot, request: Request):
    await set_commands(bot)
    await bot.send_message(settings.bots.admin_id, text='Бот запущен!')  # уведомление админу о старте бота

    apscheduler.add_job(scheduler.check_remember, trigger='date',
                        run_date=datetime.now() + timedelta(seconds=data.time_check_remember),
                        kwargs={'bot': bot, 'chat_id': settings.bots.admin_id, 'request': request})

    apscheduler.add_job(scheduler.remember, trigger='date',
                        run_date=datetime.now() + timedelta(seconds=data.time_remember),
                        kwargs={'bot': bot, 'chat_id': settings.bots.admin_id, 'request': request})

    apscheduler.add_job(scheduler.delivery, trigger='date',
                        run_date=datetime.now() + timedelta(seconds=data.time_delivery),
                        kwargs={'bot': bot, 'chat_id': settings.bots.admin_id, 'request': request})

    apscheduler.start()  # запуск планировщика задач


async def stop_bot(bot: Bot, request: Request):
    await bot.send_message(settings.bots.admin_id, text='Бот остановлен!')  # уведомление админу об остановке бота
    apscheduler.shutdown(wait=False)  # остановка планировщика задач
    await request.update_default_status()
