import asyncio
import base64
import json

class TwilioAudioInterface:
    def __init__(self, websocket):
        self.websocket = websocket
        self.audio_queue = asyncio.Queue()
        self.closed = False

    # Called by ElevenLabs to get user audio
    async def get_audio(self):
        # Wait for Twilio to provide audio via push_user_audio
        return await self.audio_queue.get()

    # Called by your Twilio handler for every 'media' event from Twilio
    async def push_user_audio(self, audio_bytes):
        await self.audio_queue.put(audio_bytes)

    # Called by ElevenLabs to play agent audio
    async def play_agent_audio(self, audio_bytes):
        # Immediately send to Twilio in the correct format
        payload = base64.b64encode(audio_bytes).decode()
        await self.websocket.send_text(json.dumps({
            "event": "media",
            "media": {"payload": payload}
        }))

    async def close(self):
        self.closed = True

