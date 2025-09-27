import logging
import json
import requests
from quixstreams import Application
from confluent_kafka import KafkaException
import asyncio
from dotenv import load_dotenv
import os

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    force=True
)


def value_to_data(value):
    data = {'chat_id': value['chat_id'], 'text': value['text']}
    message_thread_id = value.get('message_thread_id')
    if message_thread_id is not None:
        data['message_thread_id'] = message_thread_id
    return data


def send_data(value):
    if value["chat_id"] is not None:
        data = value_to_data(value)
        logging.info(f"Sending {data['text']} to {data['chat_id']}")
        URL = f'https://api.telegram.org/bot{TOKEN_TG}/sendMessage'
        requests.post(URL, data).json()
        logging.info(f"POST sent")
    else:
        logging.error(f"value does not have a chat_id {value}")


load_dotenv()
TOKEN_TG = os.getenv('TOKEN_TG')

app = Application(
    broker_address="kafka:9092",
    loglevel="DEBUG",
    consumer_group="event_reader",
)
try:
    with app.get_consumer() as consumer:
        consumer.subscribe(["notifications", "logs"])

        while True:
            msg = consumer.poll(1)

            if msg is None:
                print("waiting...")
            elif msg.error() is not None:
                raise Exception(msg.error())
            else:
                key = msg.key().decode('utf-8') if msg.key() else None
                value = json.loads(msg.value())
                offset = msg.offset()
                logging.info(f"{offset, key, value}")
                if msg.topic() == "notifications":
                    if key in ("message", "event"):
                        logging.info(f"message {value}, key {key}, message topic - {msg.topic()}")
                        send_data(value)
                    # Here should be the anti-spam logic
                if msg.topic() == "logs":
                    if key == "logs":
                        logging.info(f"message {value}, key {key}, message topic - {msg.topic()}")
                        send_data(value)


except KafkaException as e:
    logging.error(f"Kafka has raised exception {e}")
except Exception as e:
    logging.error(f"Non-kafka error occured {e}")
