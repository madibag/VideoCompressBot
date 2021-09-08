#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Madiba E T

# the logging things
import logging
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)


import asyncio
import os
import time
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


async def convert_video(video_file, output_directory,Data):
    # https://stackoverflow.com/a/13891070/4723940

    #https://superuser.com/questions/714804/converting-video-from-1080p-to-720p-with-smallest-quality-loss-using-ffmpeg

    out_put_file_name = output_directory + "/" + str(round(time.time())) + ".mkv"
    file_genertor_command = [
        "ffmpeg",
        "-i",
        video_file,
        "-c:v",
        "libx265",
        "-c:a",
        "copy",
        "-vf",
        f"scale=-1:{Data}",
        "-async",
        "1",
        "-strict",
        "-2",
        out_put_file_name
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()

    process.terminate()

    #os.remove(video_file)
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        print(e_response)
        return None


