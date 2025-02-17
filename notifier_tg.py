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
logging.basicConfig(
    level=logging.INFO,
    filename="py_log.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s"
)
db_password = os.getenv('DATABASE_PW')
port = os.getenv('PORT')


def remove_spaces(input_str):
    return input_str.replace(" ", "")


def conn_check():
    db_password = os.getenv('DATABASE_PW')
    db_password = remove_spaces(db_password)
    try:
        conn = psycopg2.connect(
            host="db",
            dbname="postgres",
            user="postgres",
            password=db_password,
            port=5432
        )
        print("Connection successful!")
        logging.info("Connection succesful!")
        conn.close()
    except psycopg2.OperationalError as e:
        print("Connection failed:", e)
        logging.error(f"Connection failed: {e}")


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


@bot.message_handler(commands=['help', 'start'])
async def send_help(message):
    text = """
    Hey, I'm your Discord to Telegram Notifier bot!
    I will track added Discord guilds and notify you when somebody enters voice chat
    What can I do?
    /help, /start - send help(this message)
    /add_channel [Name_of_guild] - Add Discord guild to tracking in this chat. Discord Bot should be added to the
    discord guild
    (If you want to add Bot to your discord guild, use this link - )
    /remove_channel [Name_of_guild] - remove Discord guild from tracking in this chat
    """
    await bot.reply_to(message, text)


@bot.message_handler(commands='get_ip')
async def send_ip(message):
    text = message.chat.id
    await bot.reply_to(message, text)


def create_database_conn():
    global conn, cur
    conn = psycopg2.connect(
        host="db",
        dbname="postgres",
        user="postgres",
        password=db_password,
        port=port
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tracking (
        DISCORD_ID TEXT PRIMARY KEY,
        tg_chat_id BIGINT[]  -- Array of BIGINTs (PostgreSQL only)
    );
    
    CREATE TABLE IF NOT EXISTS discord_to_telegram_delays (
        event_id UUID PRIMARY KEY,
        discord_event_timestamp TIMESTAMP NOT NULL,
        telegram_notification_timestamp TIMESTAMP NOT NULL
    );

    """)
    conn.commit()
    cur.execute("""SELECT * FROM tracking""")
    channels = cur.fetchall()
    logging.info(f"channels - {channels}")


def extract_arg(arg):
    return arg.split()[1:]


def get_discord_guild_exists():
    cur.execute(
        """
        SELECT DISCORD_ID 
        FROM tracking;
        """
    )
    result = cur.fetchall()
    logging.info(f"get_discord_guild_exists: {result}")
    return result


def list_to_text(l):
    text = "\n"
    for i in l:
        text = text + str(i) + "\n"
    logging.info(f"list_to_text: {text}")
    return text


conn_check()
create_database_conn()


@bot.message_handler(commands='add_channel')
async def add_channel(message):
    channel = str(extract_arg(message.text)[0])
    chat_id = str(message.chat.id)

    existing_guilds = get_discord_guild_exists()
    existing_guilds_text = list_to_text(existing_guilds)

    if channel not in existing_guilds:
        text = f"""Discord guild {channel} has not connected to our service yet.
                    However, you can connect to these guilds: {existing_guilds_text}"""
        logging.info(f"user tried to connect to guild {channel}, while it is not connected to our system")
    else:
        logging.info(f"channel {channel} is found in existing guilds")
        print(channel)
        logging.info(f"Adding channel {channel} for chat ID {chat_id}")
        cur.execute(f"""
            INSERT INTO tracking (DISCORD_ID, tg_chat_id)
            VALUES ('{channel}', ARRAY[{chat_id}]::BIGINT[])  -- Insert new DISCORD_ID with initial tg_chat_id array
            ON CONFLICT (DISCORD_ID)  -- If DISCORD_ID already exists
            DO UPDATE
            SET tg_chat_id = CASE
                WHEN NOT ARRAY[{chat_id}]::BIGINT[] <@ tracking.tg_chat_id THEN tracking.tg_chat_id || {chat_id}
                ELSE tracking.tg_chat_id
            END;
        """)

        conn.commit()  # Commit the insert/update operation

        # Fetch data from the tracking table
        cur.execute("SELECT * FROM tracking")
        result = cur.fetchall()  # Fetch all rows from the query
        text = f"Channel added: {result}"
    logging.info(text)
    await bot.reply_to(message, text)


@bot.message_handler(commands='remove_channel')
async def remove_channel(message):
    # Extract the channel and chat ID from the command text
    channel = str(extract_arg(message.text)[0])
    chat_id = str(message.chat.id)

    # Print for debugging purposes
    print(f"Removing channel {channel} for chat ID {chat_id}")
    logging.info(f"Removing channel {channel} for chat ID {chat_id}")

    # SQL query to delete the chat ID from the tg_chat_id array
    cur.execute(f"""
        UPDATE tracking
        SET tg_chat_id = ARRAY(
            SELECT unnest(tg_chat_id)
            EXCEPT
            SELECT {chat_id}::BIGINT
        )
        WHERE DISCORD_ID = '{channel}' AND {chat_id}::BIGINT = ANY(tg_chat_id);
    """)

    conn.commit()  # Commit the update operation

    # Fetch data from the tracking table to confirm deletion
    cur.execute("SELECT * FROM tracking")
    result = cur.fetchall()  # Fetch all rows from the query
    text = f"Channel removed. Updated tracking data: {result}"
    logging.info(text)
    await bot.reply_to(message, text)


def run():
    try:
        asyncio.run(bot.polling())
        logging.info(f"Telegram bot is up and working")
    except Exception as e:
        logging.error(f"Telegram Bot is not working, error: {e}")
