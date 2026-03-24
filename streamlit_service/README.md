# Streamlit Service 🎨

Веб-интерфейс для системы AI RAG Book System, разработанный с использованием Streamlit.

## 📖 Описание

Streamlit Service предоставляет удобный веб-интерфейс для:
- Регистрации и аутентификации пользователей
- Загрузки и управления документами
- Общения с документами с использованием технологии RAG

> **Важно:** Система поддерживает загрузку документов **только в формате PDF**. Документы на любом языке поддерживаются.

## 🏗️ Архитектура

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
│   (Пользователи)│ │   (Файлы)    │ │   (FastAPI)  │
└─────────────────┘ └──────────────┘ └──────────────┘
```

## 🚀 Быстрый старт

### Требования

- Python 3.11+
- Docker и Docker Compose (для зависимостей)
- Запущенный RAG Service

### Установка

1. **Установите зависимости:**
```bash
cd streamlit_service
uv sync
```

2. **Создайте файл `.env` в корне проекта:**
```env
# Конфигурация JWT
JWT_SECRET_KEY=ваш-секретный-ключ

# Конфигурация базы данных
DATABASE_URL=postgres://user:password@localhost:5432/bookdb

# Конфигурация RAG Service
RAG_API_URL=http://localhost:8000/api/rag

# Конфигурация Minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
```

3. **Запустите зависимости (PostgreSQL, Minio, RAG Service):**
```bash
docker-compose up -d postgres minio rag_service
```

4. **Запустите Streamlit:**
```bash
streamlit run main.py
```

5. **Откройте в браузере:**
```
http://localhost:8501
```

## 🐳 Docker

### Сборка и запуск

```bash
# Сборка образа
docker-compose build streamlit_service

# Запуск сервиса
docker-compose up -d streamlit_service
```

### Логи

```bash
docker-compose logs -f streamlit_service
```

## 🎯 Возможности

### Аутентификация

- **Регистрация**: Создание новых учётных записей
- **Вход**: Безопасная аутентификация с JWT-токенами
- **Управление сессией**: Сохранение сессии при перезагрузке страницы
- **Выход**: Безопасная очистка сессии

### Управление файлами

- **Загрузка**: Загрузка файлов в формате PDF
- **Просмотр**: Список всех загруженных файлов
- **Удаление**: Удаление ненужных файлов
- **Обработка**: Автоматическая обработка и векторизация документов

### Чат-интерфейс

- **Вопросы**: Запросы на естественном языке о документах
- **Ответы ИИ**: Ответы от LLM с цитатами
- **История**: История разговора в рамках сессии
- **Очистка истории**: Сброс контекста разговора

## 📁 Структура проекта

```
streamlit_service/
├── main.py                 # Основное приложение Streamlit
├── database.py             # Операции с базой данных (Tortoise ORM)
├── models.py               # Модели базы данных (User)
├── jwt_tool.py             # Утилиты JWT-токенов
├── rag_client.py           # Клиент для API RAG Service
├── minio_client.py         # Клиент для хранилища Minio
├── test_auth.py            # Тесты аутентификации
├── Dockerfile              # Конфигурация Docker
├── pyproject.toml          # Зависимости Python
├── uv.lock                 # Lock-файл зависимостей
└── README.md               # Этот файл
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `JWT_SECRET_KEY` | Секретный ключ для JWT-токенов | `secret_key` |
| `DATABASE_URL` | Строка подключения PostgreSQL | `postgres://user:password@localhost:5432/streamlit_db` |
| `RAG_API_URL` | URL API RAG Service | `http://localhost:8000/api/rag` |
| `MINIO_ENDPOINT` | Адрес сервера Minio | `localhost:9000` |
| `MINIO_ACCESS_KEY` | Ключ доступа Minio | `minioadmin` |
| `MINIO_SECRET_KEY` | Секретный ключ Minio | `minioadmin` |
| `MINIO_SECURE` | Использовать HTTPS для Minio | `false` |

### Конфигурация базы данных

Сервис использует **Tortoise ORM** с PostgreSQL:

```python
# database.py
await Tortoise.init(
    db_url="postgres://user:password@localhost:5432/bookdb",
    modules={"models": ["models"]},
)
```

### Конфигурация JWT

Токены действительны **1 час** по умолчанию:

```python
# jwt_tool.py
class JWTPayload(BaseModel):
    user_id: str
    exp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
```

## 🎨 Страницы

### 1. Страница аутентификации

**Вкладки:**
- **Вход**: Введите учётные данные для доступа к аккаунту
- **Регистрация**: Создание нового аккаунта

**Возможности:**
- Валидация пароля (минимум 6 символов)
- Проверка уникальности имени пользователя
- Автоматическая генерация JWT-токена при входе

### 2. Страница загрузки файлов

**Возможности:**
- Загрузка файлов в формате PDF
- Валидация типа файла (только PDF)
- Индикаторы прогресса
- Автоматическая генерация ChromaDB после загрузки

**Использование:**
```python
uploaded_files = st.file_uploader(
    "Выберите файлы для загрузки",
    type=["pdf"],  # Только PDF
    accept_multiple_files=True
)
```

### 3. Страница управления файлами

**Возможности:**
- Список всех загруженных файлов
- Удаление файлов с подтверждением
- Отображение количества файлов

### 4. Страница чата

**Возможности:**
- Чат-интерфейс с историей сообщений
- Ответы ИИ в реальном времени
- Обработка ошибок
- Кнопка очистки истории

