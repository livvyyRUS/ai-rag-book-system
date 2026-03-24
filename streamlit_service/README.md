# Streamlit Service 🎨

Web UI for the AI RAG Book System built with Streamlit.

## 📖 Description

Streamlit Service provides a user-friendly web interface for:
- User registration and authentication
- Document upload and management
- Chat with documents using RAG technology

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Streamlit Service                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Auth      │  │   File      │  │    Chat     │     │
│  │   System    │  │   Manager   │  │   Interface │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
│   PostgreSQL    │ │    Minio     │ │  RAG Service │
│   (Users)       │ │   (Files)    │ │   (FastAPI)  │
└─────────────────┘ └──────────────┘ └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for dependencies)
- RAG Service running

### Installation

1. **Install dependencies:**
```bash
cd streamlit_service
uv sync
```

2. **Create `.env` file in the project root:**
```env
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-here

# Database Configuration
DATABASE_URL=postgres://user:password@localhost:5432/bookdb

# RAG Service Configuration
RAG_API_URL=http://localhost:8000/api/rag

# Minio Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
```

3. **Start dependencies (PostgreSQL, Minio, RAG Service):**
```bash
docker-compose up -d postgres minio rag_service
```

4. **Run Streamlit:**
```bash
streamlit run main.py
```

5. **Open in browser:**
```
http://localhost:8501
```

## 🐳 Docker

### Build and Run

```bash
# Build image
docker-compose build streamlit_service

# Run service
docker-compose up -d streamlit_service
```

### Logs

```bash
docker-compose logs -f streamlit_service
```

## 🎯 Features

### Authentication

- **Registration**: Create new user accounts
- **Login**: Secure authentication with JWT tokens
- **Session Management**: Persistent sessions across page reloads
- **Logout**: Secure session cleanup

### File Management

- **Upload**: Upload multiple documents (PDF, TXT, DOCX, MD)
- **View**: List all uploaded files
- **Delete**: Remove unwanted files
- **Processing**: Automatic document processing and vectorization

### Chat Interface

- **Ask Questions**: Natural language queries about documents
- **AI Responses**: LLM-powered answers with citations
- **History**: Conversation history within session
- **Clear History**: Reset conversation context

## 📁 Project Structure

```
streamlit_service/
├── main.py                 # Main Streamlit application
├── database.py             # Database operations (Tortoise ORM)
├── models.py               # Database models (User)
├── jwt_tool.py             # JWT token utilities
├── rag_client.py           # RAG Service API client
├── minio_client.py         # Minio storage client
├── test_auth.py            # Authentication tests
├── Dockerfile              # Docker configuration
├── pyproject.toml          # Python dependencies
├── uv.lock                 # Dependency lock file
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | Secret key for JWT tokens | `secret_key` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:password@localhost:5432/streamlit_db` |
| `RAG_API_URL` | RAG Service API URL | `http://localhost:8000/api/rag` |
| `MINIO_ENDPOINT` | Minio server endpoint | `localhost:9000` |
| `MINIO_ACCESS_KEY` | Minio access key | `minioadmin` |
| `MINIO_SECRET_KEY` | Minio secret key | `minioadmin` |
| `MINIO_SECURE` | Use HTTPS for Minio | `false` |

### Database Configuration

The service uses **Tortoise ORM** with PostgreSQL:

```python
# database.py
await Tortoise.init(
    db_url="postgres://user:password@localhost:5432/bookdb",
    modules={"models": ["models"]},
)
```

### JWT Configuration

Tokens are valid for **1 hour** by default:

```python
# jwt_tool.py
class JWTPayload(BaseModel):
    user_id: str
    exp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
```

## 🎨 Pages

### 1. Authentication Page

**Tabs:**
- **Вход (Login)**: Enter credentials to access your account
- **Регистрация (Register)**: Create a new account

**Features:**
- Password validation (min 6 characters)
- Duplicate username check
- Automatic JWT token generation on login

### 2. Upload Files Page

**Features:**
- Multi-file upload
- File type validation (PDF, TXT, DOCX, MD)
- Progress indicators
- Automatic ChromaDB generation after upload

**Usage:**
```python
uploaded_files = st.file_uploader(
    "Выберите файлы для загрузки",
    type=["pdf", "txt", "docx", "md"],
    accept_multiple_files=True
)
```

### 3. Manage Files Page

**Features:**
- List all uploaded files
- Delete files with confirmation
- File count display

### 4. Chat Page

**Features:**
- Chat interface with message history
- Real-time AI responses
- Error handling
- Clear history button

