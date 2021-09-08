#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Madiba E T

# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import time
import aiohttp

# the secret configuration specific things
if bool(os.environ.get("ENV", False)):
    from config import Config
else:
    from sample_config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from helper_funcs.display_progress import progress_for_pyrogram
from helper_funcs.help_Nekmo_ffmpeg import convert_video

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser



@pyrogram.Client.on_message(pyrogram.filters.command(["compress"]))
async def convert(bot, update):

    if update.from_user.id not in Config.AUTH_USERS:
        await update.message.delete()
        return
    saved_file_path = Config.DOWNLOAD_LOCATION + "/" + str(round(time.time())) + ".FFMpegRoBot.mkv"
    if not os.path.exists(saved_file_path):
        a = await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.DOWNLOAD_START,
            reply_to_message_id=update.message_id
        )
        """try:
            c_time = time.time()
            if update.reply_to_message..startswith("http"):
                async with aiohttp.ClientSession() as session:
                    
                    try:
                        await dl.download_coroutine(
                            bot,
                            session,
                            update.reply_to_message,
                            saved_file_path,
                            update.message.chat.id,
                            update.message.message_id,
                            c_time
                        )
                    except:
                        await bot.edit_message_text(
                                text=Translation.SLOW_URL_DECED,
                                chat_id=update.message.chat.id,
                                message_id=update.message.message_id
                            )
                        return False


            
        except (ValueError) as e:
            await bot.edit_message_text(
                chat_id=update.chat.id,
                text=str(e),
                message_id=a.message_id
            )"""
        c_time = time.time()
        await bot.download_media(
                message=update.reply_to_message,
                file_name=saved_file_path,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.DOWNLOAD_START,
                    a,
                    c_time
                )
            )
        #else:
        await bot.edit_message_text(
            chat_id=update.chat.id,
            text=Translation.SAVED_RECVD_DOC_FILE,
            message_id=a.message_id
        )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FF_MPEG_RO_BOT_STOR_AGE_ALREADY_EXISTS,
            reply_to_message_id=update.message_id
        )
    if os.path.exists(saved_file_path):
        commands = update.command
        cmd = commands
        inline_keyboard = []
        HHD = [pyrogram.types.InlineKeyboardButton(
                                    text="Resoulution 1080P:",
                                    callback_data=("1080").encode("UTF-8")
                                )]
        HD = [pyrogram.types.InlineKeyboardButton(
                                    "Resoulution 720P:",
                                    callback_data=("720").encode("UTF-8")
                                )]
        SSD = [pyrogram.types.InlineKeyboardButton(
                                    "Resoulution 480P:",
                                    callback_data=("480").encode("UTF-8")
                                )]
        SD = [pyrogram.types.InlineKeyboardButton(
                                    "Resoulution 360p:",
                                    callback_data=("360").encode("UTF-8")
                                )]
        inline_keyboard.append(HHD)
        inline_keyboard.append(HD)
        inline_keyboard.append(SSD)
        inline_keyboard.append(SD)

        reply_markup = pyrogram.types.InlineKeyboardMarkup(inline_keyboard)

        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION.format(""),
            reply_markup=reply_markup,
            parse_mode="html",
            reply_to_message_id=update.message_id
        )

@pyrogram.Client.on_callback_query()
async def call_back(bot, update):
    saved_file_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".FFMpegRoBot.mkv"
    Data = update.data
    a=update.message

    await bot.edit_message_text(
                chat_id=update.from_user.id,
                text="The video is being compressed please wait a little bit...",
                message_id=a.message_id
            )

    o = await convert_video(saved_file_path, Config.DOWNLOAD_LOCATION,Data)

    #print(update)              
    if os.path.exists(o):
        width = 0
        height = 0
        metadata = extractMetadata(createParser(saved_file_path))
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")
    logger.info(o)
    if o is not None:
        await bot.edit_message_text(
                chat_id=update.from_user.id,
                text=Translation.UPLOAD_START,
                message_id=a.message_id
            )
        c_time = time.time()
        await bot.send_video(
                    chat_id=update.from_user.id,
                    video=o,
                    # caption=description,
                    # duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    # reply_markup=reply_markup,
                    # thumb=thumb_image_path,
                    reply_to_message_id=update.message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        a,
                        c_time
                      )
              )
            
        os.remove(saved_file_path)
            
        await bot.edit_message_text(
                    chat_id=update.from_user.id,
                    text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                    disable_web_page_preview=True,
                    message_id=a.message_id
                    )
async def download_coroutine(bot, session, url, file_name, chat_id, message_id, start):
    downloaded = 0
    display_message = ""
    async with session.get(url, timeout=Config.PROCESS_MAX_TIMEOUT) as response:
        total_length = int(response.headers["Content-Length"])
        content_type = response.headers["Content-Type"]
        if "text" in content_type and total_length < 500:
            return await response.release()
        await bot.edit_message_text(
            chat_id,
            message_id,
            text="""Initiating Download
URL: {}
File Size: {}""".format(url, humanbytes(total_length))
        )
        with open(file_name, "wb") as f_handle:
            while True:
                chunk = await response.content.read(Config.CHUNK_SIZE)
                if not chunk:
                    break
                f_handle.write(chunk)
                downloaded += Config.CHUNK_SIZE
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
                        current_message = """**Download Status**
URL: {}
File Size: {}
Downloaded: {}
ETA: {}""".format(
    url,
    humanbytes(total_length),
    humanbytes(downloaded),
    TimeFormatter(estimated_total_time)
)
                        if current_message != display_message:
                            await bot.edit_message_text(
                                chat_id,
                                message_id,
                                text=current_message
                            )
                            display_message = current_message
                    except Exception as e:
                        logger.info(str(e))
                        pass
        return await response.release()
