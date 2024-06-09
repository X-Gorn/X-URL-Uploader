#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K


import time
import os
import json
import random
import re
import asyncio
from PIL import Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from pyrogram.types import InputMediaPhoto
from datetime import datetime
from pyrogram import Client, enums
from pyrogram.types import CallbackQuery
from .display_progress import progress_for_pyrogram, humanbytes
from .help_Nekmo_ffmpeg import generate_screen_shots
from .helper import run_cmd, ffmpeg_supported_video_mimetypes
from .. import client


# Detect URLS using Regex. https://stackoverflow.com/a/3809435/15561455
URL_REGEX = re.compile(
    pattern=r'(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*))(.*)?')


async def youtube_dl_call_back(bot: Client, update: CallbackQuery):
    tg_send_type, youtube_dl_format, youtube_dl_ext = update.data.split("|")
    thumb_image_path = client.config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + ".jpg"
    if client.custom_thumbnail.get(update.from_user.id):
        thumb_image_path = client.custom_thumbnail.get(update.from_user.id)
    save_ytdl_json_path = client.config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + ".json"
    try:
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
    except FileNotFoundError:
        await bot.delete_messages(
            chat_id=update.message.chat.id,
            message_ids=update.message.id,
            revoke=True
        )
        return False
    custom_file_name = str(response_json.get("title")) + \
        "_" + youtube_dl_format + "." + youtube_dl_ext
    youtube_dl_username = None
    youtube_dl_password = None
    regex = URL_REGEX.search(update.message.reply_to_message.text)
    youtube_dl_url = regex.group(1)
    text = regex.group(2) if regex.group(2) else ""
    if "|" in text:
        url_parts = text.split("|")
        if len(url_parts) == 2:
            _ = url_parts[0]
            custom_file_name = url_parts[1]
        elif len(url_parts) == 4:
            _ = url_parts[0]
            custom_file_name = url_parts[1]
            youtube_dl_username = url_parts[2]
            youtube_dl_password = url_parts[3]
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
        # https://stackoverflow.com/a/761825/4723940
        if youtube_dl_username is not None:
            youtube_dl_username = youtube_dl_username.strip()
        if youtube_dl_password is not None:
            youtube_dl_password = youtube_dl_password.strip()
    else:
        for entity in update.message.reply_to_message.entities:
            if entity.type == enums.MessageEntityType.TEXT_LINK:
                youtube_dl_url = entity.url
            elif entity.type == enums.MessageEntityType.URL:
                o = entity.offset
                l = entity.length
                youtube_dl_url = youtube_dl_url[o:o + l]
    await bot.edit_message_text(
        text=client.translation.DOWNLOAD_START,
        chat_id=update.message.chat.id,
        message_id=update.message.id
    )
    description = client.translation.CUSTOM_CAPTION_UL_FILE.format(
        bot.me.mention)
    if "fulltitle" in response_json:
        description = response_json["fulltitle"][0:1021]
        # escape Markdown and special characters
    description = client.custom_caption.get(
        update.from_user.id) if client.custom_caption.get(update.from_user.id) else description
    tmp_directory_for_each_user = client.config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user + "/" + custom_file_name
    command_to_exec = []
    if tg_send_type == "audio":
        command_to_exec = [
            "yt-dlp",
            "-c",
            "--max-filesize", str(client.config.TG_MAX_FILE_SIZE),
            "--prefer-ffmpeg",
            "--extract-audio",
            "--audio-format", youtube_dl_ext,
            "--audio-quality", youtube_dl_format,
            youtube_dl_url,
            "-o", download_directory
        ]
    else:
        # command_to_exec = ["youtube-dl", "-f", youtube_dl_format, "--hls-prefer-ffmpeg", "--recode-video", "mp4", "-k", youtube_dl_url, "-o", download_directory]
        minus_f_format = youtube_dl_format
        if "youtu" in youtube_dl_url:
            minus_f_format = youtube_dl_format + "+bestaudio"
        command_to_exec = [
            "yt-dlp",
            "-c",
            "--max-filesize", str(client.config.TG_MAX_FILE_SIZE),
            "--embed-subs",
            "-f", minus_f_format,
            "--hls-prefer-ffmpeg", youtube_dl_url,
            "-o", download_directory
        ]
    if client.config.HTTP_PROXY != "":
        command_to_exec.append("--proxy")
        command_to_exec.append(client.config.HTTP_PROXY)
    if youtube_dl_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(youtube_dl_username)
    if youtube_dl_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(youtube_dl_password)
    command_to_exec.append("--no-warnings")
    start = datetime.now()
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    ad_string_to_replace = "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output."
    if e_response and ad_string_to_replace in e_response:
        error_message = e_response.replace(ad_string_to_replace, "")
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=error_message
        )
        return False
    if t_response:
        # logger.info(t_response)
        os.remove(save_ytdl_json_path)
        end_one = datetime.now()
        time_taken_for_download = (end_one - start).seconds
        file_size = client.config.TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError:
            download_directory = download_directory + "." + "mkv"
            # https://stackoverflow.com/a/678242/4723940
            file_size = os.stat(download_directory).st_size
        if file_size > client.config.TG_MAX_FILE_SIZE:
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                text=client.translation.RCHD_TG_API_LIMIT.format(
                    time_taken_for_download, humanbytes(file_size)),
                message_id=update.message.id
            )
        else:
            is_w_f = False
            images = await generate_screen_shots(
                download_directory,
                tmp_directory_for_each_user,
                is_w_f,
                client.config.DEF_WATER_MARK_FILE,
                300,
                9
            )
            await bot.edit_message_text(
                text=client.translation.UPLOAD_START,
                chat_id=update.message.chat.id,
                message_id=update.message.id
            )
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
            # auto generate thumbnail if not available
            if not os.path.exists(thumb_image_path):
                if client.guess_mime_type(download_directory) in ffmpeg_supported_video_mimetypes:
                    await run_cmd('ffmpeg -ss {} -i "{}" -vframes 1 "{}"'.format(random.randint(0, duration), download_directory, thumb_image_path))
            # get the correct width, height, and duration for videos greater than 10MB
            if os.path.exists(thumb_image_path) and not client.custom_thumbnail.get(update.from_user.id):
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
                    parse_mode=enums.ParseMode.HTML,
                    duration=duration,
                    performer=response_json.get('artist') if response_json.get(
                        'artist') else response_json.get('channel'),
                    title=response_json.get('track') if response_json.get(
                        'track') else response_json.get('title'),
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
                    parse_mode=enums.ParseMode.HTML,
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
                    parse_mode=enums.ParseMode.HTML,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        client.translation.UPLOAD_START,
                        update.message,
                        start_time
                    )
                )
            if client.config.DUMP_ID:
                await media.copy(client.config.DUMP_ID, caption=f'User Name: {update.from_user.first_name}\nUser ID: {update.from_user.id}\nLink: {youtube_dl_url}')
            end_two = datetime.now()
            time_taken_for_upload = (end_two - end_one).seconds
            media_album_p: list[InputMediaPhoto] = []
            if images:
                i = 0
                caption = "@xurluploaderbot"
                for image in images:
                    if os.path.exists(str(image)):
                        if i == 0:
                            media_album_p.append(
                                InputMediaPhoto(
                                    media=image,
                                    caption=caption,
                                    parse_mode=enums.ParseMode.HTML
                                )
                            )
                        else:
                            media_album_p.append(
                                InputMediaPhoto(
                                    media=image
                                )
                            )
                        i = i + 1
                media_group = await bot.send_media_group(
                    chat_id=update.message.chat.id,
                    disable_notification=True,
                    reply_to_message_id=update.message.id,
                    media=media_album_p
                )
                if client.config.DUMP_ID:
                    await bot.copy_media_group(client.config.DUMP_ID, from_chat_id=update.from_user.id, message_id=media_group[0].media_group_id, captions=f'User Name: {update.from_user.first_name}\nUser ID: {update.from_user.id}\nLink: {youtube_dl_url}')
                for photo in media_album_p:
                    os.remove(photo.media)
            os.remove(download_directory)
            if not client.custom_thumbnail.get(update.from_user.id):
                os.remove(thumb_image_path)
            await bot.edit_message_text(
                text=client.translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(
                    time_taken_for_download, time_taken_for_upload),
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                disable_web_page_preview=True
            )
