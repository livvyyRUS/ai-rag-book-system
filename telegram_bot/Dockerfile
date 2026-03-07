FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN uv sync --no-dev --no-cache && rm -rf /root/.cache/uv

COPY . /app

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "main.py"]