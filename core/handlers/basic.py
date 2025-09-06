from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from core.utils.db_requests import Request
from core.utils.subscription import check_subscription, get_keyboard
from core.keyboards.inline import ready_keyboard
from core.settings import settings
import data  # файл с участниками рассылки
import logging  # для настройки логгирования

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command('start'))
async def get_start(message: Message, request: Request):  # ответ на команду /start
    try:
        await request.add_data(message.from_user.id, message.from_user.first_name, message.date)

        await message.answer(f"{message.from_user.first_name}, чтобы забрать все полезные материалы"
                             f" из нашей рассылки, подпишись на всех организаторов:\n"
                             f"\n"
                             f"{data.channel1}\n"
                             f"{data.channel2}\n"
                             f"{data.channel3}\n"
                             f"\n"
                             f"\u2705 После подписки нажми ГОТОВО",
                             reply_markup=ready_keyboard)
        logger.info(f"{message.from_user.id} press /start")

    except Exception as e:
        logger.error(f"{message.from_user.id} press /start: {e}")


@router.message(Command('help'))
async def get_help(message: Message):  # ответ на команду /help
    try:
        await message.answer(f"Если нужна помощь, то обращайся к {settings.bots.profile}")
        logger.info(f"{message.from_user.id} press /help")

    except Exception as e:
        logger.error(f"{message.from_user.id} press /help: {e}")


@router.callback_query(F.data == 'ready1')
async def click_button(call: CallbackQuery, bot: Bot, request: Request):
    try:
        not_subscription = await check_subscription(bot, call.from_user.id)
        not_subs_keyboard = await get_keyboard(not_subscription)

        if len(not_subscription) == 0:
            await request.update_status('ready', call.from_user.id)
            await call.message.answer('Молодец, жди подарок!')
            await call.answer()  # чтобы на кнопке не горели часики
            logger.info(f"{call.from_user.id} subscription True")
        else:
            await call.message.answer(f"Для получения подарка надо подписаться еще на каналы\n"
                                      f"\u2705 После подписки нажми кнопку\n"
                                      f" ГОТОВО",
                                      reply_markup=not_subs_keyboard)
            await call.answer()  # чтобы на кнопке не горели часики
            logger.info(f"{call.from_user.id} subscription False")

    except Exception as e:
        logger.error(f"Error READY_button: {e}")
