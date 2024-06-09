from pyrogram import Client, enums
from aiohttp import ClientSession
from .config import Config
from .translation import Translation


class BotClient(Client):

    def __init__(self):
        self.session: ClientSession = None
        self.config = Config
        self.translation = Translation
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


client = BotClient()
