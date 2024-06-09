import time
import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait
from aiohttp import ClientSession
from typing import Union
from .display_progress import humanbytes, TimeFormatter
from .. import client


async def download_coroutine(bot: Union[Client, None], session: ClientSession, url: str, file_name: str, chat_id: Union[str, int, None], message_id: Union[int, None], start: float, headers: dict):
    downloaded = 0
    display_message = ""
    async with session.get(url, timeout=client.config.PROCESS_MAX_TIMEOUT, headers=headers) as response:
        total_length = int(response.headers.get("Content-Length", 0))
        content_type = response.headers["Content-Type"]
        if "text" in content_type and total_length < 500 and total_length:
            return await response.release()
        if total_length:
            if bot:
                await bot.edit_message_text(
                    chat_id,
                    message_id,
                    text="Initiating Download\nURL: {}\nFile Size: {}".format(
                        url, humanbytes(total_length))
                )
        with open(file_name, "wb") as f_handle:
            while True:
                chunk = await response.content.read(client.config.CHUNK_SIZE)
                if not chunk:
                    break
                f_handle.write(chunk)
                if total_length:
                    downloaded += client.config.CHUNK_SIZE
                    now = time.time()
                    diff = now - start
                    if round(diff % 5.00) == 0 or downloaded == total_length:
                        percentage = downloaded * 100 / total_length
                        speed = downloaded / diff
                        elapsed_time = round(diff) * 1000
                        time_to_completion = round(
                            (total_length - downloaded) / speed) * 1000
                        estimated_total_time = elapsed_time + time_to_completion
                        try:
                            current_message = "Download Status {}%\nURL: {}\nFile Size: {}\nDownloaded: {}\nETA: {}".format(percentage,
                                                                                                                            url, humanbytes(total_length), humanbytes(downloaded), TimeFormatter(estimated_total_time))
                            if current_message != display_message:
                                if bot:
                                    await bot.edit_message_text(
                                        chat_id,
                                        message_id,
                                        text=current_message
                                    )
                                    display_message = current_message
                        except FloodWait:
                            pass
                        except Exception as e:
                            if bot:
                                error = str(e)
                                await bot.edit_message_text(
                                    chat_id,
                                    message_id,
                                    text=f"Error: {error}"
                                )
        if bot:
            try:
                await bot.edit_message_text(
                    chat_id,
                    message_id,
                    text=f"Download Completed."
                )
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await bot.edit_message_text(
                    chat_id,
                    message_id,
                    text=f"Download Completed."
                )
        return await response.release()
