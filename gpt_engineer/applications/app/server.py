import asyncio
import websockets
from gpt_engineer.core.default.lean_agent import LeanAgent
from gpt_engineer.core.preprompt_holder import PrepromptHolder
import tempfile
import json

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

        event = json.loads(message)
        assert "type" in event
        if event["type"] == "init":
            code = agent.init(event["prompt"])
            await websocket.send(json.dumps(code))
        elif event["type"] == "improve":
            code = agent.improve(json.loads(event["code"]), event["prompt"])
            await websocket.send(json.dumps(code))
        elif event["type"] == "execute":
            process = agent.execution_env.execute_program(event["code"])
            stdout, stderr = process.communicate()
            # stdout and stderr are bytes, decode them to string if needed
            output = stdout.decode("utf-8")
            error = stderr.decode("utf-8")
            await websocket.send(json.dumps({"output": output, "error": error}))


async def main():
    async with websockets.serve(handler, "", 8000):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
