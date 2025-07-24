import asyncio
import websockets
import json

from PyQt5.QtCore import QThread, pyqtSignal


class WebSocketThread(QThread):
    message_received: pyqtSignal = pyqtSignal(bytes)  # Signal to send messages to PyQt UI

    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()  # Separate event loop for async tasks
        self.running = True

    async def websocket_client(self):
        uri = "ws://192.168.1.236:8080"

        async with websockets.connect(uri) as websocket:
            await websocket.send("anomalie")
            response = await websocket.recv()
            print("Server response:", response, flush=True)
            test_message = {
                "type": "test",
                "content": "This is a JSON test message",
                "sender": "Python Client"
            }
            await websocket.send(json.dumps(test_message))

            while True:
                message = await websocket.recv()
                self.message_received.emit(message)

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.websocket_client())

    def stop(self):
        self.running = False
        self.quit()

# Function that processes messages received from WebSockets
# def handle_message(data):
#     if isinstance(data, bytes):
#         data = data.decode("utf-8")
#     return(json.loads(data))
