import os
import logging
import asyncio
import time
import psycopg2
import discord
import requests
import uuid
from datetime import datetime
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    filename="py_log.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s")

load_dotenv()
TOKEN_TG = os.getenv('TOKEN_TG')
CHAT_ID = os.getenv('CHAT_ID')
intents = discord.Intents.all()
URL = f'https://api.telegram.org/bot{TOKEN_TG}/sendMessage'


print("Started")
logging.info('notifier_ds is started')

port = os.getenv('PORT')


def generate_event_id():
    return str(uuid.uuid4())


async def send_message(message, is_private):
    try:
        response = "Hello world"
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        logging.error(f"Hello world raised exception: {e}")
        print(e)


def get_nickname(author):
    if author is not None:
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


def send_data(event_msg, url, discord_channel_name, conn, event_id):
    list_tg_id = take_ids(discord_channel_name, conn)
    print(list_tg_id, '  ', list_tg_id[0][0])
    if not list_tg_id:
        logging.warning(f"No Telegram IDs found for channel {discord_channel_name}")
        return
    for tg_id in list_tg_id[0][0]:
        print(tg_id)
        data = {'chat_id': {int(tg_id)}, 'text': event_msg}
        try:
            requests.post(url, data).json()
            logging.info(f"Request successfully sent {data}")
        except Exception as e:
            logging.error(f"Request is not send, exception {e}")

    telegram_notification_timestamp = datetime.utcnow()
    update_telegram_notification(conn, event_id, telegram_notification_timestamp)


def take_ids(discord_channel_name, conn):
    cur = conn.cursor()
    cur.execute(f"""
        SELECT tg_chat_id FROM tracking WHERE DISCORD_ID = %s 
    """, (discord_channel_name,))
    list_tg_ids = cur.fetchall()  # Fetch all rows from the query result
    print(list_tg_ids)
    return list_tg_ids


def db_connect():
    db_password = os.getenv('DATABASE_PW')
    conn = psycopg2.connect(
        host="db",
        dbname="postgres",
        user="postgres",
        password=db_password,
        port=5432
    )
    return conn


def record_discord_event(db_connection, event_id, discord_event_timestamp):
    try:
        # Connect to your PostgreSQL database
        conn = db_connection
        cur = conn.cursor()

        # Insert event into the table
        query = """
        INSERT INTO discord_to_telegram_delays (event_id, discord_event_timestamp)
        VALUES (%s, %s)
        ON CONFLICT (event_id) DO NOTHING;
        """
        cur.execute(query, (event_id, discord_event_timestamp))
        conn.commit()
        print(f"Recorded Discord event: {event_id}")
        logging.info(f"Recorded Discord event: {event_id}")
    except Exception as e:
        print(f"Error recording Discord event: {e}")
        logging.error(f"Error recording Discord event: {e}")


def update_telegram_notification(db_connection, event_id, telegram_notification_timestamp):
    try:
        # Connect to your PostgreSQL database
        conn = db_connection
        cursor = conn.cursor()

        # Update event in the table
        query = """
        UPDATE discord_to_telegram_delays
        SET telegram_notification_timestamp = %s
        WHERE event_id = %s;
        """
        cursor.execute(query, (telegram_notification_timestamp, event_id))
        conn.commit()
        print(f"Updated Telegram notification timestamp for event: {event_id}")
    except Exception as e:
        print(f"Error updating Telegram notification: {e}")


def run_discord_bot():
    global intents
    token = os.getenv('TOKEN')
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logging.info(f"{client.user} is now running")
        conn = db_connect()
        await get_existing_guilds(conn)

    async def get_existing_guilds(db_connection) -> list[str]:
        text_channel_list = []
        conn = db_connection
        cur = conn.cursor()
        for guild in client.guilds:
            if guild.name not in text_channel_list:
                text_channel_list.append(guild.name)
                cur.execute(f"""
                    INSERT INTO tracking (DISCORD_ID, tg_chat_id)
                    VALUES (%s, ARRAY[]::BIGINT[])  -- Insert new DISCORD_ID with empty tg_chat_id array
                    ON CONFLICT (DISCORD_ID)  -- If DISCORD_ID already exists
                    DO NOTHING;
                """, (guild.name, ))
            print(text_channel_list)
        logging.info(text_channel_list)
        conn.commit()
        conn.close()
        return text_channel_list

    @client.event
    async def on_voice_state_update(member, before, after):
        discord_channel_name = str(member.guild)
        if not before.channel and after.channel:
            conn = db_connect()  # On this conn
            discord_event_timestamp = datetime.utcnow()  # Take current time
            event_id = generate_event_id()  # Generate unique Event Id
            record_discord_event(conn, event_id, discord_event_timestamp)  # Make a record in the delays db
            event_msg = get_nickname(member.nick) + ' joined the channel ' + str(after.channel)  # create an output
            logging.info(f"event_msg created: {event_msg}")
            send_data(event_msg, URL, discord_channel_name, conn, event_id)  # Call func to send data on tg
            print(member.guild)
            conn.commit()
            conn.close()

        elif before.channel and not after.channel:
            conn = db_connect()  # On this conn
            discord_event_timestamp = datetime.utcnow()  # Take current time
            event_id = generate_event_id()  # Generate unique Event Id
            record_discord_event(conn, event_id, discord_event_timestamp)  # Make a record in the delays db
            event_msg = get_nickname(member.nick) + ' left the channel ' + str(before.channel)  # create an output
            logging.info(f"event_msg created: {event_msg}")
            send_data(event_msg, URL, discord_channel_name, conn, event_id)  # Call func to send data on tg
            print(member.guild)
            conn.commit()
            conn.close()

    attempt = 1
    while True:
        try:
            client.run(token)
        except Exception as e:
            logging.error(f"Discord bot crashed: {e}")
            time.sleep(min(10 * attempt, 600))  # Max wait time: 10 minutes
            attempt += 1


if __name__ == "__main__":
    run_discord_bot()
