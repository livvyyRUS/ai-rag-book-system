# ---- Stage 1: Установка зависимостей и создание виртуального окружения ----
FROM python:3.12-slim AS builder

# Устанавливаем uv (менеджер пакетов) – он понадобится только на этапе сборки
RUN pip install --no-cache-dir uv

WORKDIR /app

# Копируем только файлы с описанием зависимостей, чтобы использовать кэш Docker
COPY pyproject.toml uv.lock* ./

# Создаём виртуальное окружение и устанавливаем зависимости (без dev-пакетов)
# Кэш uv удаляем сразу, чтобы не тащить его в следующий слой
RUN uv sync --no-dev --no-cache && rm -rf /root/.cache/uv


# ---- Stage 2: Финальный образ для запуска приложения ----
FROM python:3.12-slim

WORKDIR /app

# Копируем виртуальное окружение из предыдущего этапа
COPY --from=builder /app/.venv /app/.venv

# Копируем исходный код приложения
COPY . /app

# Добавляем путь к исполняемым файлам виртуального окружения в PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]