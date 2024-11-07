#!/usr/bin/python
import asyncio
from telebot.async_telebot import AsyncTeleBot
import logging
import os
from dotenv import load_dotenv
import psycopg2



load_dotenv()
token = os.getenv('TOKEN_TG')
bot = AsyncTeleBot(token)
logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w", format="%(asctime)s %(levelname)s %(message)s")
db_password = os.getenv('DATABASE_PW')
port = os.getenv('PORT')

conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password=db_password, port=port)
cur = conn.cursor()


cur.execute("""CREATE TABLE IF NOT EXISTS tracking (
    DISCORD_ID INTEGER PRIMARY KEY,
    tg_chat_id INTEGER[]
    );
    """)
conn.commit()


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    text = 'Hi, I am EchoBot.\nJust write me something and I will repeat it!'
    await bot.reply_to(message, text)

@bot.message_handler(commands='get_ip')
async def send_ip(message):
    text = message.chat.id
    await bot.reply_to(message, text)

def extract_arg(arg):
    return arg.split()[1:]

@bot.message_handler(commands='add_channel')
async def add_channel(message):
    channel = extract_arg(message.text)[0]
    chat_id = str(message.chat.id)
    print(channel)
    cur.execute(f"""
        INSERT INTO tracking (DISCORD_ID, tg_chat_id)
        VALUES ({channel}, ARRAY[{chat_id}])  -- Insert new DISCORD_ID with initial tg_chat_id array
        ON CONFLICT (DISCORD_ID)  -- If DISCORD_ID already exists
        DO UPDATE
        SET tg_chat_id = CASE
            WHEN NOT ARRAY[{chat_id}] <@ tracking.tg_chat_id THEN tracking.tg_chat_id || {chat_id}
            ELSE tracking.tg_chat_id
        END;
    """)

    conn.commit()  # Commit the insert/update operation

    # Fetch data from the tracking table
    cur.execute("SELECT * FROM tracking")
    result = cur.fetchall()  # Fetch all rows from the query
    text = f"Channel added: {result}"
    await bot.reply_to(message, text)


def run():
    try:
        asyncio.run(bot.polling())
        logging.info(f"Telegram bot is up and working")
    except Exception as e:
        logging.error(f"Telegram Bot is not working, error: {e}")