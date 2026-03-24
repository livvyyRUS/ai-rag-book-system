# RAG Service 📚

Микросервис для обработки документов и генерации ответов на вопросы с использованием RAG (Retrieval-Augmented Generation).

## 📖 Описание

RAG Service — это основной компонент системы, который отвечает за:
- Загрузку и обработку документов (PDF)
- Создание векторных представлений текста
- Семантический поиск по документам
- Генерацию ответов с использованием языковых моделей

> **Важно:** Система поддерживает загрузку документов **только в формате PDF**. Документы на любом языке поддерживаются.

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────┐
│                  RAG Service                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   RAGAgent  │  │  TalkAgent  │  │  RAG Core   │ │
│  │  (поиск)    │  │  (ответы)   │  │  (векторы)  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
│   ChromaDB      │ │   Ollama/    │ │    Minio     │
│  (векторная БД) │ │   OpenRouter │ │  (файлы)     │
└─────────────────┘ └──────────────┘ └──────────────┘
```

## 🚀 Быстрый старт

### Требования

- Python 3.11+
- Docker и Docker Compose (для запуска зависимостей)
- 4+ ГБ ОЗУ

### Установка

1. **Установите зависимости:**
```bash
cd rag_service
uv sync
```

2. **Создайте файл `.env` в корне проекта:**
```env
# JWT
JWT_SECRET_KEY=ваш-секретный-ключ

# Minio
MINIO_USER=minioadmin
MINIO_PASSWORD=minioadmin
MINIO_HOST=localhost

# LLM Provider (ollama или openrouter)
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b-instruct
OLLAMA_BASE_URL=http://localhost:11434

# Или для OpenRouter:
# LLM_PROVIDER=openrouter
# OPENROUTER_API_KEY=ваш-api-ключ
# OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct:free

# HuggingFace Embeddings
HF_EMBEDDINGS_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

3. **Запустите зависимости (Minio, Ollama):**
```bash
docker-compose up -d minio ollama
```

4. **Запустите RAG сервис:**
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Откройте Swagger UI:**
```
http://localhost:8000/docs
```

## 🔧 Настройка LLM

### Вариант 1: Ollama (локально, бесплатно)

```bash
# Установите Ollama: https://ollama.ai
ollama pull qwen2.5:7b-instruct
```

В `.env`:
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b-instruct
OLLAMA_BASE_URL=http://localhost:11434
```

### Вариант 2: OpenRouter (облако, есть бесплатные модели)

1. Зарегистрируйтесь на [openrouter.ai](https://openrouter.ai)
2. Получите API ключ

В `.env`:
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

## 📡 API Endpoints

### Аутентификация

Все запросы требуют JWT токен. Передавайте его в параметре `jwt_token`.

### Загрузка документов

**POST** `/api/rag/upload_books`

Загружает документы пользователя в хранилище.

```bash
curl -X POST "http://localhost:8000/api/rag/upload_books?user_id=user-default&jwt_token=YOUR_TOKEN" \
  -F "files=@book1.pdf" \
  -F "files=@book2.pdf"
