# X-Noid

import lk21, requests, urllib.parse, filetype, tldextract
from pyrogram import Client, filters
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from helper_funcs.display_progress import progress_for_pyrogram
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from translation import Translation


@Client.on_message(filters.regex(pattern=".*http.*"))
async def _lk21(bot, update):
    if update.from_user.id in Config.BANNED_USERS:
        await update.reply_text("You are BANNED")
        return
    update_channel = Config.UPDATE_CHANNEL
    if update_channel:
        try:
            user = await bot.get_chat_member(update_channel, update.chat.id)
            if user.status == "kicked":
               await update.reply_text("Sorry, You are **BANNED**")
               return
        except UserNotParticipant:
            #await update.reply_text(f"Join @{update_channel} To Use Me")
            await update.reply_text(
                text="**Join My Updates Channel to use Me**",
                reply_markup=InlineKeyboardMarkup([
                    [ InlineKeyboardButton(text="Join My Updates Channel", url=f"https://t.me/{update_channel}")]
              ])
            )
            return
        except Exception:
            await update.reply_text("Something Wrong. Contact @xgorn")
            return
    url = update.text
    file_name = None
    folder = f'./lk21/{update.from_user.id}/'
    bypass = ['zippyshare', 'hxfile', 'mediafire', 'anonfiles']
    ext = tldextract.extract(url)
    if ext.domain in bypass:
        pablo = await update.reply_text('LK21 link detected')
        time.sleep(2.5)
        if os.path.isdir(folder):
            await update.reply_text("Don't spam, wait till your previous task done.")
            await pablo.delete()
            return
        os.makedirs(folder)
        await pablo.edit_text('Downloading...')
        bypasser = lk21.Bypass()
        xurl = bypasser.bypass_url(url)
        if ' | ' in url:
            url_parts = url.split(' | ')
            url = url_parts[0]
            file_name = url_parts[1]
        else:
            if xurl.find('/'):
                urlname = xurl.rsplit('/', 1)[1]
            file_name = urllib.parse.unquote(urlname)
        dldir = f'{folder}{file_name}'
        r = requests.get(xurl, allow_redirects=True)
        open(dldir, 'wb').write(r.content)
        try:
            file = filetype.guess(dldir)
            xfiletype = file.mime
        except AttributeError:
            xfiletype = file_name
        if xfiletype in ['video/mp4', 'video/x-matroska', 'video/webm', 'audio/mpeg']:
            metadata = extractMetadata(createParser(dldir))
            if metadata is not None:
                if metadata.has("duration"):
                    duration = metadata.get('duration').seconds
        start_time = time.time()
        if xfiletype in ['video/mp4', 'video/x-matroska', 'video/webm']:
            video = await bot.send_video(
                chat_id=update.chat.id,
                video=dldir,
                caption=file_name,
                duration=duration,
                reply_to_message_id=update.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    update,
                    start_time
                )
            )
            video_f = await video.forward(Config.LOG_CHANNEL)
            await video_f.reply_text("Name: " + str(update.from_user.first_name) + "\nUser ID: " + "<code>" + str(update.from_user.id) + "</code>" + '\nLK21 URL: ' + url)
        elif xfiletype == 'audio/mpeg':
            audio = await bot.send_audio(
                chat_id=update.chat.id,
                audio=dldir,
                caption=file_name,
                duration=duration,
                reply_to_message_id=update.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    update,
                    start_time
                )
            )
            audio_f = await audio.forward(Config.LOG_CHANNEL)
            await audio_f.reply_text("Name: " + str(update.from_user.first_name) + "\nUser ID: " + "<code>" + str(update.from_user.id) + "</code>" + '\nLK21 URL: ' + url)
        else:
            doc = await bot.send_document(
                chat_id=update.chat.id,
                document=dldir,
                caption=file_name,
                reply_to_message_id=update.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    update,
                    start_time
                )
            )
            doc_f = await doc.forward(Config.LOG_CHANNEL)
            await doc_f.reply_text("Name: " + str(update.from_user.first_name) + "\nUser ID: " + "<code>" + str(update.from_user.id) + "</code>" + '\nLK21 URL: ' + url)
        await pablo.delete()
        shutil.rmtree(folder)
