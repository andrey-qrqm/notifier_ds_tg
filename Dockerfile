FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY main.py /app/launch_tg.py
COPY requirements.txt /app/requirements.txt
COPY notifier_tg.py /app/notifier_tg.py
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3", "launch_tg.py"]