# Getting Started using Docker

**Running using docker cli**:

Building the image:
- `git clone https://github.com/gpt-engineer-org/gpt-engineer.git`
- `cd gpt-engineer`
- `docker build --rm -t gpt-engineer -f docker/Dockerfile .`

Running the container:
- `docker run -it --rm -e OPENAI_API_KEY="YOUR OPENAI KEY" -v ./your-project:/project gpt-engineer`

The `-v` flag mounts the `your-project` folder into the container. Make sure to have a `prompt` file in there.

**Running using docker-compose cli**:

Building the image:
- `git clone https://github.com/gpt-engineer-org/gpt-engineer.git`
- `cd gpt-engineer`
- `docker-compose -f docker-compose.yml build`
- `docker-compose run --rm gpt-engineer`


Set the OPENAI_API_KEY in docker/docker-compose.yml using .env file or environment variable, and mount your project folder into the container using volumes. for example "./projects/example:/project" ./projects/example is the path to your project folder.


**Running using compose dc.yaml incorporating ollma and litellm**:
This compose file runs an ollama server which is read by litellm 
gpt engineers uses only openai commands to interact with litellm
Grabbing and experimenting with different models is as simple as ollama pull "modelname"
In detail you would exec into the container created by the compose file - the models will be persisted
on your server and can be selected by changing the .env file or the litellm configuration file

Building the image:
- `git clone https://github.com/gpt-engineer-org/gpt-engineer.git`
- `cd gpt-engineer`
- copy .env_example to .env and edit

- There are 3 sections some variables are used by multiple containers

- OLLAMA 
-    set the OLLAMA_SOURCE_DIR to a folder on your machine with enough space to hold the models
-    e.g. mistral needs 5GB free

- LITELLM
-    defaults should be ok for most

- GPT-ENGINEER
-    Set the GPT_PROJECT folder to your code repo - the default is $home/gptprojects
-  Set the default model to a valid ollama image and the ollmaa container will automatically download and set that
-  for the project and run. default is "mistral" For ore advanced managemnet use a litellm configuration yml
-  First time run `docker-compose -f dc.yml up --build`

- Subsequent runs can just run `docker-compose -f dc.yml up -d' to start and 'docker-compose -f dc.yml down' to shutdown

