from prometheus_client import start_http_server, Gauge
import psycopg2
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Prometheus metrics
total_events_metric = Gauge('discord_to_telegram_total_events', 'Total number of events processed')
average_delay_metric = Gauge('discord_to_telegram_avg_delay_seconds', 'Average delay in seconds between Discord and Telegram notifications')
max_delay_metric = Gauge('discord_to_telegram_max_delay_seconds', 'Maximum delay in seconds between Discord and Telegram notifications')
min_delay_metric = Gauge('discord_to_telegram_min_delay_seconds', 'Minimum delay in seconds between Discord and Telegram notifications')


def db_connect():
    # Establishes connection to the database
    db_password = os.getenv('DATABASE_PW')
    conn = psycopg2.connect(
        host="db",
        dbname="postgres",
        user="postgres",
        password=db_password,
        port=5432
    )
    return conn


def fetch_metrics_from_db():
    # Fetches delay data from the database and calculates metrics
    conn = db_connect()
    cur = conn.cursor()

    # Query to calculate delays (in seconds)
    query = """
    SELECT 
        EXTRACT(EPOCH FROM (telegram_notification_timestamp - discord_event_timestamp)) AS delay_seconds
    FROM discord_to_telegram_delays
    WHERE telegram_notification_timestamp IS NOT NULL;
    """
    cur.execute(query)
    delays = [row[0] for row in cur.fetchall()]
    conn.close()

    # If no data is present, return default values
    if not delays:
        return 0, 0, 0, 0

    total_events = len(delays)
    avg_delay = sum(delays) / total_events
    max_delay = max(delays)
    min_delay = min(delays)
    return total_events, avg_delay, max_delay, min_delay


def update_metrics():
    # Updates Prometheus metrics with the latest data
    total_events, avg_delay, max_delay, min_delay = fetch_metrics_from_db()

    # Update Prometheus gauges
    total_events_metric.set(total_events)
    average_delay_metric.set(avg_delay)
    max_delay_metric.set(max_delay)
    min_delay_metric.set(min_delay)

    print(f"Updated Metrics - Total: {total_events}, Avg: {avg_delay:.2f}s, Max: {max_delay:.2f}s, Min: {min_delay:.2f}s")


if __name__ == "__main__":
    # Start Prometheus HTTP server on port 8000
    print("Starting Prometheus metrics server on port 8000...")
    start_http_server(8000)

    # Periodically update metrics
    while True:
        update_metrics()
        time.sleep(300)  # Update every 30 seconds
