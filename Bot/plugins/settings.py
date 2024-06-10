import os
from .. import client
from pyrogram import Client, filters
from pyrogram.types import Message
from ..functions.helper import URL_REGEX, run_cmd
from ..functions.filters import Filter


async def reply_to_photo_filter(_, __, m: Message):
    return bool(m.reply_to_message.photo)


async def no_args_filter(_, __, m: Message):
    return True if len(m.command) == 1 else False


@Client.on_message(filters.private & filters.command('caption') & Filter.auth_users)
async def custom_caption(bot: Client, update: Message):
    if client.database:
        user = await client.database.xurluploader.users.find_one({'id': update.from_user.id})
        if not user:
            user = await client.database.xurluploader.users.insert_one({'id': update.from_user.id, 'banned': False})
        else:
            if user.get('banned'):
                return await update.reply('You are banned.')
    try:
        caption = update.text.html.split(' ', 1)[1]
        await update.reply(text='Custom caption updated.')
    except IndexError:
        if not client.custom_caption.get(update.from_user.id):
            return await update.reply(
                text='Ex: `/caption abcdfgh`'
            )
        caption = ""
        await update.reply(text='Custom caption cleared.')
    client.custom_caption[update.from_user.id] = caption


@Client.on_message(filters.private & filters.command('thumbnail') & ~filters.reply & (filters.regex(pattern=URL_REGEX) | filters.create(no_args_filter)) & Filter.auth_users)
async def custom_thumbnail(bot: Client, update: Message):
    if client.database:
        user = await client.database.xurluploader.users.find_one({'id': update.from_user.id})
        if not user:
            user = await client.database.xurluploader.users.insert_one({'id': update.from_user.id, 'banned': False})
        else:
            if user.get('banned'):
                return await update.reply('You are banned.')
    try:
        thumbnail = f'{client.config.DOWNLOAD_LOCATION}/{update.from_user.id}.jpg'
        command = 'wget -O "{}" "{}"'.format(
            thumbnail, URL_REGEX.findall(update.text)[0])
        await run_cmd(command)
        await update.reply(text='Custom thumbnail updated.')
    except IndexError:
        if not client.custom_thumbnail.get(update.from_user.id):
            return await update.reply(
                text='Reply to a photo or `/thumbnail https.....jpg`'
            )
        if os.path.isfile(client.custom_thumbnail[update.from_user.id]):
            os.remove(client.custom_thumbnail[update.from_user.id])
        thumbnail = None
        await update.reply(text='Custom thumbnail cleared.')
    client.custom_thumbnail[update.from_user.id] = thumbnail


@Client.on_message(filters.private & filters.command('thumbnail') & filters.reply & filters.create(reply_to_photo_filter) & Filter.auth_users)
async def custom_thumbnail_reply(bot: Client, update: Message):
    if client.database:
        user = await client.database.xurluploader.users.find_one({'id': update.from_user.id})
        if not user:
            user = await client.database.xurluploader.users.insert_one({'id': update.from_user.id, 'banned': False})
        else:
            if user.get('banned'):
                return await update.reply('You are banned.')
    client.custom_thumbnail[update.from_user.id] = await update.reply_to_message.download(file_name=f'{client.config.DOWNLOAD_LOCATION}/{update.from_user.id}.jpg')
    await update.reply(text='Custom thumbnail updated.')
