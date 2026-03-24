# AI RAG Book System 📚

Микросервисная система для общения с книгами и документами с использованием технологии RAG (Retrieval-Augmented Generation).

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AI RAG Book System                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐         ┌──────────────────────────────────┐ │
│  │  Streamlit       │  HTTP   │  RAG Service (FastAPI)           │ │
│  │  Service         │────────▶│  - Обработка документов          │ │
│  │  (Порт 8501)     │         │  - Векторный поиск               │ │
│  │                  │         │  - Интеграция с LLM              │ │
│  └──────────────────┘         └──────────────────────────────────┘ │
│         │                              │  │  │                      │
│         │                              │  │  │                      │
│         ▼                              ▼  │  │                      │
│  ┌──────────────────┐         ┌──────────────────────────────────┐ │
│  │  PostgreSQL      │         │  Minio          │  Ollama        │ │
│  │  (Пользователи)  │         │  (Хранилище)    │  (LLM)         │ │
│  │  Порт 5432       │         │  Порт 9000      │  Порт 11434    │ │
│  └──────────────────┘         └──────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 📁 Структура проекта

```
ai-rag-book-system/
├── docker-compose.yml          # Конфигурация Docker Compose
├── .env                        # Переменные окружения (создать из .env.example)
├── .gitignore
├── README.md                   # Этот файл
│
├── rag_service/                # RAG микросервис (FastAPI)
│   ├── app/
│   │   ├── main.py            # Точка входа FastAPI
│   │   ├── api/               # API эндпоинты
│   │   ├── ai/                # Интеграция с ИИ/LLM
│   │   ├── rag.py             # Основная логика RAG
│   │   └── files.py           # Работа с файлами (Minio)
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── README.md
│
├── streamlit_service/          # Веб-интерфейс (Streamlit)
│   ├── main.py                # Приложение Streamlit
│   ├── database.py            # Операции с базой данных
│   ├── jwt_tool.py            # JWT аутентификация
│   ├── rag_client.py          # Клиент для RAG сервиса
│   ├── minio_client.py        # Клиент для Minio
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── README.md
│
├── pg_data/                    # Данные PostgreSQL (том)
├── minio_data/                 # Данные Minio (том)
├── hf_cache/                   # Кэш моделей HuggingFace
├── ollama_models/              # Кэш моделей Ollama
└── rag_data/                   # Обработанные данные RAG
```

## 🚀 Быстрый старт

### Требования

- **Docker** и **Docker Compose** установлены
- **NVIDIA GPU** (опционально, для лучшей производительности LLM)
- **8+ ГБ ОЗУ** (рекомендуется 16+ ГБ)
- **Python 3.11+** (для локальной разработки)

### 1. Клонирование репозитория

```bash
git clone <url-репозитория>
cd ai-rag-book-system
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корневой директории:

```bash
# Скопируйте пример, если доступен
cp .env.example .env
```

Отредактируйте `.env` с вашими настройками:

```env
# ==================== Конфигурация JWT ====================
JWT_SECRET_KEY=ваш-секретный-ключ-замените-в-продакшене

# ==================== Конфигурация PostgreSQL ====================
POSTGRES_USER=bookuser
POSTGRES_PASSWORD=bookpassword
POSTGRES_DB=bookdb

# ==================== Конфигурация Minio ====================
MINIO_USER=minioadmin
MINIO_PASSWORD=minioadmin
MINIO_HOST=minio

# ==================== Конфигурация LLM ====================
# Выберите один: ollama или openrouter
LLM_PROVIDER=ollama

# Для Ollama (локально, бесплатно)
OLLAMA_MODEL=qwen2.5:7b-instruct

# Для OpenRouter (облако, требуется API ключ)
# LLM_PROVIDER=openrouter
# OPENROUTER_API_KEY=ваш-api-ключ-openrouter
# OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct:free

# ==================== Конфигурация эмбеддингов ====================
HF_EMBEDDINGS_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### 3. Запуск всех сервисов

```bash
docker-compose up -d
```

Дождитесь запуска всех сервисов (2-3 минуты при первом запуске):

```bash
docker-compose ps
```

### 4. Доступ к приложению

| Сервис | URL | Описание |
|--------|-----|----------|
| **Streamlit UI** | http://localhost:8501 | Веб-интерфейс |
| **RAG API** | http://localhost:8000/docs | Документация API |
| **Minio Console** | http://localhost:9001 | UI хранилища файлов |
| **Ollama** | http://localhost:11434 | Сервер LLM |

## 📖 Руководство пользователя

### Шаг 1: Регистрация аккаунта

1. Откройте http://localhost:8501
2. Перейдите на вкладку «Регистрация»
3. Введите имя пользователя и пароль (минимум 6 символов)
4. Нажмите «Зарегистрироваться»

### Шаг 2: Вход в систему

1. Введите ваши учётные данные
2. Нажмите «Войти»

### Шаг 3: Загрузка документов

1. Перейдите в раздел «Загрузка файлов»
2. Выберите файлы в формате **PDF**
3. Нажмите «Загрузить и обработать файлы»
4. Дождитесь завершения обработки

> **Важно:** Система поддерживает загрузку документов **только в формате PDF**. Документы на любом языке поддерживаются.

### Шаг 4: Общение с документами

1. Перейдите в раздел «Чат с ботом»
2. Задавайте вопросы по вашим документам
3. Получайте ответы от ИИ с цитатами

