#!/bin/bash

echo "Waiting for Kafka to be ready..."
until docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list >/dev/null 2>&1; do
    echo "Kafka is not ready yet. Retrying in 5 seconds..."
    sleep 5
done

echo "Kafka is ready. Creating topics..."
docker run --rm --network app_network confluentinc/cp-kafka:7.5.0 \
    kafka-topics --create --if-not-exists --topic notifications --partitions 1 --replication-factor 1 --bootstrap-server kafka:9092

echo "Kafka topics initialized successfully!"
