#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K


import asyncio
import os
import time
import re
from datetime import datetime
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from pyrogram import Client, enums
from pyrogram.types import CallbackQuery
from .display_progress import progress_for_pyrogram
from .download import download_coroutine
from .. import client


# Detect URLS using Regex. https://stackoverflow.com/a/3809435/15561455
URL_REGEX = re.compile(
    pattern=r'(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*))(.*)?')


async def ddl_call_back(bot: Client, update: CallbackQuery):
    tg_send_type, _, __ = update.data.split("=")
    thumb_image_path = client.config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + ".jpg"
    if client.custom_thumbnail.get(update.from_user.id):
        thumb_image_path = client.custom_thumbnail.get(update.from_user.id)
    regex = URL_REGEX.search(update.message.reply_to_message.text)
    youtube_dl_url = regex.group(1)
    text = regex.group(2) if regex.group(2) else ""
    if "|" in text:
        url_parts = youtube_dl_url.split("|")
        if len(url_parts) == 2:
            _ = url_parts[0]
            custom_file_name = url_parts[1]
        else:
            for entity in update.message.reply_to_message.entities:
                if entity.type == enums.MessageEntityType.TEXT_LINK:
                    youtube_dl_url = entity.url
                elif entity.type == enums.MessageEntityType.URL:
                    o = entity.offset
                    l = entity.length
                    youtube_dl_url = youtube_dl_url[o:o + l]
        if youtube_dl_url is not None:
            youtube_dl_url = youtube_dl_url.strip()
        if custom_file_name is not None:
            custom_file_name = custom_file_name.strip()
    else:
        custom_file_name = os.path.basename(youtube_dl_url)
        for entity in update.message.reply_to_message.entities:
            if entity.type == enums.MessageEntityType.TEXT_LINK:
                youtube_dl_url = entity.url
            elif entity.type == enums.MessageEntityType.URL:
                o = entity.offset
                l = entity.length
                youtube_dl_url = youtube_dl_url[o:o + l]
    description = client.custom_caption.get(update.from_user.id) if client.custom_caption.get(update.from_user.id) else client.translation.CUSTOM_CAPTION_UL_FILE.format(
        bot.me.mention)
    start = datetime.now()
    await bot.edit_message_text(
        text=client.translation.DOWNLOAD_START,
        chat_id=update.message.chat.id,
        message_id=update.message.id
    )
    tmp_directory_for_each_user = client.config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user + "/" + custom_file_name
    c_time = time.time()
    try:
        await download_coroutine(
            bot,
            client.session,
            youtube_dl_url,
            download_directory,
            update.message.chat.id,
            update.message.id,
            c_time,
            None
        )
    except asyncio.TimeoutError:
        await bot.edit_message_text(
            text=client.translation.SLOW_URL_DECED,
            chat_id=update.message.chat.id,
            message_id=update.message.id
        )
        return False
    if os.path.exists(download_directory):
        end_one = datetime.now()
        await bot.edit_message_text(
            text=client.translation.UPLOAD_START,
            chat_id=update.message.chat.id,
            message_id=update.message.id
        )
        file_size = client.config.TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError as exc:
            download_directory = os.path.splitext(
                download_directory)[0] + "." + "mkv"
            # https://stackoverflow.com/a/678242/4723940
            file_size = os.stat(download_directory).st_size
        if file_size > client.config.TG_MAX_FILE_SIZE:
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                text=client.translation.RCHD_TG_API_LIMIT,
                message_id=update.message.id
            )
        else:
            # get the correct width, height, and duration for videos greater than 10MB
            # ref: message from @BotSupport
            width = 0
            height = 0
            duration = 0
            if tg_send_type != "file":
                metadata = extractMetadata(createParser(download_directory))
                if metadata is not None:
                    if metadata.has("duration"):
                        duration = metadata.get('duration').seconds
            # get the correct width, height, and duration for videos greater than 10MB
            if os.path.exists(thumb_image_path):
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                if tg_send_type == "vm":
                    height = width
                # resize image
                # ref: https://t.me/PyrogramChat/44663
                # https://stackoverflow.com/a/21669827/4723940
                Image.open(thumb_image_path).convert(
                    "RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                # https://stackoverflow.com/a/37631799/4723940
                # img.thumbnail((90, 90))
                if tg_send_type == "file":
                    img.resize((320, height))
                else:
                    img.resize((90, height))
                img.save(thumb_image_path, "JPEG")
                # https://pillow.readthedocs.io/en/3.1.x/reference/Image.html#create-thumbnails
            else:
                thumb_image_path = None
            start_time = time.time()
            # try to upload file
            if tg_send_type == "audio":
                media = await bot.send_audio(
                    chat_id=update.message.chat.id,
                    audio=download_directory,
                    caption=description,
                    duration=duration,
                    # performer=response_json["uploader"],
                    # title=response_json["title"],
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client.translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
            elif tg_send_type == "file":
                media = await bot.send_document(
                    chat_id=update.message.chat.id,
                    document=download_directory,
                    thumb=thumb_image_path,
                    caption=description,
                    # reply_markup=reply_markup,
                    reply_to_message_id=update.message.reply_to_message.id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client.translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
            elif tg_send_type == "vm":
                media = await bot.send_video_note(
                    chat_id=update.message.chat.id,
                    video_note=download_directory,
                    duration=duration,
                    length=width,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client.translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
            elif tg_send_type == "video":
                media = await bot.send_video(
                    chat_id=update.message.chat.id,
                    video=download_directory,
                    caption=description,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client.translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
            end_two = datetime.now()
            if client.config.DUMP_ID:
                await media.copy(client.config.DUMP_ID, caption=f'User Name: {update.from_user.first_name}\nUser ID: {update.from_user.id}\nLink: {youtube_dl_url}')
            os.remove(download_directory)
            if not client.custom_thumbnail.get(update.from_user.id):
                os.remove(thumb_image_path)
            time_taken_for_download = (end_one - start).seconds
            time_taken_for_upload = (end_two - end_one).seconds
            await bot.edit_message_text(
                text=client.translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(
                    time_taken_for_download, time_taken_for_upload),
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                disable_web_page_preview=True
            )
    else:
        await bot.edit_message_text(
            text=client.translation.NO_VOID_FORMAT_FOUND.format(
                "Incorrect Link"),
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            disable_web_page_preview=True
        )
