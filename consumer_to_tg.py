import logging
import json
import requests
from quixstreams import Application
from confluent_kafka import KafkaException
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN_TG = os.getenv('TOKEN_TG')

app = Application(
    broker_address="kafka:9092",
    loglevel="DEBUG",
    consumer_group="event_reader",
)
try:
    with app.get_consumer() as consumer:
        consumer.subscribe(["notifications"])

        while True:
            msg = consumer.poll(1)

            if msg is None:
                print("waiting...")
            elif msg.error() is not None:
                raise Exception(msg.error())
            else:
                key = msg.key().decode('utf-8')
                value = json.loads(msg.value())
                offset = msg.offset()
                print(f"{offset, key, value}")
                if key == "message":
                    if value["chat_id"] is not None:
                        logging.info(f"Sending {value['text']} to {value['chat_id']}")
                        URL = f'https://api.telegram.org/bot{TOKEN_TG}/sendMessage'
                        requests.post(URL, value).json()
                        logging.info(f"POST sent")
                    else:
                        logging.error(f"value does not have a chat_id {value}")

                if key == "event":
                    if value["chat_id"] is not None:
                        logging.info(f"Sending {value['text']} to {value['chat_id']}")
                        URL = f'https://api.telegram.org/bot{TOKEN_TG}/sendMessage'
                        requests.post(URL, value).json()
                        logging.info(f"POST sent")
                    else:
                        logging.error(f"value does not have a chat_id {value}")

except KafkaException as e:
    logging.error(f"Kafka has raised exception {e}")
except Exception as e:
    logging.error(f"Non-kafka error occured {e}")
