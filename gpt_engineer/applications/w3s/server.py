# Changelog
# * @ATheorell created this file
# * @zdanl here modiyfing @atheorell work from websockets to socket.io

import uvicorn
import socketio
import tempfile
import json

from gpt_engineer.core.default.lean_agent import LeanAgent

sio = socketio.Server()
app = socketio.ASGIApp(sio)
tempdir = tempfile.gettempdir()
agent = LeanAgent.with_default_config(tempdir)

from gpt_engineer.core.preprompt_holder import PrepromptHolder


# in case OPENAI_API_KEY isnt exported or in .env the web app should be
# able to set the API Key
@sio.on("gpt4_api_key")
def gpt4_api_key_seed(sid, data):
    code = agent.seed(data)


@sio.on("init")
async def gptengineer_init(event, sid, data):
    print(f"{event}: {data}")
    code = agent.init(event["prompt"])
    await socketio.emit("prompt", {"payload": json.dumps(code)})


@sio.on("improve")
async def gptengineer_init(event, sid, data):
    print(f"{event}: {data}")
    code = agent.improve(json.loads(event["code"]), event["prompt"])
    await socketio.emit("improve", {"payload": json.dumps(code)})


@sio.on("execute")
async def gptengineer_init(event, sid, data):
    print(f"{event}: {data}")
    process = agent.execution_env.execute_program(event["code"])
    stdout, stderr = process.communicate()
    output = stdout.decode("utf-8")
    error = stderr.decode("utf-8")
    payload = json.dumps({"output": output, "error": error})
    await socketio.emit("execute", {"payload": payload})


@sio.event
def connect(sid, environ, auth):
    print("connection to browser established ", sid)


@sio.event
def disconnect(sid):
    print("disconnected from browser ", sid)


async def main():
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=4444)
