import os
import json
import base64
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.responses import HTMLResponse
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from twilio_audio_interface import TwilioAudioInterface

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")

app = FastAPI()

@app.get("/")
def index():
    return HTMLResponse("<h2>Twilio-ElevenLabs Streaming Voicebot is running!</h2>")

@app.websocket("/twilio/stream")
async def twilio_ws(websocket: WebSocket):
    await websocket.accept()
    interface = TwilioAudioInterface(websocket)
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    conversation = Conversation(
        client=client,
        agent_id=ELEVENLABS_AGENT_ID,
        requires_auth=True,
        audio_interface=interface,
        callback_agent_response=lambda r: print(f"Agent: {r}"),
        callback_user_transcript=lambda t: print(f"User: {t}"),
    )
    conversation.start_session()

    try:
        while True:
            data = await websocket.receive_text()
            event = json.loads(data)
            if event.get("event") == "start":
                print("Twilio stream started.")
                await websocket.send_text(json.dumps({"event": "connected"}))
            elif event.get("event") == "media":
                payload = event["media"]["payload"]
                audio_bytes = base64.b64decode(payload)
                # Push Twilio audio to ElevenLabs streaming input
                await interface.push_user_audio(audio_bytes)
            elif event.get("event") == "stop":
                print("Twilio stream stopped.")
                break
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        conversation.end_session()
        await interface.close()
        await websocket.close()

