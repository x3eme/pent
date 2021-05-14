import asyncio
import websockets

async def hello():
    uri = "wss://stream.binance.com:9443"
    async with websockets.connect(uri) as websocket:
        name = input('{"method": "LIST_SUBSCRIPTIONS","id": 3}')

        await websocket.send(name)
        print("> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())