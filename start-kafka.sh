#!/bin/bash
set -e

# Create network if it doesn't exist
docker network inspect app_network >/dev/null 2>&1 || \
    docker network create app_network

# Build the Kafka image
docker build -t custom-kafka -f Dockerfile.kafka .

# Run the Kafka container (if not already running)
if ! docker ps --format '{{.Names}}' | grep -q '^kafka$'; then
    docker run -d \
        --name kafka \
        --network app_network \
        -p 9092:9092 \
        -p 29092:29092 \
        -e CLUSTER_ID="6NZCVziHwaCq9ztugHZYgw" \
        -e KAFKA_LISTENERS="PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093" \
        -e KAFKA_ADVERTISED_LISTENERS="PLAINTEXT://kafka:9092" \
        -e KAFKA_CONTROLLER_QUORUM_VOTERS="1@kafka:9093" \
        -e KAFKA_NODE_ID=1 \
        -e KAFKA_PROCESS_ROLES="broker,controller" \
        -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP="PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,CONTROLLER:PLAINTEXT" \
        -e KAFKA_INTER_BROKER_LISTENER_NAME="PLAINTEXT" \
        -e KAFKA_CONTROLLER_LISTENER_NAMES="CONTROLLER" \
        -e KAFKA_LOG_DIRS="/tmp/kraft-combined-logs" \
        -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
        -e KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1 \
        -e KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1 \
        --restart unless-stopped \
        custom-kafka
    echo "Kafka container started."
else
    echo "Kafka container already running."
fi

# Wait until Kafka is ready
echo "Waiting for Kafka to be ready..."
until docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list >/dev/null 2>&1; do
    echo "Kafka is not ready yet. Retrying in 5 seconds..."
    sleep 5
done

# Create topics
echo "Kafka is ready. Creating topics..."
docker run --rm --network app_network confluentinc/cp-kafka:7.5.0 \
    kafka-topics --create --if-not-exists \
    --topic notifications --partitions 1 --replication-factor 1 \
    --bootstrap-server kafka:9092

docker run --rm --network app_network confluentinc/cp-kafka:7.5.0 \
    kafka-topics --create --if-not-exists \
    --topic logs --partitions 1 --replication-factor 1 \
    --bootstrap-server kafka:9092


echo "Kafka topics initialized successfully!"
