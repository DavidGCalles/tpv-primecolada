import asyncio
import websockets
import json
import time

WEBSOCKET_URL = "ws://localhost:3001"

async def listen_persistently():
    """
    Connects to the WebSocket server and persistently listens for messages,
    attempting to reconnect on failure.
    """
    while True:
        try:
            async with websockets.connect(WEBSOCKET_URL) as websocket:
                print(f"✅ Connected to WebSocket server at {WEBSOCKET_URL}")
                print("👂 Listening for messages...")
                async for message in websocket:
                    print("📩 Received message from WebSocket:")
                    try:
                        data = json.loads(message)
                        print(json.dumps(data, indent=2))
                    except json.JSONDecodeError:
                        print(f"❌ Received non-JSON message: {message}")

        except websockets.exceptions.ConnectionClosed as e:
            print(f"❌ WebSocket connection closed: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except ConnectionRefusedError:
            print("❌ Connection refused. Is the WebSocket server running? Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"💥 An unexpected error occurred: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(listen_persistently())
    except KeyboardInterrupt:
        print("\n🛑 Script interrupted by user. Exiting.")