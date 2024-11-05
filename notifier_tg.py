#!/usr/bin/python
import asyncio
from telebot.async_telebot import AsyncTeleBot
import logging
import os
from dotenv import load_dotenv
load_dotenv()
token = os.getenv('TOKEN_TG')
bot = AsyncTeleBot(token)
logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w", format="%(asctime)s %(levelname)s %(message)s")
# Handle '/start' and '/help'


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    text = 'Hi, I am EchoBot.\nJust write me something and I will repeat it!'
    await bot.reply_to(message, text)


def run():
    try:
        asyncio.run(bot.polling())
        logging.info(f"Telegram bot is up and working")
    except Exception as e:
        logging.error(f"Telegram Bot is not working, error: {e}")