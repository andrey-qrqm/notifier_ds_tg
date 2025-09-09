import os
import logging
import time
import psycopg2
import discord
import requests
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from quixstreams import Application
from confluent_kafka import KafkaException
import json
# test 9

logging.basicConfig(
    level=logging.INFO,
    # filename="py_log.log",
    # filemode="w",
    format="%(asctime)s %(levelname)s %(message)s")

load_dotenv()
TOKEN_TG = os.getenv('TOKEN_TG')
CHAT_ID = int(os.getenv('CHAT_ID'))
TOPIC_ID = int(os.getenv('TOPIC_ID'))
intents = discord.Intents.all()
URL = f'https://api.telegram.org/bot{TOKEN_TG}/sendMessage'


print("Started")
logging.info('notifier_ds is started')

port = os.getenv('PORT')

kafka_app = Application(
    broker_address="kafka:9092",
    loglevel="DEBUG",
)


def generate_event_id():
    return str(uuid.uuid4())


async def send_message(message, is_private):
    # currently not in use
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
            logging.info(f"get_nickname returns author: {author}")
            return author
        except Exception as e:
            logging.warning(f"get_nickname finds Exception: {e}, returns {author}")
            return author


def check_nickname_not_none(member):
    nickname = get_nickname(member.nick)
    if nickname is None:
        nickname = member.name
    return nickname


def send_data(event_msg, discord_channel_name, conn, username, is_join, data_type):
    list_tg_id = take_ids(discord_channel_name, conn)
    print(list_tg_id, '  ', list_tg_id[0][0])
    if not list_tg_id:
        logging.warning(f"No Telegram IDs found for channel {discord_channel_name}")
        return
    for tg_id in list_tg_id[0][0]:
        print(tg_id)
        if int(tg_id) == CHAT_ID:
            logging.info(f"chat id: {int(tg_id)}, Required for topics: {CHAT_ID}, topic = {TOPIC_ID}")
            data = {
                'chat_id': int(tg_id),
                'message_thread_id': TOPIC_ID,
                'text': event_msg,
                'username': username,
                'is_join': is_join,
                'data_type': data_type,
                'disable_notification': True
            }
        else:
            logging.info(f"chat id: {int(tg_id)}, Required for topics: {CHAT_ID}")
            data = {
                'chat_id': int(tg_id),
                'topic_id': None,
                'text': event_msg,
                'username': username,
                'is_join': is_join,
                'data_type': data_type,
                'disable_notification': True
            }

        if data_type == "message":
            try:
                with kafka_app.get_producer() as producer:
                    logging.info(f"producer got data: {json.dumps(data)}")
                    producer.produce(
                        topic="notifications",
                        key="message",
                        value=json.dumps(data),
                    )
            except KafkaException as e:
                logging.error(f"Kafka raised exception {e}")

        if data_type == "event":
            try:
                with kafka_app.get_producer() as producer:
                    logging.info(f"producer got data: {json.dumps(data)}")
                    producer.produce(
                        topic="notifications",
                        key="event",
                        value=json.dumps(data),
                    )
            except KafkaException as e:
                logging.error(f"Kafka raised exception {e}")



def take_ids(discord_channel_name, conn):
    cur = conn.cursor()
    logging.info(f"discord_channel_name = {discord_channel_name}")
    cur.execute(f"""
        SELECT tg_chat_id FROM tracking WHERE DISCORD_ID = %s
    """, (discord_channel_name,))
    list_tg_ids = cur.fetchall()  # Fetch all rows from the query result
    print(list_tg_ids)
    logging.info(f"Fetched TG IDs: {list_tg_ids}")
    return list_tg_ids


def db_connect():
    # Connect to the db
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
    # Record the discord timestamp for metrics
    try:
        # Connect to your PostgreSQL database
        conn = db_connection
        cur = conn.cursor()

        # Insert event into the table
        query = f"""
        INSERT INTO discord_to_telegram_delays {event_id}, {discord_event_timestamp}
        ON CONFLICT (event_id) DO NOTHING;
        """
        cur.execute(query)
        conn.commit()
        print(f"Recorded Discord event: {event_id}")
        logging.info(f"Recorded Discord event: {event_id}")
    except Exception as e:
        print(f"Error recording Discord event: {e}")
        logging.error(f"Error recording Discord event: {e}")


def update_telegram_notification(db_connection, event_id, telegram_notification_timestamp):
    # Record the telegram timestamp for metrics
    try:
        # Connect to your PostgreSQL database
        conn = db_connection
        cursor = conn.cursor()

        # Update event in the table
        query = f"""
        UPDATE discord_to_telegram_delays
        SET telegram_notification_timestamp = {telegram_notification_timestamp}
        WHERE event_id = {event_id};
        """
        cursor.execute(query)
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
        # Returns list of Guilds Names, where the bot is activated
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
        # Event of joining and leaving:
        discord_channel_name = str(member.guild)
        if not before.channel and after.channel and not member.bot:
            conn = db_connect()  # On this conn
            user_trigger = str(check_nickname_not_none(member))

            logging.info(f"user joined: {user_trigger}")
            is_join = 't' #user join flag
            data_type = "message" # will send to a message topic
            event_msg = user_trigger + ' joined the channel ' + str(after.channel)  # create an output
            logging.info(f"event_msg created: {event_msg}")
            send_data(event_msg, discord_channel_name, conn, user_trigger, is_join, data_type)  # Call func to send data on tg
            print(member.guild)
            conn.commit()
            conn.close()

        elif before.channel and not after.channel and not member.bot:
            conn = db_connect()  # On this conn

            is_join = 'f' #user join flag false
            data_type = "message"
            user_trigger = str(check_nickname_not_none(member)) # Nickname/Name of user who left channel
            logging.info(f"user left: {user_trigger}")

            event_msg = user_trigger + ' left the channel ' + str(before.channel)  # create an output
            logging.info(f"event_msg created: {event_msg}")
            send_data(event_msg, discord_channel_name, conn, user_trigger, is_join, data_type)  # Call func to send data on tg
            print(member.guild)
            conn.commit()
            conn.close()


    @client.event
    async def on_scheduled_event_create(event):
        logging.info(f"event {event.name} has been created, guild = {event.guild}, channel = {event.channel}")
        conn = db_connect()
        event_time = (event.start_time + timedelta(hours=3)).strftime("%d %B, %H:%M")
        event_message = f"**{event.name}** in {event.guild}. Start - **{event_time}**"
        event_id = generate_event_id()  # Generate unique Event Id
        send_data(event_message, str(event.guild), conn, "event", is_join='t', data_type="event")
        logging.info(f"send data - {event_message} to {event.guild}")
        conn.commit()
        conn.close()

    @client.event
    async def on_scheduled_event_delete(event):
        logging.info(f"event {event.name} has been created, guild = {event.guild}, channel = {event.channel}")
        conn = db_connect()
        event_time = (event.start_time + timedelta(hours=3)).strftime("%d %B, %H:%M")
        event_message = f"**{event.name}** in {event.guild}. Start - **{event_time}** IS DELETED"
        event_id = generate_event_id()  # Generate unique Event Id
        send_data(event_message, str(event.guild), conn, "event", is_join='f', data_type="event")
        logging.info(f"send data - {event_message} to {event.guild}")
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