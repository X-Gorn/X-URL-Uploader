from .. import client
from ..functions import filters as myFilters
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait


@Client.on_message(filters.private & filters.command('broadcast') & filters.reply & myFilters.database)
async def broadcast(bot: Client, update: Message):
    message = await update.reply(text='Broadcast started...')
    for user in client.database.xurluploader.users.find({}):
        try:
            await update.reply_to_message.copy(user['id'])
        except FloodWait as e:
            await client.sleep(e.value)
            await update.reply_to_message.copy(user['id'])
    await message.edit(text='Broadcast done.')