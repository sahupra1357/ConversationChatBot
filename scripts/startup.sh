#!/bin/bash

echo "Setting up ConversationChatBot with Ollama and DeepSeek Coder..."

# Check if docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    
    # Prompt for configuration
    read -p "Do you want to use Ollama with DeepSeek (local) or OpenAI (cloud)? [ollama/openai]: " llm_choice
    
    if [ "$llm_choice" = "openai" ]; then
        # Configure for OpenAI
        sed -i '' 's/LLM_PROVIDER=ollama/LLM_PROVIDER=openai/g' .env
        read -p "Enter your OpenAI API key: " openai_key
        sed -i '' "s/OPENAI_API_KEY=your_openai_api_key/OPENAI_API_KEY=$openai_key/g" .env
    else
        # Configure for Ollama
        sed -i '' "s/OLLAMA_BASE_URL=http:\/\/localhost:11434/OLLAMA_BASE_URL=http:\/\/ollama:11434/g" .env
    fi
else
    echo ".env file already exists. Using existing configuration."
fi

# Start the services
echo "Starting Docker services..."

# Determine the platform
if [[ $(uname -m) == 'arm64' ]]; then
    # This is Apple Silicon
    echo "Detected Apple Silicon (M-series) Mac"
    export OLLAMA_PLATFORM="linux/arm64"
    
    # # Add platform to .env file if using Ollama
    # if grep -q "LLM_PROVIDER=ollama" .env; then
    #     echo "OLLAMA_PLATFORM=linux/arm64" >> .env
    # fi
else
    # This is Intel/AMD architecture
    echo "Detected Intel/AMD architecture"
    export OLLAMA_PLATFORM="linux/amd64"
    
    # Check for NVIDIA GPU
    if command -v nvidia-smi &> /dev/null; then
        echo "NVIDIA GPU detected. Will use GPU acceleration."
    else
        echo "No NVIDIA GPU detected. Ollama will run on CPU only (slower)."
        echo "Consider using a smaller model or OpenAI for better performance."
    fi
fi

docker compose down

docker rmi $(docker images -q) -f

docker volume rm $(docker volume ls -q) -f

# Determine which profile to use based on LLM_PROVIDER
if grep -q "LLM_PROVIDER=ollama" .env; then
    echo "Using Ollama as LLM provider. The DeepSeek Coder model will be downloaded automatically."
    docker-compose --profile ollama up -d
else
    echo "Using OpenAI as LLM provider."
    docker-compose up -d
fi

echo "Setup complete! Your ConversationChatBot is now running."
echo "- Frontend: http://localhost:5173"
echo "- Backend API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"
