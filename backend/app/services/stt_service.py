import asyncio
import tempfile

from app.config import settings

try:
    import whisper

    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class SpeechToTextService:
    _model = None
    _lock = asyncio.Lock()

    @classmethod
    async def _get_model(cls):
        async with cls._lock:
            if cls._model is None and WHISPER_AVAILABLE:
                loop = asyncio.get_event_loop()
                cls._model = await loop.run_in_executor(
                    None, lambda: whisper.load_model(settings.WHISPER_MODEL)
                )
        return cls._model

    @classmethod
    async def transcribe_mic(cls, language: str = "en") -> str:
        try:
            import sounddevice as sd
            import numpy as np
            import scipy.io.wavfile as wav
        except ImportError:
            return "[Install sounddevice: pip install sounddevice numpy scipy]"

        fs = 16000
        duration = 5
        print(f"  Recording for {duration} seconds...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.int16)
        sd.wait()
        print("  Recording done.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            wav.write(tmp.name, fs, recording)
            tmp_path = tmp.name

        model = await cls._get_model()
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None, lambda: model.transcribe(tmp_path, language=language)
            )
            return result.get("text", "").strip()
        except Exception as e:
            return f"[Transcription error: {e}]"
        finally:
            import os
            os.unlink(tmp_path)

    @classmethod
    async def transcribe(cls, audio_bytes: bytes, language: str = "ur") -> str:
        model = await cls._get_model()
        if model is None:
            return "[Whisper not installed]"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None, lambda: model.transcribe(tmp_path, language=language)
            )
            return result.get("text", "").strip()
        except Exception as e:
            return f"[Transcription error: {e}]"
        finally:
            import os
            os.unlink(tmp_path)
