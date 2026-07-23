import asyncio
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient
from twilio.twiml.voice_response import VoiceResponse, Gather, Say

from app.config import settings


class SignalWireHttpClient(TwilioHttpClient):
    def __init__(self, space: str):
        super().__init__()
        clean = space.replace(".signalwire.com", "")
        self.sw_base = f"https://{clean}.signalwire.com"
        self.twilio_base = "https://api.twilio.com"

    def request(self, method, url, **kwargs):
        if url.startswith(self.twilio_base):
            url = url.replace(self.twilio_base, self.sw_base)
        return super().request(method, url, **kwargs)


class VoiceService:
    _client = None
    _lock = asyncio.Lock()

    @classmethod
    async def _get_client(cls):
        async with cls._lock:
            if cls._client is None:
                loop = asyncio.get_event_loop()
                http_client = SignalWireHttpClient(settings.SIGNALWIRE_SPACE)
                cls._client = await loop.run_in_executor(
                    None,
                    lambda: Client(
                        settings.SIGNALWIRE_PROJECT_ID,
                        settings.SIGNALWIRE_AUTH_TOKEN,
                        http_client=http_client,
                    ),
                )
        return cls._client

    @classmethod
    async def make_call(cls, to_phone: str, webhook_url: str) -> str:
        client = await cls._get_client()
        loop = asyncio.get_event_loop()
        call = await loop.run_in_executor(
            None,
            lambda: client.calls.create(
                to=to_phone,
                from_=settings.SIGNALWIRE_PHONE_NUMBER,
                url=webhook_url,
                status_callback=f"{settings.SIGNALWIRE_WEBHOOK_BASE_URL}/api/calls/status",
                status_callback_event=["initiated", "ringing", "answered", "completed"],
                timeout=30,
            ),
        )
        return call.sid

    @classmethod
    def generate_twiml_greeting(cls, message: str, language: str = "en") -> str:
        response = VoiceResponse()
        base = settings.SIGNALWIRE_WEBHOOK_BASE_URL
        say_opts = {"voice": "Polly.Amber", "language": language}

        gather = Gather(
            input="speech",
            action=f"{base}/api/calls/process-speech",
            method="POST",
            speech_timeout="auto",
            enhanced=True,
            speech_model="phone_call",
        )
        gather.say(message, **say_opts)
        response.append(gather)

        response.say("I didn't hear you. Please speak again.", **say_opts)

        return str(response)

    @classmethod
    def generate_twiml_response(cls, audio_url: str) -> str:
        response = VoiceResponse()
        base = settings.SIGNALWIRE_WEBHOOK_BASE_URL
        response.play(audio_url)

        gather = Gather(
            input="speech",
            action=f"{base}/api/calls/process-speech",
            method="POST",
            speech_timeout="auto",
            enhanced=True,
            speech_model="phone_call",
        )
        response.append(gather)

        return str(response)

    @classmethod
    def generate_twiml_hangup(cls, message: str, language: str = "en") -> str:
        response = VoiceResponse()
        say_opts = {"voice": "Polly.Amber", "language": language}
        response.say(message, **say_opts)
        response.hangup()
        return str(response)

    @classmethod
    async def get_call_recording(cls, call_sid: str) -> str | None:
        client = await cls._get_client()
        recordings = client.recordings.list(call_sid=call_sid, limit=1)
        if recordings:
            recording = recordings[0]
            clean = settings.SIGNALWIRE_SPACE.replace(".signalwire.com", "")
            return (
                f"https://{clean}.signalwire.com/api/twilio/"
                f"2010-04-01/Accounts/"
                f"{settings.SIGNALWIRE_PROJECT_ID}/Recordings/{recording.sid}.mp3"
            )
        return None
