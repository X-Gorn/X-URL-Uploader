from pyrogram import filters
from .. import client


def database_filter(_, __, ___):
    return True if client.database else False


database = filters.create(database_filter)
