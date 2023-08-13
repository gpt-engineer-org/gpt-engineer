FROM python:3.9-slim

RUN apt-get update \
 && apt-get install -y sudo

WORKDIR /app

COPY . .

RUN sudo pip install -e .

ENTRYPOINT ["bash", "/app/entrypoint.sh"]