**Использование:**
```python
if prompt := st.chat_input("Введите ваш вопрос..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    result = run_async(rag_client.chat(prompt))
    st.session_state["messages"].append({"role": "assistant", "content": result.text})
```

## 📡 Клиент API

### RAGClient

Python-клиент для API RAG Service:

```python
from rag_client import RAGClient

rag_client = RAGClient(
    jwt_token="ваш-jwt-токен",
    user_id="user-username"
)

# Генерация ChromaDB
result = await rag_client.generate_chroma_db()

# Чат
result = await rag_client.chat("Ваш вопрос здесь")
```

### MinioClient

Операции с хранилищем файлов:

```python
from minio_client import upload_file, list_files, delete_file, get_bucket_name

bucket_name = get_bucket_name("username")  # Возвращает "user-username"

# Загрузка
upload_file(bucket_name, "file.pdf", file_bytes)

# Список
files = list_files(bucket_name)

# Удаление
delete_file(bucket_name, "file.pdf")
```

## 🔐 Безопасность

### JWT аутентификация

- Токены хранятся в session state и query params
- Автоматическая валидация токена при каждом запросе
- Срок действия токена: 1 час
- Безопасное хеширование паролей с bcrypt

### Изоляция пользователей

- Каждый пользователь имеет изолированный бакет в Minio
- Формат user_id: `user-{username}`
- Запросы к базе данных фильтруются по пользователю

### Валидация ввода

- Валидация типа файлов (только PDF)
- Требования к сложности пароля
- Проверка уникальности имени пользователя

## 🧪 Тестирование

### Запуск тестов

```bash
# Тесты аутентификации
python test_auth.py
```

### Ручное тестирование

1. **Сценарий регистрации:**
   - Зарегистрируйте нового пользователя
   - Проверьте создание пользователя в базе данных
   - Войдите с учётными данными

2. **Загрузка файлов:**
   - Загрузите тестовый PDF файл
   - Проверьте файл в консоли Minio
   - Проверьте генерацию ChromaDB

3. **Чат:**
   - Задайте вопрос по загруженному документу
   - Проверьте точность ответа
   - Протестируйте историю разговора

## 🐛 Решение проблем

### Ошибка подключения к базе данных

```bash
# Проверьте, работает ли PostgreSQL
docker-compose ps postgres

# Проверьте DATABASE_URL
echo $DATABASE_URL

# Проверьте подключение
docker exec -it postgres_db psql -U user -d bookdb
```

### RAG Service недоступен

```bash
# Проверьте статус RAG сервиса
docker-compose ps rag_service

# Просмотрите логи RAG
docker-compose logs rag_service

# Проверьте API напрямую
curl http://localhost:8000/api/rag
```

### Ошибка подключения к Minio

```bash
# Проверьте статус Minio
docker-compose ps minio

# Откройте консоль Minio
# http://localhost:9001

# Проверьте учётные данные
```

### Истёк срок действия JWT-токена

- Токен истекает через 1 час
- Выйдите и войдите снова
- Токен автоматически обновляется при входе

### Сессия потеряна при перезагрузке

- Проверьте сохранение query params
- Убедитесь, что JWT_SECRET_KEY постоянен
- Очистите кэш браузера и попробуйте снова

## 📊 Производительность

| Операция | Среднее время |
|----------|---------------|
| Регистрация пользователя | < 1 сек |
| Вход пользователя | < 1 сек |
| Загрузка файла (10 МБ) | 2-5 сек |
| Генерация ChromaDB | 30-60 сек |
| Ответ чата | 3-10 сек |

## 🔄 Управление сессией

### Session State

```python
st.session_state["authenticated"] = True
st.session_state["username"] = "username"
st.session_state["user_id"] = "user-username"
st.session_state["jwt_token"] = "jwt-токен"
st.session_state["messages"] = [...]  # История чата
```

### Query Params

Сессия сохраняется при перезагрузке страницы через query params:
```
?jwt_token=xxx&username=xxx&user_id=xxx
```

## 🤝 Интеграция с RAG Service

### Используемые API эндпоинты

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/upload_books` | POST | Загрузка документов |
| `/generate_chroma_db` | POST | Генерация векторной БД |
| `/chat` | GET | Чат с документами |
| `/clear_history` | POST | Очистка истории чата |

### Обработка ошибок

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

## 📝 Примеры кода

### Регистрация пользователя

```python
from database import add_user

success = await add_user("newuser", "password123")
if success:
    st.success("Регистрация успешна!")
else:
    st.error("Пользователь уже существует")
```

### Загрузка файлов

```python
from minio_client import create_bucket_if_not_exists, upload_file

bucket_name = get_bucket_name(username)
create_bucket_if_not_exists(bucket_name)

for file in uploaded_files:
    upload_file(bucket_name, file.name, file.getvalue())
```

### Чат с RAG

```python
from rag_client import RAGClient

rag_client = RAGClient(jwt_token, user_id)
result = await rag_client.chat("В чём основная тема?")
st.write(result.text)
```

## 🛠️ Разработка

### Локальная разработка

```bash
# Установка зависимостей
uv sync

# Запуск с автоперезагрузкой
streamlit run main.py --server.head true

# Запуск на определённом порту
streamlit run main.py --server.port 8501
```

### Docker разработка

```bash
# Сборка образа
docker build -t streamlit-service .

# Запуск контейнера
docker run -p 8501:8501 --env-file .env streamlit-service
```

## 📄 Лицензия

MIT License