**Usage:**
```python
if prompt := st.chat_input("Введите ваш вопрос..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    result = run_async(rag_client.chat(prompt))
    st.session_state["messages"].append({"role": "assistant", "content": result.text})
```

## 📡 API Client

### RAGClient

Python client for RAG Service API:

```python
from rag_client import RAGClient

rag_client = RAGClient(
    jwt_token="your-jwt-token",
    user_id="user-username"
)

# Generate ChromaDB
result = await rag_client.generate_chroma_db()

# Chat
result = await rag_client.chat("Your question here")
```

### MinioClient

File storage operations:

```python
from minio_client import upload_file, list_files, delete_file, get_bucket_name

bucket_name = get_bucket_name("username")  # Returns "user-username"

# Upload
upload_file(bucket_name, "file.pdf", file_bytes)

# List
files = list_files(bucket_name)

# Delete
delete_file(bucket_name, "file.pdf")
```

## 🔐 Security

### JWT Authentication

- Tokens are stored in session state and query params
- Automatic token validation on each request
- Token expiration: 1 hour
- Secure password hashing with bcrypt

### User Isolation

- Each user has isolated bucket in Minio
- User ID format: `user-{username}`
- Database queries filtered by user

### Input Validation

- File type validation
- Password strength requirements
- Username uniqueness check

## 🧪 Testing

### Run Tests

```bash
# Authentication tests
python test_auth.py
```

### Manual Testing

1. **Registration Flow:**
   - Register new user
   - Verify user created in database
   - Login with credentials

2. **File Upload:**
   - Upload test PDF/TXT file
   - Verify file in Minio console
   - Check ChromaDB generation

3. **Chat:**
   - Ask question about uploaded document
   - Verify response accuracy
   - Test conversation history

## 🐛 Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
docker exec -it postgres_db psql -U user -d bookdb
```

### RAG Service Unavailable

```bash
# Check RAG service status
docker-compose ps rag_service

# View RAG logs
docker-compose logs rag_service

# Test API directly
curl http://localhost:8000/api/rag
```

### Minio Connection Error

```bash
# Check Minio status
docker-compose ps minio

# Access Minio console
# http://localhost:9001

# Verify credentials
```

### JWT Token Expired

- Token expires after 1 hour
- Logout and login again
- Token automatically refreshed on login

### Session Lost on Refresh

- Check query params are preserved
- Verify JWT_SECRET_KEY is consistent
- Clear browser cache and try again

## 📊 Performance

| Operation | Average Time |
|-----------|-------------|
| User Registration | < 1 sec |
| User Login | < 1 sec |
| File Upload (10 MB) | 2-5 sec |
| ChromaDB Generation | 30-60 sec |
| Chat Response | 3-10 sec |

## 🔄 Session Management

### Session State

```python
st.session_state["authenticated"] = True
st.session_state["username"] = "username"
st.session_state["user_id"] = "user-username"
st.session_state["jwt_token"] = "jwt-token"
st.session_state["messages"] = [...]  # Chat history
```

### Query Params

Session persists across page reloads via query params:
```
?jwt_token=xxx&username=xxx&user_id=xxx
```

## 🤝 Integration with RAG Service

### API Endpoints Used

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload_books` | POST | Upload documents |
| `/generate_chroma_db` | POST | Generate vector DB |
| `/chat` | GET | Chat with documents |
| `/clear_history` | POST | Clear chat history |

### Error Handling

```python
try:
    result = await rag_client.chat(prompt)
except Exception as e:
    st.error(f"Ошибка при получении ответа: {e}")
    st.session_state["messages"].append({
        "role": "assistant",
        "content": "Извините, произошла ошибка."
    })
```

## 📝 Code Examples

### User Registration

```python
from database import add_user

success = await add_user("newuser", "password123")
if success:
    st.success("Регистрация успешна!")
else:
    st.error("Пользователь уже существует")
```

### File Upload

```python
from minio_client import create_bucket_if_not_exists, upload_file

bucket_name = get_bucket_name(username)
create_bucket_if_not_exists(bucket_name)

for file in uploaded_files:
    upload_file(bucket_name, file.name, file.getvalue())
```

### Chat with RAG

```python
from rag_client import RAGClient

rag_client = RAGClient(jwt_token, user_id)
result = await rag_client.chat("What is the main theme?")
st.write(result.text)
```

## 🛠️ Development

### Local Development

```bash
# Install dependencies
uv sync

# Run with auto-reload
streamlit run main.py --server.head true

# Run on specific port
streamlit run main.py --server.port 8501
```

### Docker Development

```bash
# Build image
docker build -t streamlit-service .

# Run container
docker run -p 8501:8501 --env-file .env streamlit-service
```

## 📄 License

MIT License
