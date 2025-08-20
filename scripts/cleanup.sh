#!/bin/bash
echo "Stopping all running containers..."
docker ps -a -q | xargs -r docker stop

echo "Removing all containers..."
docker ps -a -q | xargs -r docker rm

echo "Removing all Docker networks..."
docker network ls -q | xargs -r docker network rm

echo "Removing all Docker images..."
docker images -q | xargs -r docker rmi -f

echo "Removing all Docker volumes..."
docker volume ls -q | xargs -r docker volume rm -f

echo "Cleanup complete!"