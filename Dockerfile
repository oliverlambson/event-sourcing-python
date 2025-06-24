FROM docker.io/python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:0.7.14 /uv /uvx /bin/

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential wget \
    && rm -rf /var/lib/apt/lists/*

COPY uv.lock ./
COPY pyproject.toml ./
RUN uv sync --locked --no-dev --compile-bytecode
ENV PATH="/app/.venv/bin:$PATH"

COPY . .

EXPOSE 8080

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080", "app:asgi_app"]
