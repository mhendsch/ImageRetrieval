#!/bin/bash

echo "Starting image retrieval services.."

python3 src/inference_service.py &
python3 src/document_db_service.py &
python3 src/embedding_service.py &

ALREADY_STOPPING=false

cleanup() {
    if [ "$ALREADY_STOPPING" = false ]; then
        ALREADY_STOPPING=true
        echo "Stopping all services..."
        kill 0
    fi
}

trap cleanup SIGINT SIGTERM

echo "All services running. Ctrl+C to stop."
wait