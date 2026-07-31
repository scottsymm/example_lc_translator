FROM python:3.11-slim

WORKDIR /app

# Install Node.js 20 and pnpm
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g pnpm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency manifests first for layer caching
COPY pyproject.toml pnpm-workspace.yaml package.json ./
COPY packages/lc-translator-core/pyproject.toml packages/lc-translator-core/README.md ./packages/lc-translator-core/
COPY packages/lc-translator-api/pyproject.toml packages/lc-translator-api/README.md ./packages/lc-translator-api/

# Install Python dependencies
RUN uv sync --extra dev

# Install JS dependencies
RUN pnpm install

# Copy source and build frontend
COPY . .
RUN pnpm --filter web build

ENV LC_TRANSLATOR_STATIC_DIR=/app/apps/web/dist
EXPOSE 8000

CMD ["uv", "run", "--package", "lc-translator-api", "uvicorn", "lc_translator_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
