import traceback
from .. import client
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, Forbidden, BadRequest


@Client.on_message(filters.private & filters.command('broadcast') & filters.reply & client.filters.database & filters.user(users=client.config.OWNER_ID))
async def broadcast(bot: Client, update: Message):
    message = await update.reply(text='Broadcast started...')
    async for user in client.database.xurluploader.users.find({}):
        try:
            await update.reply_to_message.copy(user['id'])
        except FloodWait as e:
            await client.sleep(e.value)
            await update.reply_to_message.copy(user['id'])
        except Forbidden:
            client.logger.warning(
                'Broadcast: Forbidden - {}'.format(user['id']))
        except BadRequest:
            client.logger.warning(
                'Broadcast: BadRequest - {}'.format(user['id']))
        except Exception:
            client.logger.warning(traceback.format_exc())
    await message.edit(text='Broadcast done.')


@Client.on_message(filters.private & filters.command('broadcast') & ~filters.reply & client.filters.database & filters.user(users=client.config.OWNER_ID))
async def broadcast_no_reply(bot: Client, update: Message):
    await update.reply('Reply to a message.')


@Client.on_message(filters.private & filters.command('ban') & client.filters.database & filters.user(users=client.config.OWNER_ID))
async def ban(bot: Client, update: Message):
    try:
        user_id = int(update.command[1])
    except IndexError:
        await update.reply('User ID not detected.\n\nExample: /ban 12345')
    except ValueError:
        await update.reply('ID should be an integer.\n\nExample: /ban 12345')
    else:
        result = await client.database.xurluploader.users.update_one({'id': user_id}, {'$set': {'banned': True}})
        if result.raw_result['updatedExisting']:
            await update.reply('User Banned')
        else:
            await update.reply('User ID is not exist in database.')


@Client.on_message(filters.private & filters.command('unban') & client.filters.database & filters.user(users=client.config.OWNER_ID))
async def unban(bot: Client, update: Message):
    try:
        user_id = int(update.command[1])
    except IndexError:
        await update.reply('User ID not detected.\n\nExample: /unban 12345')
    except ValueError:
        await update.reply('ID should be an integer.\n\nExample: /unban 12345')
    else:
        result = await client.database.xurluploader.users.update_one({'id': user_id}, {'$set': {'banned': False}})
        if result.raw_result['updatedExisting']:
            await update.reply('User Unbanned')
        else:
            await update.reply('User ID is not exist in database.')
