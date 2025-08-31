from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from core.utils.db_requests import Request
from core.utils.subscription import check_subscription, get_keyboard
from core.keyboards.inline import ready_keyboard
import data  # файл с участниками рассылки
import logging  # для настройки логгирования

logger = logging.getLogger(__name__)


async def check_remember(bot: Bot, chat_id: int, request: Request):
    await bot.send_message(chat_id, f"Проверка подписок у ready")  # уведомление администратору

    try:
        users_check = await request.select_member('ready')  # пользователи со статусом ready
        logger.info(f"Start check for {len(users_check)} users: {users_check}")

        for user in users_check:

            try:
                not_subscription = await check_subscription(bot, user['id'])

                if len(not_subscription) != 0:
                    await request.update_status('member', user['id'])
                    logger.info(f"Has been changed status for user: {user['id']}")

            except Exception as e:
                logger.error(f"Strange things to remember for {user['id']}: {e}")

    except Exception as e:
        logger.critical(f"Epic fail for check_ready: {e}", exc_info=True)


async def remember(bot: Bot, chat_id: int, request: Request):
    await bot.send_message(chat_id, f"Рассылка напоминалок")  # уведомление администратору

    try:
        users_member = await request.select_member('member')  # пользователи со статусом member
        logger.info(f"Start remember for {len(users_member)} users: {users_member}")

        for user in users_member:
            try:
                not_subscription = await check_subscription(bot, user['id'])
                not_subs_keyboard = await get_keyboard(not_subscription)

                if len(not_subscription) != 0:
                    await bot.send_message(user['id'], f"Уже СЕГОДНЯ ты можешь получить БЕСПЛАТНЫЕ материалы.\n"
                                           f"\n"
                                           f"До рассылки осталось два часа! Успей подписаться на каналы.\n"
                                           f"\u2705 Не забудь нажать кнопку ГОТОВО",
                                           reply_markup=not_subs_keyboard)

                else:
                    await bot.send_message(user['id'], f"Ой-ой, ты забыл нажать кнопку ГОТОВО \u2705",
                                                            reply_markup=ready_keyboard)
                    logger.info(f"User {user['id']} has not pressed button Ready")

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
                    await bot.send_message(user['id'], f"Рассылка не поступила, так как ты не подписан"
                                                            f" на всех организаторов")
                    logger.info(f"No delivery for user: {user['id']}")

            except TelegramForbiddenError as e:
                logger.error(f"{user['id']} has blocked our bot:  {e}")
                await request.update_status('blocked', user['id'])

            except Exception as e:
                logger.error(f"Strange things to delivery for {user['id']}: {e} ")

    except Exception as e:
        logger.critical(f"Epic fail for delivery: {e}")
