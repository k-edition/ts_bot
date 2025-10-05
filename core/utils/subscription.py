from aiogram.types import ChatMember  # для определения статуса пользователя в канале
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton  # для создания клавиатуры
import data  # файл с участниками рассылки
import logging  # для настройки логгирования

logger = logging.getLogger(__name__)


async def check_status(chat_member: ChatMember) -> bool:  # проверка статуса пользователя на канале
    logger.info(f"{chat_member.status}")
    return chat_member.status in ['member', 'creator', 'administrator', 'restricted']


async def check_subscription(bot, user_id) -> list[str]:  # получение списка каналов без подписки

    not_subscription = []

    for channel in data.channels_list:

        chat_member = await bot.get_chat_member(chat_id=channel, user_id=user_id)

        if not await check_status(chat_member):
            not_subscription.append(channel)

    return not_subscription


async def get_keyboard(not_subscription):  # создание динамической клавиатуры
    buttons = []
    for channel in not_subscription:
        buttons.append([
            InlineKeyboardButton(text=f"{channel}",
                                 url=f"{data.channels_list[channel]}")
        ])
    buttons.append([
            InlineKeyboardButton(text='ГОТОВО',
                                 callback_data='ready1')
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
