# Stage 1: Builder stage
FROM python:3.13-slim AS builder

# Install necessary OS packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    tk \
    tcl \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy source code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir openai>=1.0.0 backoff langchain_google_genai

# Stage 2: Final stage
FROM python:3.13-slim

WORKDIR /app

# Copy installed Python packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/bin /usr/bin

# Copy app code
COPY --from=builder /app .

# Copy entrypoint and ensure Unix line endings
COPY docker/entrypoint.sh .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
