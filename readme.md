# ConversationChatBot

A full-stack AI-powered chatbot application with real-time research capabilities using the arXiv API, with support for local LLMs through Ollama.

## 🚀 Features

- **AI-Powered Conversations**: Real-time chat with advanced language model capabilities
- **Research Integration**: Automatically searches arXiv for relevant research papers
- **Local LLM Support**: Run entirely locally with Ollama for privacy and no API costs
- **BGE-Large Embeddings**: High-quality open-source embeddings model
- **Conversation Management**: Create and manage multiple conversations
- **Responsive UI**: Clean and modern interface that works on all devices
- **Persistent Storage**: All conversations are stored in a database for future reference

## 🏗️ Tech Stack

### Frontend
- **React** with **TypeScript**
- **Tailwind CSS** for styling
- **React Query** for data fetching and state management
- **Vite** for fast development and building

### Backend
- **FastAPI** for high-performance API endpoints
- **SQLModel** (SQLAlchemy + Pydantic) for database models
- **LlamaIndex** for RAG (Retrieval Augmented Generation)
- **Qdrant** for vector storage and similarity search
- **BGE-Large** for embeddings (free, open-source alternative)
- **Ollama** for local LLM support (DeepSeek Coder and DeepSeek R1 models)

### Infrastructure
- **Docker** and **Docker Compose** for containerization
- **PostgreSQL** for database storage
- **Alembic** for database migrations

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)
- OpenAI API key (optional - not needed with BGE embeddings and Ollama)
- GPU recommended for local LLM usage (but works on CPU)

## 🚀 Getting Started

### Quick Setup (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ConversationChatBot.git
   cd ConversationChatBot
   ```

2. Run the startup script:
   ```bash
   ./scripts/startup.sh
   ```
   This script will:
   - Create a `.env` file from the example
   - Ask if you want to use Ollama (local) or OpenAI (cloud)
   - Start all services with Docker Compose
   - Download the necessary models if using Ollama
   - Provide URLs to access the application

### Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ConversationChatBot.git
   cd ConversationChatBot
   ```

2. Set up environment variables:
   - Create a `.env` file in the root directory (see `.env.example` for reference)
   - Add your OpenAI API key (if using OpenAI) or set `LLM_PROVIDER=ollama` to use local models

3. Start the application:
   ```bash
   # If using OpenAI:
   docker-compose up -d
   
   # If using Ollama with DeepSeek:
   docker-compose --profile ollama up -d
   ```

4. Download the Ollama models (if using Ollama):
   ```bash
   # Start the model loader to download DeepSeek and BGE-Large
   docker-compose up -d ollama-model-loader
   
   # Check if models are downloaded
   ./scripts/check_ollama_models.sh
   ```

5. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Hardware Support

The application is designed to work across different hardware configurations:

#### Apple Silicon (M1/M2/M3/M4)
- Automatically detected by the startup script
- Uses Metal API for GPU acceleration
- Set `OLLAMA_PLATFORM=linux/arm64` in your `.env` file
- Great performance for local LLM inference

#### NVIDIA GPUs
- Automatically detected by the startup script
- Requires NVIDIA drivers and NVIDIA Container Toolkit
- Provides the best performance for local LLM inference
- GPU acceleration enabled automatically

#### Systems without GPU
- Falls back to CPU-only mode
- Will be significantly slower for local inference
- Consider using smaller models or OpenAI for better performance

### Supported Models

#### LLM Models (via Ollama)
- **DeepSeek Coder** (`deepseek-coder:latest`): Optimized for code-related tasks
- **DeepSeek R1 8B** (`deepseek-r1:8b`): General purpose model, good balance of performance and quality
- Any other model supported by Ollama can be used by changing `OLLAMA_MODEL` in your `.env` file

#### Embedding Models
- **BGE-Large** (`bge-large:latest`): High-quality open-source embedding model
- **OpenAI Embeddings** (`text-embedding-3-small`): Available when using OpenAI as provider

### Troubleshooting

#### Connection Issues with Ollama
If you encounter connection errors when trying to use Ollama:

1. Make sure Ollama container is running:
   ```bash
   docker ps | grep ollama
   ```

2. Check if the models are properly downloaded:
   ```bash
   ./scripts/check_ollama_models.sh
   ```

3. Verify Ollama is accessible from the backend:
   ```bash
   # The backend container should connect to Ollama using:
   OLLAMA_BASE_URL=http://ollama:11434
   ```

4. If running a local Ollama service on your host machine, ensure it's not conflicting with the Docker container:
   ```bash
   # Stop the local Ollama service
   sudo pkill ollama
   # or
   sudo launchctl unload ~/Library/LaunchAgents/com.ollama.ollama.plist
   ```

#### Model Download Issues
If models aren't downloading properly:

1. Manually download using the ollama-model-loader:
   ```bash
   docker-compose up -d ollama-model-loader
   ```

2. Check the logs for any errors:
   ```bash
   docker-compose logs ollama-model-loader
   ```

3. Manually trigger a model download:
   ```bash
   docker exec $(docker ps -q -f name=ollama-model-loader) curl -X POST http://ollama:11434/api/pull -d '{"name": "deepseek-r1:8b"}'
   ```

### Local Development

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the backend directory
   - Configure Ollama or OpenAI settings as needed

5. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file with:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

## 🧠 How It Works

### RAG System with arXiv Integration

The application uses a Retrieval Augmented Generation (RAG) system to provide research-backed responses:

1. User queries are analyzed to identify research topics
2. The system searches arXiv for relevant papers
3. Paper abstracts and content are vectorized and stored in Qdrant
4. LlamaIndex retrieves the most relevant papers for the query
5. An LLM (OpenAI or local DeepSeek model via Ollama) generates a coherent response based on the retrieved information

### Embedding Models

The application uses vector embeddings to represent and search text:

1. **BGE-Large**: A high-quality open-source embedding model
   - Used for converting paper content into vector representations
   - Available through both HuggingFace and Ollama
   - 1024-dimensional vectors for efficient semantic search

2. The embedding process:
   - Paper text is chunked into manageable segments
   - Each chunk is converted to a vector using BGE-Large
   - Vectors are stored in Qdrant for fast similarity search
   - User queries are also embedded for matching against stored vectors

### LLM Provider Options

The application supports multiple LLM providers:

1. **OpenAI**: Cloud-based GPT models (requires API key)
   - Set `LLM_PROVIDER=openai` in your `.env` file
   - Configure `OPENAI_MODEL` and other parameters

2. **Ollama**: Local LLM for privacy and cost savings
   - Set `LLM_PROVIDER=ollama` in your `.env` file
   - Configure `OLLAMA_MODEL` (options include `deepseek-coder:latest` or `deepseek-r1:8b`)
   - Models are downloaded and managed through Ollama
   - GPU recommended for optimal performance

### Conversation Management

- Conversations are stored in a PostgreSQL database
- Each conversation can be resumed at any time
- Message history provides context for improved responses
- API endpoints handle creation, retrieval, and management of conversations

## 📝 API Documentation

The API documentation is available at `http://localhost:8000/docs` when the backend is running. Key endpoints include:

- `/chat`: Submit a message and receive an AI response
- `/conversations`: Manage conversation threads
- `/messages`: Retrieve and create messages

## 🧩 Project Structure

```
ConversationChatBot/
├── backend/                 # FastAPI backend
│   ├── alembic/             # Database migrations
│   ├── app/                 # Application code
│   │   ├── arxiv_rag.py     # ArXiv integration and RAG system
│   │   ├── llm_providers.py # LLM provider abstraction
│   │   ├── routes/          # API endpoints
│   │   ├── config.py        # Configuration settings
│   │   └── ...
│   └── ...
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── api/             # API client functions
│   │   ├── hooks/           # Custom React hooks
│   │   └── ...
│   └── ...
├── scripts/                 # Utility scripts
│   ├── startup.sh           # Quick setup script
│   ├── download_ollama_models.sh # Script to download models
│   ├── check_ollama_models.sh # Script to check Ollama models
│   ├── check_ollama.sh      # Interactive Ollama management tool
│   └── ...
└── docker-compose.yml       # Docker configuration
```

## 🛠️ Configuration Options

### Environment Variables

Key configuration options in the `.env` file:

#### LLM Settings
- `LLM_PROVIDER`: Choose between `openai` or `ollama`
- `OLLAMA_MODEL`: The model to use with Ollama (e.g., `deepseek-r1:8b`)
- `OLLAMA_BASE_URL`: URL to connect to Ollama (default: `http://ollama:11434`)
- `LLM_TEMPERATURE`: Controls randomness in responses (0-1)
- `LLM_MAX_TOKENS`: Maximum tokens in responses

#### Embedding Settings
- `EMBED_MODEL`: Embedding model to use (e.g., `bge-large:latest`)
- `VECTOR_DIM`: Dimension of vectors (1024 for BGE-Large)

#### Database Settings
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, etc.: Database connection details

#### ArXiv Settings
- `MAX_RESULTS`: Number of results to fetch from arXiv
- `SHORT_SUMMARY_LENGTH`: Length of paper summaries

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Ollama](https://ollama.ai/) for local LLM support
- [DeepSeek](https://github.com/deepseek-ai/DeepSeek-Coder) for the open-source code model
- [BGE](https://github.com/FlagOpen/BAAI) for the embedding model
- [arXiv](https://arxiv.org/) for the research paper database
- [LlamaIndex](https://www.llamaindex.ai/) for the RAG framework
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [React](https://reactjs.org/) for the frontend framework
