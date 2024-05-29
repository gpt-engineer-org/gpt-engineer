# Getting Started Using Docker

This guide provides step-by-step instructions on how to set up and run the Docker environment for your GPT-Engineer project.

## Prerequisites

- Docker installed on your machine.
- Git (for cloning the repository).

## Setup Instructions

### Using Docker CLI

1. **Clone the Repository**

    ```bash
    git clone https://github.com/gpt-engineer-org/gpt-engineer.git
    cd gpt-engineer
    ```

2. **Build the Docker Image**

    ```bash
    docker build --rm -t gpt-engineer -f docker/Dockerfile .
    ```

3. **Run the Docker Container**

    ```bash
    docker run -it --rm -e OPENAI_API_KEY="YOUR_OPENAI_KEY" -v ./your-project:/project gpt-engineer
    ```

    Replace `YOUR_OPENAI_KEY` with your actual OpenAI API key. The `-v` flag mounts your local `your-project` directory inside the container. Replace this with your actual project directory.  Ensure this directory contains all necessary files, including the `prompt` file.

### Using Docker Compose

1. **Clone the Repository** (if not already done)

    ```bash
    git clone https://github.com/gpt-engineer-org/gpt-engineer.git
    cd gpt-engineer
    ```

2. **Build and Run using Docker Compose**

    ```bash
    docker-compose -f docker-compose.yml build
    docker-compose run --rm gpt-engineer
    ```

    Set the `OPENAI_API_KEY` in the `docker/docker-compose.yml` using an `.env` file or as an environment variable. Mount your project directory to the container using volumes, e.g., `"./projects/example:/project"` where `./projects/example` is the path to your project directory.

3. **Another alternative using Docker Compose**

    Since there is only one `docker-compose.yml` file, you could run it without the -f option.
    - `docker compose up -d --build` - To build and start the containers defined in your `docker-compose.yml` file in detached mode
    - `docker compose up -d` - To start the containers defined in your `docker-compose.yml` file in detached mode
    - `docker compose down` - To stop and remove all containers, networks, and volumes associated with the `docker-compose.yml`
    - `docker compose restart` - To restart the containers defined in the `docker-compose.yml` file

## Debugging

To facilitate debugging, you can run a shell inside the built Docker image:

```bash
docker run -it --entrypoint /bin/bash gpt-engineer
```

This opens a shell inside the Docker container, allowing you to execute commands and inspect the environment manually.
