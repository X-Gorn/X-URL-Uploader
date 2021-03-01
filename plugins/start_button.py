#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import asyncio
import json
import math
import os
import shutil
import time
from datetime import datetime

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from helper_funcs.chat_base import TRChatBase
from pyrogram.client import Client 
from pyrogram.client.filters import filters
from pyrogram.client.types import InlineKeyboardButton, InlineKeyboardMarkup
from translation import Translation


@pyrogram.Client.on_message(filters.command('start'))
async def start(bot, message):
    """Start command handler"""
    buttons = [[
        InlineKeyboardButton('Channel', url='https://t.me/xTeamBots'),
        InlineKeyboardButton('Master', url='https://t.me/xgorn'),
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply(Translation.START_TEXT, reply_markup=reply_markup)
