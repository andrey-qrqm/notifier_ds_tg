#!/bin/bash

case "$1" in
    start)
        echo "Starting standalone PostgreSQL..."
        ./start-postgres.sh
        
        echo "Starting standalone Kafka..."
        ./start-kafka.sh
        
        echo "Initializing Kafka topics..."
        ./init-kafka.sh
        
        echo "Starting other services..."
        docker-compose up -d
        ;;
    stop)
        echo "Stopping services..."
        docker-compose down
        
        echo "Stopping Kafka..."
        docker stop kafka 2>/dev/null || true
        
        echo "Stopping PostgreSQL..."
        docker stop db 2>/dev/null || true
        ;;
    restart)
        echo "Restarting services..."
        ./manage-services.sh stop
        sleep 5
        ./manage-services.sh start
        ;;
    status)
        echo "PostgreSQL status:"
        docker ps -f name=db
        
        echo -e "\nKafka status:"
        docker ps -f name=kafka
        
        echo -e "\nOther services status:"
        docker-compose ps
        ;;
    logs)
        if [ "$2" = "postgres" ]; then
            docker logs db
        elif [ "$2" = "kafka" ]; then
            docker logs kafka
        else
            docker-compose logs ${2:-}
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs [service]}"
        exit 1
        ;;
esac
