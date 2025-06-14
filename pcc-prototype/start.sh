#!/bin/bash

echo "🏥 Starting Patient Command Center..."
echo ""
echo "This will start:"
echo "  - Kafka message broker"
echo "  - FastAPI backend with AI agents"
echo "  - React frontend dashboard"
echo "  - Synthetic HL7 data generator"
echo ""
echo "The frontend will be available at http://localhost:5173"
echo ""

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# Start Docker Compose
docker compose up --build

echo ""
echo "Shutting down services..."
docker compose down