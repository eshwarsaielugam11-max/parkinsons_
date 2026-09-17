import asyncio
import websockets
import json

async def test():
    uri = "ws://127.0.0.1:8000/api/v1/stream"
    async with websockets.connect(uri) as ws:
        for i in range(3):
            # Send 2 seconds of zero bytes
            await ws.send(b"\x00" * 64000)
            res = await ws.recv()
            print(f"Window {i+1}:", json.loads(res))

asyncio.run(test())
