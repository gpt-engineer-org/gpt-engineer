# Stage 1: Builder stage
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
  tk \
  tcl \
  curl \
  git \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -e .

# Stage 2: Final stage
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/bin /usr/bin
COPY --from=builder /app .

COPY docker/entrypoint.sh .

ENTRYPOINT ["bash", "/app/entrypoint.sh"]
