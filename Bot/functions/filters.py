from pyrogram import filters
from .. import client


async def database_filter(_, __, ___):
    return True if client.database else False


database = filters.create(database_filter)
