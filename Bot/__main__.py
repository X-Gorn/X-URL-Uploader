import os
from . import client
from aiohttp import ClientSession
from pyrogram import idle


async def main():
    await client.startup()
    await client.bot.set_bot_commands(client.config.BOT_COMMANDS)
    session = ClientSession()
    client.session = session
    await idle()


if __name__ == '__main__':
    if not os.path.isdir(client.config.DOWNLOAD_LOCATION):
        os.makedirs(client.config.DOWNLOAD_LOCATION)
    client.run(main())
