#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K


from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from .. import client


@Client.on_message(filters.private & filters.command("help") & filters.chat(client.config.AUTH_USERS))
async def help(bot: Client, update: Message):
    await bot.send_message(
        chat_id=update.chat.id,
        text=client.translation.HELP_USER,
        disable_web_page_preview=True,
        reply_to_message_id=update.id
    )


@Client.on_message(filters.private & filters.command("start") & filters.chat(client.config.AUTH_USERS))
async def start(bot: Client, update: Message):
    await bot.send_message(
        chat_id=update.chat.id,
        text=client.translation.START_TEXT.format(update.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Source", url="https://github.com/X-Gorn/X-URL-Uploader"
                    ),
                    InlineKeyboardButton(
                        "Project Channel", url="https://t.me/xTeamBots"),
                ],
                [InlineKeyboardButton("Author", url="https://t.me/xgorn")],
            ]
        ),
        reply_to_message_id=update.id
    )
