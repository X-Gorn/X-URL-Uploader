import motor.motor_asyncio
import asyncio
import logging
import inspect
from pyrogram import Client, enums
from aiohttp import ClientSession
from typing import Union
from .config import Config
from .translation import Translation
from .functions.filters import Filter


class BotClient(Client):

    def __init__(self):
        self.filters = Filter
        self.sleep = asyncio.sleep
        self.session: ClientSession = None
        self.config = Config
        self.translation = Translation
        self.database: Union[motor.motor_asyncio.AsyncIOMotorClient, None] = motor.motor_asyncio.AsyncIOMotorClient(self.config.DATABASE_URL) if self.config.DATABASE_URL else None
        self.custom_thumbnail = {}
        self.custom_caption = {}
        self.bot: Client = Client(
            name='X-URL-Uploader',
            api_id=self.config.APP_ID,
            api_hash=self.config.API_HASH,
            bot_token=self.config.BOT_TOKEN,
            plugins={'root': 'Bot.plugins'},
            parse_mode=enums.ParseMode.HTML
        )

    async def startup(self):
        await self.bot.start()

    @property
    def logger(self) -> logging.Logger:
        module = inspect.getmodule(inspect.stack()[1][0])
        module_name = module.__name__ if module else '__main__'
        return logging.getLogger(module_name)


client = BotClient()
