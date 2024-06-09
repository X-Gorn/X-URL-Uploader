from pyrogram import filters
from .. import client


async def database_filter(_, __, ___):
    return True if client.database else False


class Filter(object):

    database = filters.create(database_filter)

    auth_users = filters.incoming & filters.user(
        client.config.AUTH_USERS) if client.config.AUTH_USERS else filters.incoming
