import os
import logging
from pyrogram.client.filters import filters
from pyrogram.client.types import InlineKeyboardButton, InlineKeyboardMarkup
from translation import START_TEXT

logger = logging.getLogger(__name__)


@pyrogram.Client.on_message(filters.command('start'))
async def start(bot, message):
    """Start command handler"""
    buttons = [[
        InlineKeyboardButton('Channel', url='https://t.me/xTeamBots'),
        InlineKeyboardButton('Master', url='https://t.me/xgorn'),
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply(START_TEXT, reply_markup=reply_markup)


