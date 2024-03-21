# Stage 1: Builder stage
FROM python:3.11-alpine AS builder

RUN apk update && apk add --no-cache tk tcl curl

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -e .

# Stage 2: Final stage
FROM python:3.11-alpine

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app .

COPY docker/entrypoint.sh .

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
