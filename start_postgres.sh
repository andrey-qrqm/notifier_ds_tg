#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
fi

# Set default password if not set
DATABASE_PW=${DATABASE_PW:-postgrespassword}

# Create network if it doesn't exist
docker network inspect app_network >/dev/null 2>&1 || \
    docker network create app_network

# Build the Postgres image
docker build -t custom-postgres -f Dockerfile.postgres .

# Run the Postgres container
docker run -d \
    --name db \
    --network app_network \
    -e POSTGRES_PASSWORD=$DATABASE_PW \
    -p 5432:5432 \
    -v pgdata:/var/lib/postgresql/data \
    --restart unless-stopped \
    custom-postgres

echo "Standalone PostgreSQL 'db 'container is running on network 'app_network'"