```

**Поддерживаемые форматы:** `.pdf`

**Ответ:**
```json
{
  "status": "Загружено файлов: 2"
}
```

### Генерация векторной базы

**POST** `/api/rag/generate_chroma_db`

Создаёт векторное представление загруженных документов.

```bash
curl -X POST "http://localhost:8000/api/rag/generate_chroma_db?user_id=user-default&jwt_token=YOUR_TOKEN"
```

**Ответ:**
```json
{
  "status": "ok"
}
```

### Семантический поиск

**GET** `/api/rag/similarity_search`

Поиск релевантных фрагментов по запросу.

```bash
curl "http://localhost:8000/api/rag/similarity_search?user_id=user-default&query=Кто такой Раскольников?&k=3&jwt_token=YOUR_TOKEN"
```

**Параметры:**
- `query` — текст запроса
- `k` — количество результатов (по умолчанию 3)
- `jwt_token` — JWT токен

**Ответ:**
```json
{
  "answers": [
    {
      "text": "Родион Романович Раскольников — бывший студент...",
      "title": "Преступление и наказание",
      "page": 15,
      "source_file": "crime_and_punishment.pdf"
    }
  ]
}
```

### Поиск с оценками релевантности

**GET** `/api/rag/similarity_search_with_scores`

Поиск с возвращением оценок релевантности.

```bash
curl "http://localhost:8000/api/rag/similarity_search_with_scores?user_id=user-default&query=Раскольников&k=3&jwt_token=YOUR_TOKEN"
```

**Ответ:**
```json
{
  "answers": [
    {
      "text": "Родион Романович Раскольников...",
      "title": "Преступление и наказание",
      "page": 15,
      "source_file": "crime_and_punishment.pdf",
      "score": 0.89
    }
  ]
}
```

### Поиск с MMR (Maximal Marginal Relevance)

**GET** `/api/rag/similarity_search_mmr`

Поиск с балансировкой между релевантностью и разнообразием.

```bash
curl "http://localhost:8000/api/rag/similarity_search_mmr?user_id=user-default&query=Раскольников&k=3&lambda_mult=0.5&jwt_token=YOUR_TOKEN"
```

**Параметры:**
- `lambda_mult` — баланс (0.0 = разнообразие, 1.0 = релевантность)

### Чат с документами

**GET** `/api/rag/chat`

Генерация ответа на вопрос с использованием RAG и LLM.

```bash
curl "http://localhost:8000/api/rag/chat?user_id=user-default&query=Кто такой Раскольников?&jwt_token=YOUR_TOKEN"
```

**Ответ:**
```json
{
  "status": "ok",
  "text": "Родион Романович Раскольников — главный герой романа...",
  "citations": [
    {
      "book": "Преступление и наказание",
      "location": "стр. 15",
      "text": "Родион Романович Раскольников — бывший студент..."
    },
    {
      "book": "Преступление и наказание",
      "location": "стр. 45",
      "text": "Он был замкнут и угрюм..."
    }
  ]
}
```

### Очистка истории

**POST** `/api/rag/clear_history`

Очищает историю диалогов пользователя.

```bash
curl -X POST "http://localhost:8000/api/rag/clear_history" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-default", "jwt_token": "YOUR_TOKEN"}'
```

## 📁 Структура проекта

```
rag_service/
├── app/
│   ├── __init__.py
│   ├── main.py           # Точка входа FastAPI
│   ├── rag.py            # RAG логика (загрузка, векторы, поиск)
│   ├── files.py          # Работа с файлами (Minio)
│   ├── jwt.py            # JWT утилиты
│   ├── ai/
│   │   ├── llm.py        # LLM конфигурация
│   │   ├── get_session_history.py
│   │   ├── agents/
│   │   │   ├── rag_agent.py    # Агент поиска
│   │   │   └── talk_agent.py   # Агент генерации ответов
│   │   └── tools/
│   │       └── rag_tool.py     # Инструмент поиска для агента
│   └── api/
│       ├── api.py        # API endpoints
│       └── models.py     # Pydantic модели
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

## 🧪 Тестирование

```bash
# Запуск тестов (если есть)
uv run pytest

# Тестирование API через curl
./test.py
```

## 🔐 Безопасность

- JWT токены для аутентификации
- Изоляция данных по user_id
- Валидация типов файлов (только PDF)
- Ограничение размера файлов

## 📊 Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `JWT_SECRET_KEY` | Секретный ключ для JWT | (требуется) |
| `MINIO_USER` | Пользователь Minio | `minioadmin` |
| `MINIO_PASSWORD` | Пароль Minio | `minioadmin` |
| `MINIO_HOST` | Хост Minio | `localhost` |
| `LLM_PROVIDER` | Провайдер LLM (`ollama` или `openrouter`) | `ollama` |
| `OLLAMA_MODEL` | Модель Ollama | `qwen2.5:7b-instruct` |
| `OLLAMA_BASE_URL` | URL Ollama сервера | `http://localhost:11434` |
| `OPENROUTER_API_KEY` | API ключ OpenRouter | (требуется для openrouter) |
| `OPENROUTER_MODEL` | Модель OpenRouter | `meta-llama/llama-3-8b-instruct:free` |
| `OPENROUTER_BASE_URL` | URL API OpenRouter | `https://openrouter.ai/api/v1` |
| `HF_EMBEDDINGS_MODEL` | Модель эмбеддингов | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |

## 🐛 Решение проблем

### Ошибка "База данных не найдена"
```bash
# Сначала загрузите файлы и сгенерируйте ChromaDB
curl -X POST "http://localhost:8000/api/rag/generate_chroma_db?user_id=user-default&jwt_token=YOUR_TOKEN"
```

### Ollama не отвечает
```bash
# Проверьте статус Ollama
docker-compose ps ollama

# Перезапустите Ollama
docker-compose restart ollama

# Проверьте логи
docker-compose logs ollama
```

### Недостаточно памяти
- Используйте меньшую модель (например, `qwen2.5:1.5b`)
- Увеличьте лимиты Docker
- Используйте облачный LLM (OpenRouter)

## 📈 Производительность

| Операция | Время (среднее) |
|----------|-----------------|
| Загрузка книги (300 стр.) | 5-10 сек |
| Генерация ChromaDB | 30-60 сек |
| Семантический поиск | 0,5-2 сек |
| Генерация ответа (LLM) | 3-10 сек |

## 🤝 Вклад в проект

1. Fork репозиторий
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в удалённый репозиторий (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

MIT License
