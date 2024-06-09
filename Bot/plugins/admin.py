from .. import client
from ..functions import filters as myFilters
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait


@Client.on_message(filters.private & filters.command('broadcast') & filters.reply & myFilters.database & filters.chat(chats=client.config.OWNER_ID))
async def broadcast(bot: Client, update: Message):
    message = await update.reply(text='Broadcast started...')
    for user in client.database.xurluploader.users.find({}):
        try:
            await update.reply_to_message.copy(user['id'])
        except FloodWait as e:
            await client.sleep(e.value)
            await update.reply_to_message.copy(user['id'])
    await message.edit(text='Broadcast done.')


@Client.on_message(filters.private & filters.command('ban') & myFilters.database & filters.chat(chats=client.config.OWNER_ID))
async def ban(bot: Client, update: Message):
    try:
        user_id = int(update.command[1])
    except IndexError:
        await update.reply('User ID not detected.\n\nExample: /ban 12345')
    except ValueError:
        await update.reply('ID should be an integer.\n\nExample: /ban 12345')
    else:
        await client.database.xurluploader.users.update_one({'id': user_id}, {'$set': {'banned': True}})


@Client.on_message(filters.private & filters.command('unban') & myFilters.database & filters.chat(chats=client.config.OWNER_ID))
async def unban(bot: Client, update: Message):
    try:
        user_id = int(update.command[1])
    except IndexError:
        await update.reply('User ID not detected.\n\nExample: /unban 12345')
    except ValueError:
        await update.reply('ID should be an integer.\n\nExample: /unban 12345')
    else:
        await client.database.xurluploader.users.update_one({'id': user_id}, {'$set': {'banned': False}})
