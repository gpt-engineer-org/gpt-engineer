# Changelog
# * @ATheorell created this file
# * @zdanl here modiyfing @atheorell work from websockets to socket.io

from aiohttp import web
import aiohttp_cors
import socketio
import tempfile
import json

from gpt_engineer.core.default.lean_agent import LeanAgent
from gpt_engineer.core.preprompt_holder import PrepromptHolder

sio = socketio.AsyncServer(cors_allowed_origins="*")
app = web.Application()
sio.attach(app)

tempdir = tempfile.gettempdir()
agent = LeanAgent.with_default_config(tempdir)


class GPTEngineerNamespace(socketio.AsyncNamespace):
    def on_connect(self, sid, environ):
        print("Real-time socket to browser established.")

    def on_disconnect(self, sid):
        print("Browser disconnected.")

    def on_my_event(self, sid, data):
        self.emit("my_response", data)

    def on_gp4_apikey(self, sid, data):
        code = agent.seed(data)

    async def on_init(event, sid, data):
        print(f"{event}: {data}")
        code = agent.init(event["prompt"])
        await socketio.emit("prompt", {"payload": json.dumps(code)})

    async def on_improve(event, sid, data):
        print(f"{event}: {data}")
        code = agent.improve(json.loads(event["code"]), event["prompt"])
        await socketio.emit("improve", {"payload": json.dumps(code)})

    async def on_execute(event, sid, data):
        print(f"{event}: {data}")
        process = agent.execution_env.execute_program(event["code"])
        stdout, stderr = process.communicate()
        output = stdout.decode("utf-8")
        error = stderr.decode("utf-8")
        payload = json.dumps({"output": output, "error": error})
        await socketio.emit("execute", {"payload": payload})


sio.register_namespace(GPTEngineerNamespace("/gptengineer"))


async def main():
    pass


if __name__ == "__main__":
    web.run_app(app, port=4444)
