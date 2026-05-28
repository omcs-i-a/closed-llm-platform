FROM python:3.12-slim

WORKDIR /workspace

ENV UV_SYSTEM_PYTHON=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY app ./app

RUN uv sync --frozen

EXPOSE 8000 8501

CMD ["uv", "run", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
