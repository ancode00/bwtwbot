import asyncio
import base64
import json

class TwilioAudioInterface:
    def __init__(self, websocket):
        self.websocket = websocket
        self.audio_queue = asyncio.Queue()
        self.closed = False

    async def get_audio(self):
        return await self.audio_queue.get()

    async def push_user_audio(self, audio_bytes):
        await self.audio_queue.put(audio_bytes)

    async def play_agent_audio(self, audio_bytes):
        payload = base64.b64encode(audio_bytes).decode()
        await self.websocket.send_text(json.dumps({
            "event": "media",
            "media": {"payload": payload}
        }))

    async def close(self):
        self.closed = True

    # Add these two methods:
    def start(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass

