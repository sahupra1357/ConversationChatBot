# ConversationChatBot

A full-stack AI-powered chatbot application with real-time research capabilities using the arXiv API.

## 🚀 Features

- **AI-Powered Conversations**: Real-time chat with advanced language model capabilities
- **Research Integration**: Automatically searches arXiv for relevant research papers
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
- **OpenAI** for embeddings and completions

### Infrastructure
- **Docker** and **Docker Compose** for containerization
- **PostgreSQL** for database storage
- **Alembic** for database migrations

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)
- OpenAI API key

## 🚀 Getting Started

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ConversationChatBot.git
   cd ConversationChatBot
   ```

2. Set up environment variables:
   - Create a `.env` file in the root directory (see `.env.example` for reference)
   - Add your OpenAI API key

3. Start the application:
   ```bash
   docker-compose up
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

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
5. OpenAI generates a coherent response based on the retrieved information

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
│   │   ├── routes/          # API endpoints
│   │   ├── models/          # Database models
│   │   └── ...
│   └── ...
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── api/             # API client functions
│   │   ├── hooks/           # Custom React hooks
│   │   └── ...
│   └── ...
└── docker-compose.yml       # Docker configuration
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [OpenAI](https://openai.com/) for providing the language model capabilities
- [arXiv](https://arxiv.org/) for the research paper database
- [LlamaIndex](https://www.llamaindex.ai/) for the RAG framework
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [React](https://reactjs.org/) for the frontend framework