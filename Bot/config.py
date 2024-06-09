import os
from pyrogram.types import BotCommand


class Config(object):
    BOT_COMMANDS = [
        BotCommand('start', 'start bot'),
        BotCommand('help', 'help message'),
        BotCommand('caption', 'custom caption'),
        BotCommand('thumbnail', 'custom thumbnail')
    ]

    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

    APP_ID = int(os.environ.get("APP_ID", 12345))
    API_HASH = os.environ.get("API_HASH")

    # Authorized User IDS
    AUTH_USERS = [int(id) for id in os.environ.get(
        "AUTH_USERS", "").split()] if os.environ.get("AUTH_USERS", None) else None

    # the download location, where the HTTP Server runs
    DOWNLOAD_LOCATION = "./DOWNLOADS"

    # Telegram maximum file upload size
    MAX_FILE_SIZE = 50000000
    TG_MAX_FILE_SIZE = 2097152000
    FREE_USER_MAX_FILE_SIZE = 50000000

    # chunk size that should be used with requests
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 128))

    # default thumbnail to be used in the videos
    DEF_THUMB_NAIL_VID_S = os.environ.get("DEF_THUMB_NAIL_VID_S", "")

    # proxy for accessing youtube-dl in GeoRestricted Areas
    # Get your own proxy from https://github.com/rg3/youtube-dl/issues/1091#issuecomment-230163061
    HTTP_PROXY = os.environ.get("HTTP_PROXY", "")

    # maximum message length in Telegram
    MAX_MESSAGE_LENGTH = 4096

    # set timeout for subprocess
    PROCESS_MAX_TIMEOUT = 3600

    # watermark file
    DEF_WATER_MARK_FILE = ""
