import asyncio

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

async def send_message(message, user_message, is_private):
    try:
        response = "Hello world"
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
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


def run_discord_bot():
    TOKEN = os.getenv('TOKEN')
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logging.info(f"{client.user} is now running")


    @client.event
    async def on_voice_state_update(member, before, after):
        if not before.channel and after.channel:
            event_msg = get_nickname(member.name) + ' joined the channel ' + str(after.channel)
            logging.info(f"event_msg created: {event_msg}")
            data = {'chat_id': {CHAT_ID}, 'text': event_msg}
            try:
                requests.post(url, data).json()
                logging.info(f"Request successfully sent {data}")
                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Request is not send, exception {e}")

        elif before.channel and not after.channel:
            event_msg = get_nickname(member.name) + ' left the channel ' + str(before.channel)
            print(event_msg)
            data = {'chat_id': {CHAT_ID}, 'text': event_msg}
            try:
                requests.post(url, data).json()
                logging.info(f"Request successfully sent {data}")
                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Request is not send, exception {e}")

    try:
        client.run(TOKEN)
        logging.info("client.run successful")
    except Exception as e:
        logging.error(f"client.run has not succeeded, error: {e}")