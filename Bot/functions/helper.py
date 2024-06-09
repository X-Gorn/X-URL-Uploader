import shlex
import asyncio
import re
from typing import Tuple


# Detect URLS using Regex. https://stackoverflow.com/a/3809435/15561455
URL_REGEX = re.compile(
    pattern=r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)')


async def run_cmd(cmd) -> Tuple[str, str, int, int]:
    if type(cmd) == str:
        cmd = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )
