#!/bin/bash

# Add colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Ollama Models Checker${NC}"

# Check if ollama container is running
if ! docker ps | grep -q ollama; then
    echo -e "${RED}Error: Ollama container is not running!${NC}"
    echo "Please start it with: docker-compose --profile ollama up -d"
    exit 1
fi

# Check if ollama-model-loader is available
if docker ps | grep -q ollama-model-loader; then
    echo -e "${YELLOW}Using ollama-model-loader to query Ollama...${NC}"
    
    # List models
    echo -e "${GREEN}Models available in Ollama:${NC}"
    docker exec $(docker ps -q -f name=ollama-model-loader) curl -s http://ollama:11434/api/tags | python3 -m json.tool 2>/dev/null || echo "Could not parse response as JSON"
    
    # Additional information
    echo ""
    echo -e "${YELLOW}To test a model:${NC}"
    echo "docker exec \$(docker ps -q -f name=ollama-model-loader) curl -s -X POST http://ollama:11434/api/generate -d '{\"model\": \"MODEL_NAME\", \"prompt\": \"Hello, how are you?\"}'"
    echo ""
    echo -e "${YELLOW}To download a model:${NC}"
    echo "docker exec \$(docker ps -q -f name=ollama-model-loader) curl -s -X POST http://ollama:11434/api/pull -d '{\"name\": \"MODEL_NAME\"}'"
else
    echo -e "${YELLOW}ollama-model-loader is not running.${NC}"
    echo "Using a temporary container to query Ollama..."
    
    # Get the network ollama is connected to
    NETWORK=$(docker inspect ollama --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}')
    
    if [ -z "$NETWORK" ]; then
        echo -e "${RED}Error: Could not determine the Docker network.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Models available in Ollama:${NC}"
    docker run --rm --network=$NETWORK curlimages/curl curl -s http://ollama:11434/api/tags | python3 -m json.tool 2>/dev/null || echo "Could not parse response as JSON"
    
    echo ""
    echo -e "${YELLOW}To start the model loader for easier access:${NC}"
    echo "docker-compose up -d ollama-model-loader"
    
    echo ""
    echo -e "${YELLOW}To download deepseek-r1:8b model:${NC}"
    echo "docker run --rm --network=$NETWORK curlimages/curl curl -s -X POST http://ollama:11434/api/pull -d '{\"name\": \"deepseek-r1:8b\"}'"
    
    echo ""
    echo -e "${YELLOW}To download BGE embeddings model:${NC}"
    echo "docker run --rm --network=$NETWORK curlimages/curl curl -s -X POST http://ollama:11434/api/pull -d '{\"name\": \"bge-large:latest\"}'"
fi
