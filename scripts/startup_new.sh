#!/bin/bash

# Stop any running containers
docker compose down

# Remove all Docker images (use with caution!)
docker rmi $(docker images -q) -f

# Remove all Docker volumes (use with caution!)
docker volume rm $(docker volume ls -q) -f

# Start Docker containers with Ollama profile
docker compose --profile ollama up --build