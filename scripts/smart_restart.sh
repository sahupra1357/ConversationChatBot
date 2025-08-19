#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}ConversationChatBot Restart Utility${NC}"
echo "This script will restart your services without running prestart again."

# Function to check if a container exists and is running
container_running() {
    docker ps --format '{{.Names}}' | grep -q "^$1$"
    return $?
}

# Function to check if database is initialized
check_db_initialized() {
    if container_running "postgres_db"; then
        # Try to connect to the database and check if users table exists
        docker exec postgres_db psql -U postgres -d arxiv_papers -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user')" | grep -q 't'
        return $?
    else
        return 1
    fi
}

# Check if we should run prestart
if ! check_db_initialized; then
    echo -e "${YELLOW}WARNING: Database appears to be empty or not initialized.${NC}"
    read -p "Do you want to run the prestart service to initialize the database? (y/n): " run_prestart
    if [[ $run_prestart =~ ^[Yy]$ ]]; then
        prestart_flag=""
        echo -e "${GREEN}Will include prestart service.${NC}"
    else
        prestart_flag="--scale prestart=0"
        echo -e "${YELLOW}Skipping database initialization.${NC}"
    fi
else
    prestart_flag="--scale prestart=0"
    echo -e "${GREEN}Database appears to be initialized. Skipping prestart service.${NC}"
fi

# Stop current containers
echo -e "${YELLOW}Stopping current containers...${NC}"
docker-compose down

# Ask if user wants to rebuild
read -p "Do you want to rebuild the containers? (y/n): " rebuild
if [[ $rebuild =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Rebuilding containers...${NC}"
    docker-compose build
fi

# Start containers with appropriate options
echo -e "${YELLOW}Starting containers with Ollama profile...${NC}"
docker-compose --profile ollama up -d $prestart_flag

echo -e "${GREEN}All services should now be running.${NC}"
echo "You can check the logs with: docker-compose logs -f"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "1. Check if Ollama models are available:"
echo "   docker-compose exec ollama /bin/sh -c 'curl -s http://localhost:11434/api/tags'"
echo ""
echo "2. Test the Ollama model:"
echo "   docker-compose exec ollama /bin/sh -c 'curl -s http://localhost:11434/api/generate -d \"{\\\"model\\\": \\\"deepseek-r1:8b\\\", \\\"prompt\\\": \\\"Hello, how are you?\\\"}'\"" 
echo ""
echo "3. Check backend logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "4. Check Ollama logs:"
echo "   docker-compose logs -f ollama"
