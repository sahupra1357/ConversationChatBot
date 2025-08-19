#!/bin/bash

echo "Starting to download models to Ollama..."

# Get the Ollama host - use the environment variable if set, otherwise default to localhost
OLLAMA_HOST=${OLLAMA_HOST:-localhost}
OLLAMA_PORT=${OLLAMA_PORT:-11434}
OLLAMA_URL="http://${OLLAMA_HOST}:${OLLAMA_PORT}"
#EMBED_MODEL=${EMBED_MODEL:-BAAI/bge-large-en:latest}

echo "Using Ollama at ${OLLAMA_URL}"

# Maximum number of retry attempts - can be overridden with environment variable
MAX_RETRIES=${MAX_RETRIES:-30}
RETRY_INTERVAL=${RETRY_INTERVAL:-15}

echo "Will retry up to $MAX_RETRIES times with $RETRY_INTERVAL second intervals"

# Function to check if Ollama is available
check_ollama() {
    local response
    response=$(curl -s "${OLLAMA_URL}/api/tags" 2>&1) || return 1
    
    # Check if the response is valid JSON (contains [ or {)
    if [[ "$response" == *"["* ]] || [[ "$response" == *"{"* ]]; then
        return 0
    else
        return 1
    fi
}

# Make sure Ollama service is running
for ((i=1; i<=MAX_RETRIES; i++)); do
    echo "Attempt $i/$MAX_RETRIES: Checking if Ollama is available..."
    
    if check_ollama; then
        echo "Ollama is available!"
        break
    else
        echo "Ollama is not yet available. Waiting ${RETRY_INTERVAL} seconds..."
        sleep ${RETRY_INTERVAL}
        
        # If we've reached the maximum number of retries
        if [ $i -eq $MAX_RETRIES ]; then
            echo "WARNING: Ollama service did not become available after ${MAX_RETRIES} attempts."
            echo "Will attempt to download model anyway, but it might fail."
        fi
    fi
done

# Pull the model with retries
download_model() {
    local model=$1
    local retries=5
    local wait_time=30
    
    echo "Downloading model: $model (this may take a while)..."
    
    for ((j=1; j<=$retries; j++)); do
        echo "Download attempt $j/$retries for $model..."
        
        # Attempt to pull the model
        local pull_result
        pull_result=$(curl -s -X POST "${OLLAMA_URL}/api/pull" -d "{\"name\": \"$model\"}" 2>&1)
        
        # Check if the pull was successful
        if [[ "$pull_result" == *"\"status\":\"success\""* ]] || [[ "$pull_result" == *"already exists"* ]]; then
            echo "Successfully downloaded $model!"
            return 0
        else
            echo "Download attempt $j failed. Response: $pull_result"
            if [ $j -lt $retries ]; then
                echo "Waiting $wait_time seconds before next attempt..."
                sleep $wait_time
            fi
        fi
    done
    
    echo "WARNING: Failed to download $model after $retries attempts."
    return 1
}

# Try to download the model
MODEL_NAME="deepseek-coder:latest"
download_model "$MODEL_NAME"
echo "Model $MODEL_NAME download process complete."

MODEL_NAME="deepseek-r1:8b"
download_model "$MODEL_NAME"
echo "Model $MODEL_NAME download process complete."

# Also download the BGE-Large embedding model
EMBED_MODEL="bge-large:latest"
echo "Now downloading BGE-Large embedding model..."
download_model "$EMBED_MODEL"

echo "Model download process complete."
echo "To use Ollama, set LLM_PROVIDER=ollama in your .env file."
echo "To use BGE-Large embeddings, set EMBED_MODEL=bge-large in your .env file."