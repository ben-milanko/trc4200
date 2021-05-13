import asyncio
import json

import websockets
from websockets.exceptions import ConnectionClosed


async def connect(uri):
    async with websockets.connect(uri) as websocket:
        print("Connected..")
        while True:
            message = await websocket.recv()
            action = json.loads(message)
            print(action)


async def hello():
    uri = "ws://localhost:8000/stream"
    try:
        await connect(uri)
    except ConnectionClosed:
        await asyncio.sleep(3)
        print("Not able to connect.. Retrying in 3 seconds")
        await connect(uri)


asyncio.get_event_loop().run_until_complete(hello())
