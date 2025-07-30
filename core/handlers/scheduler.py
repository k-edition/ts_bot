from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from core.utils.db_requests import Request
from core.utils.subscription import check_subscription, get_keyboard
import data  # файл с участниками рассылки
import logging  # для настройки логгирования

logger = logging.getLogger(__name__)


async def remember(bot: Bot, chat_id: int, request: Request):
    await bot.send_message(chat_id, f"Рассылка напоминалок")  # уведомление администратору

    try:
        users_member = await request.select_member('member')  # пользователи со статусом member
        logger.info(f"Start remember for {len(users_member)} users: {users_member}")

        for user in users_member:
            try:
                not_subscription = await check_subscription(bot, user['id'])
                not_subs_keyboard = await get_keyboard(not_subscription)

                await bot.send_message(user['id'], f"Уже СЕГОДНЯ ты можешь получить БЕСПЛАТНЫЕ материалы.\n"
                                       f"\n"
                                       f"До рассылки осталось два часа! Успей подписаться на каналы.\n"
                                       f"\u2705 Не забудь нажать кнопку ГОТОВО",
                                       reply_markup=not_subs_keyboard)

            except TelegramForbiddenError as e:
                logger.error(f"{user['id']} has blocked our bot:  {e}")
                await request.update_status('blocked', user['id'])

            except Exception as e:
                logger.error(f"Strange things to remember for {user['id']}: {e}")

    except Exception as e:
        logger.critical(f"Epic fail for remember: {e}", exc_info=True)


async def delivery(bot: Bot, chat_id: int, request: Request):
    await bot.send_message(chat_id, f"Рассылка материалов")  # уведомление администратору

    try:
        users_ready = await request.select_member('ready')  # пользователи со статусом ready
        logger.info(f"Start delivery for {len(users_ready)} users: {users_ready}")

        for user in users_ready:
            try:
                not_subscription = await check_subscription(bot, user['id'])
                if len(not_subscription) == 0:
                    await bot.send_message(user['id'], f"Привет, спасибо за участие в рассылке!\n"
                                                            f"Материалы можно скачать по этой ссылке:\n{data.link}")
                else:
                    await bot.send_message(user['id'], f"Ты не подписан на всех организаторов")

            except TelegramForbiddenError as e:
                logger.error(f"{user['id']} has blocked our bot:  {e}")
                await request.update_status('blocked', user['id'])

            except Exception as e:
                logger.error(f"Strange things to delivery for {user['id']}: {e} ")

        await request.update_default_status()

    except Exception as e:
        logger.critical(f"Epic fail for delivery: {e}")
