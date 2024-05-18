FROM python:3.11-slim

RUN apt-get update
RUN apt-get install -y sudo tk tcl gcc curl
RUN apt-get install -y git

WORKDIR /app

COPY . .

COPY docker/entrypoint.sh ./entrypoint.sh

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["bash", "/app/entrypoint.sh"]
