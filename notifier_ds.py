import asyncio
import psycopg2
import discord
import requests
import logging
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w", format="%(asctime)s %(levelname)s %(message)s")

load_dotenv()
TOKEN_TG = os.getenv('TOKEN_TG')
CHAT_ID = os.getenv('CHAT_ID')
intents = discord.Intents.all()
url = f'https://api.telegram.org/bot{TOKEN_TG}/sendMessage'
print("RUNNING")
logging.info('notifier_ds is RUNNING')

port = os.getenv('PORT')



async def send_message(message, user_message, is_private):
    try:
        response = "Hello world"
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        logging.error(f"Hello world raised exception: {e}")
        print(e)

def get_nickname(author):
    try:
        if '(' in author:
            i = author.index('(') + 1
            nickname = author[i:(len(author) - 1)]
            logging.info(f"get_nickname returns nickname: {nickname}")
            return nickname
        else:
            logging.info(f"get_nickname returns author: {author}")
            return author
    except Exception as e:
        logging.warning(f"get_nickname finds Exception: {e}, returns {author}")
        return author


def send_data(event_msg, url, discord_channel_name):
    list_tg_id = take_ids(discord_channel_name)
    print(list_tg_id, '  ', list_tg_id[0][0])
    for tg_id in list_tg_id[0][0]:
        print(tg_id)
        data = {'chat_id': {int(tg_id)}, 'text': event_msg}
        try:
            requests.post(url, data).json()
            logging.info(f"Request successfully sent {data}")
        except Exception as e:
            logging.error(f"Request is not send, exception {e}")

def take_ids(discord_channel_name):
    db_password = os.getenv('DATABASE_PW')
    conn = psycopg2.connect(host="db", dbname="postgres", user="postgres", password=db_password, port=port)
    cur = conn.cursor()
    cur.execute(f"""
        SELECT tg_chat_id FROM tracking WHERE DISCORD_ID = '{discord_channel_name}' 
    """)
    list_tg_ids = cur.fetchall()  # Fetch all rows from the query result
    conn.commit()
    conn.close()
    print(list_tg_ids)
    return list_tg_ids

def run_discord_bot():
    TOKEN = os.getenv('TOKEN')
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logging.info(f"{client.user} is now running")
        text_channel_list = []
        for guild in client.guilds:
            if guild.name not in text_channel_list:
                text_channel_list.append(guild.name)
            print(text_channel_list)


    @client.event
    async def on_voice_state_update(member, before, after):
        discord_channel_name = str(member.guild)
        if not before.channel and after.channel:
            event_msg = get_nickname(member.name) + ' joined the channel ' + str(after.channel)
            logging.info(f"event_msg created: {event_msg}")
            send_data(event_msg, url, discord_channel_name)
            print(member.guild)

        elif before.channel and not after.channel:
            event_msg = get_nickname(member.name) + ' left the channel ' + str(before.channel)
            send_data(event_msg, url, discord_channel_name)
            print(member.guild)

    try:
        client.run(TOKEN)
        logging.info("client.run successful")
    except Exception as e:
        logging.error(f"client.run has not succeeded, error: {e}")