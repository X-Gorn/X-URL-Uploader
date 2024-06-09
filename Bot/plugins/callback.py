#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K


import re
from ..functions.dl_button import ddl_call_back
from ..functions.youtube_dl_button import youtube_dl_call_back
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery


ytdl_compiler = re.compile(r'^\w+\|\w+\|\w+$')
ddl_compiler = re.compile(r'^\w+=\w+=\w+$')


@Client.on_callback_query(filters.regex(ytdl_compiler))
async def ytdl_handler(bot: Client, callback: CallbackQuery):
    await youtube_dl_call_back(bot, callback)


@Client.on_callback_query(filters.regex(ddl_compiler))
async def ddl_handler(bot: Client, callback: CallbackQuery):
    await ddl_call_back(bot, callback)
