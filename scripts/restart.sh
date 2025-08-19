#!/bin/bash

echo "Restarting ConversationChatBot with Ollama integration..."

# Stop and remove current containers
echo "Stopping current containers..."
docker-compose down

# Rebuild the containers
echo "Rebuilding containers..."
docker-compose build

# Start with the Ollama profile, excluding the prestart service
echo "Starting containers with Ollama profile (excluding prestart)..."
docker-compose --profile ollama up -d --scale prestart=0

echo "All services should now be running."
echo "You can check the logs with: docker-compose logs -f"
echo ""
echo "To verify Ollama is working correctly:"
echo "1. Check if the model was downloaded: docker-compose exec ollama /bin/sh -c 'curl -s http://localhost:11434/api/tags'"
echo "2. Test the model: docker-compose exec ollama /bin/sh -c 'curl -s http://localhost:11434/api/generate -d \"{\\\"model\\\": \\\"deepseek-r1:8b\\\", \\\"prompt\\\": \\\"Hello, how are you?\\\"}'\"" 
echo ""
echo "To check your backend logs: docker-compose logs -f backend"
