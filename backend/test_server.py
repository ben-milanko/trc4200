import asyncio
import json
import logging
import random

import websockets

logger = logging.getLogger()


async def publish(websocket, path):
    logger.info("Starting publisher...")
    while True:
        data = {
            'detections': [
                {'class': 'car', 'x': 450, 'y': 255, 'id': 1},
                {'class': 'pedestrian', 'x': 300 + random.randint(-200, 200), 'y': 300 + random.randint(-200, 200),
                 'id': 2}
            ]
        }
        try:
            await websocket.send(json.dumps(data))
        except websockets.ConnectionClosedError:
            logger.info("Connection closed.")
            return
        await asyncio.sleep(1)


start_server = websockets.serve(publish, "127.0.0.1", 6845)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
