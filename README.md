# AI RAG Book System 📚

A microservices-based system for chatting with books and documents using RAG (Retrieval-Augmented Generation) technology.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AI RAG Book System                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐         ┌──────────────────────────────────┐ │
│  │  Streamlit       │  HTTP   │  RAG Service (FastAPI)           │ │
│  │  Service         │────────▶│  - Document Processing           │ │
│  │  (Port 8501)     │         │  - Vector Search                 │ │
│  │                  │         │  - LLM Integration               │ │
│  └──────────────────┘         └──────────────────────────────────┘ │
│         │                              │  │  │                      │
│         │                              │  │  │                      │
│         ▼                              ▼  │  │                      │
│  ┌──────────────────┐         ┌──────────────────────────────────┐ │
│  │  PostgreSQL      │         │  Minio          │  Ollama        │ │
│  │  (Users & Auth)  │         │  (File Storage) │  (LLM)         │ │
│  │  Port 5432       │         │  Port 9000      │  Port 11434    │ │
│  └──────────────────┘         └──────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
ai-rag-book-system/
├── docker-compose.yml          # Docker Compose configuration
├── .env                        # Environment variables (create from .env.example)
├── .gitignore
├── README.md                   # This file
│
├── rag_service/                # RAG Microservice (FastAPI)
│   ├── app/
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── api/               # API endpoints
│   │   ├── ai/                # AI/LLM integration
│   │   ├── rag.py             # RAG core logic
│   │   └── files.py           # File handling (Minio)
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── README.md
│
├── streamlit_service/          # Web UI (Streamlit)
│   ├── main.py                # Streamlit application
│   ├── database.py            # Database operations
│   ├── jwt_tool.py            # JWT authentication
│   ├── rag_client.py          # RAG Service client
│   ├── minio_client.py        # Minio client
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── README.md
│
├── pg_data/                    # PostgreSQL data (volume)
├── minio_data/                 # Minio data (volume)
├── hf_cache/                   # HuggingFace models cache
├── ollama_models/              # Ollama models cache
└── rag_data/                   # RAG processed data
```

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- **NVIDIA GPU** (optional, for better LLM performance)
- **8+ GB RAM** (16+ GB recommended)
- **Python 3.11+** (for local development)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-rag-book-system
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Copy example if available
cp .env.example .env
```

Edit `.env` with your settings:

```env
# ==================== JWT Configuration ====================
JWT_SECRET_KEY=your-super-secret-key-change-in-production

# ==================== PostgreSQL Configuration ====================
POSTGRES_USER=bookuser
POSTGRES_PASSWORD=bookpassword
POSTGRES_DB=bookdb

# ==================== Minio Configuration ====================
MINIO_USER=minioadmin
MINIO_PASSWORD=minioadmin
MINIO_HOST=minio

# ==================== LLM Configuration ====================
# Choose one: ollama or openrouter
LLM_PROVIDER=ollama

# For Ollama (local, free)
OLLAMA_MODEL=qwen2.5:7b-instruct

# For OpenRouter (cloud, API key required)
# LLM_PROVIDER=openrouter
# OPENROUTER_API_KEY=your-openrouter-api-key
# OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct:free

# ==================== Embeddings Configuration ====================
HF_EMBEDDINGS_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### 3. Start All Services

```bash
docker-compose up -d
```

Wait for all services to start (2-3 minutes for first run):

```bash
docker-compose ps
```

### 4. Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| **Streamlit UI** | http://localhost:8501 | Web interface |
| **RAG API** | http://localhost:8000/docs | API documentation |
| **Minio Console** | http://localhost:9001 | File storage UI |
| **Ollama** | http://localhost:11434 | LLM server |

## 📖 Usage Guide

### Step 1: Register an Account

1. Open http://localhost:8501
2. Click on "Регистрация" tab
3. Enter username and password (min 6 characters)
4. Click "Зарегистрироваться"

### Step 2: Login

1. Enter your credentials
2. Click "Войти"

### Step 3: Upload Documents

1. Navigate to "Загрузка файлов"
2. Select PDF, TXT, DOCX, or MD files
3. Click "Загрузить и обработать файлы"
4. Wait for processing to complete

### Step 4: Chat with Your Documents

1. Navigate to "Чат с ботом"
2. Ask questions about your documents
3. Get AI-powered answers with citations

### Step 5: Manage Files

1. Navigate to "Управление файлами"
2. View all uploaded files
3. Delete files you no longer need

## 🔧 Services Overview

### RAG Service (FastAPI)

The core service handling document processing and RAG operations.

**Key Features:**
- Document upload and processing (PDF, TXT, DOCX, MD)
- Vector embeddings generation
- Semantic search
- LLM-powered chat
- JWT authentication

**Documentation:** [`rag_service/README.md`](rag_service/README.md)

**API Endpoints:**
```bash
# Upload documents
POST /api/rag/upload_books

