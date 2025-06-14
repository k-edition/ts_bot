from environs import Env
from dataclasses import dataclass


@dataclass
class Bots:  # класс исползуется как контейнер для хранения значений
    bot_token: str  # аннотации типов, показывают какие типы данных ожидаются
    admin_id: int
    profile: str


@dataclass
class DataBase:
    user: str
    password: str
    database: str
    host: str
    port: int


@dataclass
class Settings:
    bots: Bots


@dataclass
class Param:
    db: DataBase


def get_settings(path: str):  # path это строка - путь к файлу, содержащему переменные окружения
    env = Env()  # класс, который отвечает за чтение переменных окружения из указанного файла
    env.read_env(path)  # метод загружает переменные из файла

    # возврат объекта класса Settings
    return Settings(bots=Bots(bot_token=env.str('BOT_TOKEN'), admin_id=env.int('ADMIN_ID'),
                              profile=env.str('PROFILE')))


def get_param(path: str):
    env = Env()
    env.read_env(path)

    return Param(db=DataBase(user=env.str('BD_USER'), password=env.str('BD_PASSWORD'), database=env.str('DATABASE'),
                             host=env.str('BD_HOST'), port=env.int('BD_PORT')))


settings = get_settings('config.py')
param = get_param('config.py')
print(settings)
print(param)
