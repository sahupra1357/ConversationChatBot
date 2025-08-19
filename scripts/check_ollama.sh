#!/bin/bash

# Color definitions
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Ollama Status Checker${NC}"
echo "This script will help you check the status of your Ollama container and models."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if Ollama container is running
if ! docker ps | grep -q ollama; then
    echo -e "${RED}Error: Ollama container is not running.${NC}"
    echo "Run 'docker-compose --profile ollama up -d' to start it."
    exit 1
fi

# Function to run curl commands using the model-loader container
run_curl() {
    if docker ps | grep -q ollama-model-loader; then
        # Use the existing model-loader container if it's running
        docker exec ollama-model-loader curl -s "$@"
    else
        # Start a temporary curl container that connects to the Ollama network
        network=$(docker inspect ollama --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}')
        docker run --rm --network=$network curlimages/curl:latest curl -s "$@"
    fi
}

# Display main menu
show_menu() {
    echo -e "\n${GREEN}Ollama Management Menu:${NC}"
    echo "1. Check if Ollama API is responding"
    echo "2. List downloaded models"
    echo "3. Check model details"
    echo "4. Download a model"
    echo "5. Test a model with a simple prompt"
    echo "6. View Ollama logs"
    echo "7. Restart Ollama container"
    echo "0. Exit"
    echo -n "Enter your choice: "
}

# Main loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1)
            echo -e "\n${YELLOW}Checking Ollama API...${NC}"
            response=$(run_curl http://ollama:11434/api/version)
            if [ ! -z "$response" ]; then
                echo -e "${GREEN}Ollama API is responding:${NC}"
                echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
            else
                echo -e "${RED}Ollama API is not responding.${NC}"
            fi
            ;;
        2)
            echo -e "\n${YELLOW}Listing downloaded models...${NC}"
            response=$(run_curl http://ollama:11434/api/tags)
            if [ ! -z "$response" ]; then
                echo -e "${GREEN}Models available in Ollama:${NC}"
                echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
            else
                echo -e "${RED}Could not retrieve model list.${NC}"
            fi
            ;;
        3)
            echo -n "Enter model name (e.g., deepseek-r1:8b): "
            read model_name
            echo -e "\n${YELLOW}Checking details for model $model_name...${NC}"
            response=$(run_curl http://ollama:11434/api/show -d "{\"name\": \"$model_name\"}")
            if [[ $response == *"error"* ]]; then
                echo -e "${RED}Error:${NC}"
                echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
            else
                echo -e "${GREEN}Model details:${NC}"
                echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
            fi
            ;;
        4)
            echo -n "Enter model name to download (e.g., deepseek-r1:8b): "
            read model_name
            echo -e "\n${YELLOW}Downloading model $model_name...${NC}"
            echo "This may take a while. Check the Ollama logs for progress."
            response=$(run_curl -X POST http://ollama:11434/api/pull -d "{\"name\": \"$model_name\"}")
            echo "$response"
            ;;
        5)
            echo -n "Enter model name (e.g., deepseek-r1:8b): "
            read model_name
            echo -n "Enter prompt: "
            read prompt
            echo -e "\n${YELLOW}Testing model $model_name with prompt: \"$prompt\"${NC}"
            response=$(run_curl -X POST http://ollama:11434/api/generate -d "{\"model\": \"$model_name\", \"prompt\": \"$prompt\", \"stream\": false}")
            echo -e "${GREEN}Response:${NC}"
            echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
            ;;
        6)
            echo -e "\n${YELLOW}Viewing Ollama logs (press Ctrl+C to exit):${NC}"
            docker logs -f ollama
            ;;
        7)
            echo -e "\n${YELLOW}Restarting Ollama container...${NC}"
            docker restart ollama
            echo "Waiting for Ollama to restart..."
            sleep 5
            echo -e "${GREEN}Ollama restarted.${NC}"
            ;;
        0)
            echo -e "\n${GREEN}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "\n${RED}Invalid option.${NC} Please try again."
            ;;
    esac
    
    echo -e "\nPress Enter to continue..."
    read
done
