FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt

COPY main.py /app/launch_tg.py
COPY notifier_tg.py /app/notifier_tg.py
COPY consumer_to_tg.py /app/consumer_to_tg.py

COPY launch_ds.py /app/launch_ds.py
COPY notifier_ds.py /app/notifier_ds.py

RUN pip3 install -r requirements.txt

CMD ["sleep", "infinity"]