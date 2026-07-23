import io
import asyncio
import httpx

from app.config import settings


class TextToSpeechService:

    @classmethod
    async def _elevenlabs(cls, text: str, voice_id: str = None) -> bytes | None:
        if not settings.ELEVENLABS_API_KEY:
            return None
        try:
            voice_id = voice_id or settings.ELEVENLABS_VOICE_ID
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": settings.ELEVENLABS_API_KEY,
            }
            payload = {
                "text": text,
                "model_id": "eleven_turbo_v2",
                "voice_settings": {"stability": 0.3, "similarity_boost": 0.7, "speed": 1.0},
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                return resp.content
        except Exception:
            return None

    @classmethod
    async def _gtts(cls, text: str) -> bytes:
        from gtts import gTTS
        import io
        loop = asyncio.get_event_loop()
        def _run():
            fp = io.BytesIO()
            tts = gTTS(text=text, lang="en")
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        return await loop.run_in_executor(None, _run)

    @classmethod
    async def synthesize(cls, text: str, voice_id: str = None) -> bytes:
        audio = await cls._elevenlabs(text, voice_id)
        if audio:
            return audio
        return await cls._gtts(text)

    @classmethod
    async def synthesize_stream(cls, text: str, voice_id: str = None):
        audio = await cls.synthesize(text, voice_id)
        yield audio