### Шаг 5: Управление файлами

1. Перейдите в раздел «Управление файлами»
2. Просматривайте все загруженные файлы
3. Удаляйте ненужные файлы

## 🔧 Обзор сервисов

### RAG Service (FastAPI)

Основной сервис для обработки документов и RAG-операций.

**Основные возможности:**
- Загрузка и обработка документов (PDF)
- Генерация векторных эмбеддингов
- Семантический поиск
- Чат с использованием LLM
- JWT аутентификация

**Документация:** [`rag_service/README.md`](rag_service/README.md)

**API эндпоинты:**
```bash
# Загрузка документов
POST /api/rag/upload_books

# Генерация векторной базы данных
POST /api/rag/generate_chroma_db

# Семантический поиск
GET /api/rag/similarity_search?query=<ваш-запрос>&k=3

# Чат с документами
GET /api/rag/chat?query=<ваш-вопрос>
```

### Streamlit Service

Веб-интерфейс для взаимодействия с пользователем.

**Основные возможности:**
- Регистрация и аутентификация пользователей
- Интерфейс загрузки файлов
- Управление документами
- Чат-интерфейс с RAG-ботом

**Документация:** [`streamlit_service/README.md`](streamlit_service/README.md)

### PostgreSQL

Хранение данных пользователей и аутентификация.

- Порт: `5432`
- Том данных: `./pg_data`

### Minio

Объектное хранилище для загруженных документов.

- Консоль: http://localhost:9001
- API: http://localhost:9000
- Том данных: `./minio_data`

### Ollama

Локальный сервер LLM.

- Порт: `11434`
- Том моделей: `./ollama_models`

## 🛠️ Разработка

### Запуск сервисов по отдельности

```bash
# Запуск только зависимостей
docker-compose up -d postgres minio ollama

# Запуск RAG сервиса локально
cd rag_service
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Запуск Streamlit локально
cd streamlit_service
uv sync
streamlit run main.py
```

### Сборка образов

```bash
docker-compose build
```

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f rag_service
```

### Остановка сервисов

```bash
# Остановить все
docker-compose down

# Остановить и удалить тома (данные будут потеряны!)
docker-compose down -v
```

## 🔐 Безопасность

- **JWT аутентификация**: Все API-запросы требуют валидный JWT-токен
- **Изоляция пользователей**: Данные каждого пользователя изолированы по user_id
- **Хеширование паролей**: Пароли хешируются с помощью bcrypt
- **Валидация ввода**: Типы и размеры файлов проверяются

## ⚙️ Опции конфигурации

### LLM провайдеры

#### Вариант 1: Ollama (локально, бесплатно)

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b-instruct
```

Рекомендуемые модели:
- `qwen2.5:7b-instruct` — Хороший баланс скорости и качества
- `qwen2.5:3b-instruct` — Быстрее, меньше ОЗУ
- `llama3.2:3b-instruct` — Альтернативный вариант

#### Вариант 2: OpenRouter (облако, API ключ)

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct:free
```

Получите API ключ на: https://openrouter.ai

### Модели эмбеддингов

```env
HF_EMBEDDINGS_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Альтернативные модели:
- `sentence-transformers/all-MiniLM-L6-v2` (английский, быстрее)
- `intfloat/multilingual-e5-large` (мультиязычная, лучшее качество)

## 🐛 Решение проблем

### Сервисы не запускаются

```bash
# Проверьте логи
docker-compose logs

# Перезапустите сервисы
docker-compose restart

# Пересоберите образы
docker-compose up -d --build
```

### Ошибка загрузки модели Ollama

```bash
# Проверьте логи Ollama
docker-compose logs ollama

# Загрузите модель вручную
docker exec -it ollama ollama pull qwen2.5:7b-instruct
```

### Недостаточно памяти

- Используйте модели меньшего размера (например, `qwen2.5:1.5b`)
- Увеличьте лимиты памяти Docker
- Используйте облачную LLM (OpenRouter)

### Проблемы с подключением к базе данных

```bash
# Проверьте, работает ли PostgreSQL
docker-compose ps postgres

# Перезапустите PostgreSQL
docker-compose restart postgres
```

### Проблемы с подключением к Minio

```bash
# Проверьте, работает ли Minio
docker-compose ps minio

# Откройте консоль Minio
# http://localhost:9001
```

## 📊 Бенчмарки производительности

| Операция | Среднее время |
|----------|---------------|
| Загрузка книги (300 стр.) | 5-10 сек |
| Генерация ChromaDB | 30-60 сек |
| Семантический поиск | 0,5-2 сек |
| Генерация ответа (LLM) | 3-10 сек |

## 📝 Документация API

Полная документация API доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в удалённый репозиторий (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 🙏 Благодарности

- [FastAPI](https://fastapi.tiangolo.com/) — Современный веб-фреймворк Python
- [Streamlit](https://streamlit.io/) — Фреймворк для дата-приложений
- [LangChain](https://python.langchain.com/) — Фреймворк для оркестрации LLM
- [Ollama](https://ollama.ai/) — Локальный сервер LLM
- [Minio](https://min.io/) — Объектное хранилище
- [ChromaDB](https://www.trychroma.com/) — Векторная база данных

## 📞 Поддержка

По вопросам и проблемам:
- Создайте issue в репозитории
- Проверьте существующую документацию
- Изучите документацию API на http://localhost:8000/docs
