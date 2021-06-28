import os, shutil, glob
from pyrogram import Client, filters
from helper_funcs.helper import get_text, run_cmd


@Client.on_message(filters.command('zdl'))
async def _zippydl(bot, update):
    zurl = get_text(update)
    zs_dir = f'./zippyshare/{update.from_user.id}/
    if os.path.isdir(zs_dir)
        pass
    else:
        os.makedirs(zs_dir)
    cmd = f'zippyshare-dl {zurl} --output-folder {zs_dir}'
    await run_cmd(cmd)
    for file in glob.glob(f'{zs_dir}*'):
        await bot.send_document(update.chat.id, file, caption='@xurluploaderbot')