# Generate vector database
POST /api/rag/generate_chroma_db

# Semantic search
GET /api/rag/similarity_search?query=<your-query>&k=3

# Chat with documents
GET /api/rag/chat?query=<your-question>
```

### Streamlit Service

Web UI for user interaction.

**Key Features:**
- User registration and authentication
- File upload interface
- Document management
- Chat interface with RAG bot

**Documentation:** [`streamlit_service/README.md`](streamlit_service/README.md)

### PostgreSQL

User authentication and data storage.

- Port: `5432`
- Data volume: `./pg_data`

### Minio

Object storage for uploaded documents.

- Console: http://localhost:9001
- API: http://localhost:9000
- Data volume: `./minio_data`

### Ollama

Local LLM server.

- Port: `11434`
- Models volume: `./ollama_models`

## 🛠️ Development

### Running Services Individually

```bash
# Start only dependencies
docker-compose up -d postgres minio ollama

# Start RAG service locally
cd rag_service
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Streamlit locally
cd streamlit_service
uv sync
streamlit run main.py
```

### Building Images

```bash
docker-compose build
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f rag_service
```

### Stopping Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes (data will be lost!)
docker-compose down -v
```

## 🔐 Security

- **JWT Authentication**: All API requests require valid JWT tokens
- **User Isolation**: Each user's data is isolated by user_id
- **Password Hashing**: Passwords are hashed using bcrypt
- **Input Validation**: File types and sizes are validated

## ⚙️ Configuration Options

### LLM Providers

#### Option 1: Ollama (Local, Free)

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b-instruct
```

Recommended models:
- `qwen2.5:7b-instruct` - Good balance of speed and quality
- `qwen2.5:3b-instruct` - Faster, less RAM
- `llama3.2:3b-instruct` - Alternative option

#### Option 2: OpenRouter (Cloud, API Key)

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct:free
```

Get API key at: https://openrouter.ai

### Embedding Models

```env
HF_EMBEDDINGS_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Alternative models:
- `sentence-transformers/all-MiniLM-L6-v2` (English, faster)
- `intfloat/multilingual-e5-large` (Multilingual, better quality)

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild images
docker-compose up -d --build
```

### Ollama Model Download Fails

```bash
# Check Ollama logs
docker-compose logs ollama

# Manually pull model
docker exec -it ollama ollama pull qwen2.5:7b-instruct
```

### Out of Memory

- Use smaller LLM models (e.g., `qwen2.5:1.5b`)
- Increase Docker memory limits
- Use cloud LLM (OpenRouter)

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Minio Connection Issues

```bash
# Check Minio is running
docker-compose ps minio

# Access Minio console
# http://localhost:9001
```

## 📊 Performance Benchmarks

| Operation | Average Time |
|-----------|-------------|
| Book Upload (300 pages) | 5-10 sec |
| ChromaDB Generation | 30-60 sec |
| Semantic Search | 0.5-2 sec |
| Answer Generation (LLM) | 3-10 sec |

## 📝 API Documentation

Full API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Streamlit](https://streamlit.io/) - Data app framework
- [LangChain](https://python.langchain.com/) - LLM orchestration framework
- [Ollama](https://ollama.ai/) - Local LLM server
- [Minio](https://min.io/) - Object storage
- [ChromaDB](https://www.trychroma.com/) - Vector database

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation
- Review API documentation at http://localhost:8000/docs
