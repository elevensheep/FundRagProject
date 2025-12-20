#!/bin/bash

echo "🚀 Starting deployment..."

# .env 파일 확인
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before running again."
    exit 1
fi

# Docker 빌드 및 실행
echo "🏗️  Building Docker images..."
docker-compose build

echo "▶️  Starting services..."
docker-compose up -d

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service URLs:"
echo "   - Spring Boot API: http://localhost:8080"
echo "   - MongoDB: mongodb://localhost:27017"
echo "   - Kafka: localhost:9092"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart: docker-compose restart"
echo ""
