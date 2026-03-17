# RAG Service

RAG (Retrieval-Augmented Generation) microservice for book question-answering system.

## LLM Configuration

You can choose between two LLM providers: **Ollama** (local) or **OpenRouter** (cloud API).

### Option 1: Ollama (Local, Free)

1. Install [Ollama](https://ollama.ai)
2. Pull a model:
   ```bash
   ollama pull qwen3:4b-instruct-2507-q4_K_M
   ```
3. In `.env` file, set:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=qwen3:4b-instruct-2507-q4_K_M
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   ```

### Option 2: OpenRouter (Cloud, Free Models Available)

1. Register at [https://openrouter.ai](https://openrouter.ai)
2. Get your API key (no credit card required for free models)
3. In `.env` file, set:
   ```env
   LLM_PROVIDER=openrouter
   OPENROUTER_API_KEY=your_api_key_here
   OPENROUTER_MODEL=openrouter/free
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   ```

#### Available Free Models on OpenRouter

You can use `openrouter/free` router or specify a specific free model:
- `meta-llama/llama-3-8b-instruct:free`
- `google/gemma-7b-it:free`
- `mistralai/mistral-7b-instruct:free`
- `microsoft/phi-3-mini-128k-instruct:free`

See [OpenRouter models](https://openrouter.ai/models) for the full list.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider: `ollama` or `openrouter` | `ollama` |
| `LLM_TEMPERATURE` | Model temperature (0.0-1.0) | `0.7` |
| `OLLAMA_MODEL` | Ollama model name | `qwen3:4b-instruct-2507-q4_K_M` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://host.docker.internal:11434` |
| `OPENROUTER_API_KEY` | OpenRouter API key | (required for openrouter) |
| `OPENROUTER_MODEL` | OpenRouter model name | `openrouter/free` |
| `OPENROUTER_BASE_URL` | OpenRouter API URL | `https://openrouter.ai/api/v1` |
| `HF_EMBEDDINGS_MODEL` | HuggingFace embeddings model | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |

## Installation

```bash
uv sync
```

## Running

```bash
uv run uvicorn app.main:app --reload
```

## API Endpoints

- `POST /api/rag/upload_books` - Upload books (.txt, .pdf)
- `POST /api/rag/generate_chroma_db` - Generate vector database
- `GET /api/rag/similarity_search` - Semantic search
- `GET /api/rag/similarity_search_with_scores` - Search with relevance scores
- `GET /api/rag/similarity_search_mmr` - Search with MMR (diversity)
- `GET /api/rag/chat` - Chat with documents (RAG + LLM)
