import asyncio
# @zdanl here modiyfing @atheorell work from websockets to socket.io
import socketio
from gpt_engineer.core.default.lean_agent import LeanAgent
from gpt_engineer.core.preprompt_holder import PrepromptHolder
import tempfile
import json


@sio.on('gpt4_api_key')
def gpt4_api_key_seed(sid, data):
    code = agent.seed(data)
    
            
@sio.on('*')
def catch_all(event, sid, data):
    pass
            
@sio.event
def connect(sid, environ, auth):
    print('connect ', sid)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

async def handler(websocket):
    # Initialize agent
    tempdir = tempfile.gettempdir()
    agent = LeanAgent.with_default_config(tempdir)
    # messages holds:
    # "type" of request
    #   init, improve, execute, preprompt
    # "prompt"
    #   What to do in NL.
    # "code"
    #   A program in json format
    async for message in websocket:
        # Parse a "play" event from the UI.
        # ^^ @zdanl: this is wrong. we are explicitly pushing to the UI, not
        # awaiting polls from the UI. this is the benefit of websockets

        event = json.loads(message)
        assert "type" in event
        if event["type"] == "init":
            code = agent.init(event["prompt"])
            await socketio.emit('prompt', {'payload': json.dumps(code)})
        elif event["type"] == "improve":
            code = agent.improve(json.loads(event["code"]), event["prompt"])
            await socketio.emit('improve', {'payload': json.dumps(code)})
        elif event["type"] == "execute":
            process = agent.execution_env.execute_program(event["code"])
            stdout, stderr = process.communicate()
            # stdout and stderr are bytes, decode them to string if needed
            output = stdout.decode("utf-8")
            error = stderr.decode("utf-8")
            payload = json.dumps({"output": output, "error": error})
            await socketio.emit('execute', {'payload': payload})

        
async def main():
    async with socketio.listen():
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    sio = socketio.Server(4444)
    asyncio.run(main())
