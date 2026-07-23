"""Multi-provider LLM service with automatic fallback — direct httpx, no LangChain."""

import json
import structlog
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import settings

logger = structlog.get_logger()


class LLMFallbackError(Exception):
    pass


class MultiLLMService:
    _http: httpx.AsyncClient | None = None

    def _client(self) -> httpx.AsyncClient:
        if self._http is None:
            self.__class__._http = httpx.AsyncClient(timeout=httpx.Timeout(45.0, connect=10.0))
        return self._http

    async def _call_gemini(self, messages: list[dict], user_input: str) -> str:
        key = settings.GOOGLE_API_KEY
        if not key:
            raise LLMFallbackError("Gemini: no API key")
        body = {"contents": [{"parts": [{"text": m["content"]} for m in messages] + [{"text": user_input}]}]}
        r = await self._client().post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={key}",
            json=body,
        )
        if r.status_code != 200:
            raise LLMFallbackError(f"Gemini {r.status_code}: {r.text[:200]}")
        data = r.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise LLMFallbackError(f"Gemini: no candidates — {data.get('promptFeedback', {})}")
        return candidates[0]["content"]["parts"][0]["text"]

    async def _call_groq(self, messages: list[dict], user_input: str) -> str:
        key = settings.GROQ_API_KEY
        if not key:
            raise LLMFallbackError("Groq: no API key")
        msgs = [{"role": m["role"], "content": m["content"]} for m in messages] + [{"role": "user", "content": user_input}]
        r = await self._client().post(
            "https://api.groq.com/openai/v1/chat/completions",
            json={"model": settings.GROQ_MODEL, "messages": msgs, "max_tokens": 300},
            headers={"Authorization": f"Bearer {key}"},
        )
        if r.status_code != 200:
            raise LLMFallbackError(f"Groq {r.status_code}: {r.text[:200]}")
        return r.json()["choices"][0]["message"]["content"]

    async def _call_openai(self, messages: list[dict], user_input: str) -> str:
        key = settings.OPENAI_API_KEY
        if not key:
            raise LLMFallbackError("OpenAI: no API key")
        msgs = [{"role": m["role"], "content": m["content"]} for m in messages] + [{"role": "user", "content": user_input}]
        r = await self._client().post(
            "https://api.openai.com/v1/chat/completions",
            json={"model": settings.OPENAI_MODEL, "messages": msgs, "max_tokens": 300},
            headers={"Authorization": f"Bearer {key}"},
        )
        if r.status_code != 200:
            raise LLMFallbackError(f"OpenAI {r.status_code}: {r.text[:200]}")
        return r.json()["choices"][0]["message"]["content"]

    async def _call_anthropic(self, messages: list[dict], user_input: str) -> str:
        key = settings.ANTHROPIC_API_KEY
        if not key:
            raise LLMFallbackError("Anthropic: no API key")
        msgs = [{"role": m["role"], "content": m["content"]} for m in messages] + [{"role": "user", "content": user_input}]
        r = await self._client().post(
            "https://api.anthropic.com/v1/messages",
            json={"model": settings.ANTHROPIC_MODEL, "messages": msgs, "max_tokens": 300},
            headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
        )
        if r.status_code != 200:
            raise LLMFallbackError(f"Anthropic {r.status_code}: {r.text[:200]}")
        return r.json()["content"][0]["text"]

    async def _call_ollama(self, messages: list[dict], user_input: str) -> str:
        msgs = [{"role": m["role"], "content": m["content"]} for m in messages] + [{"role": "user", "content": user_input}]
        try:
            r = await self._client().post(
                "http://localhost:11434/api/chat",
                json={"model": settings.OLLAMA_MODEL, "messages": msgs, "stream": False},
                timeout=httpx.Timeout(120.0, connect=5.0),
            )
            if r.status_code != 200:
                raise LLMFallbackError(f"Ollama {r.status_code}: {r.text[:200]}")
            return r.json()["message"]["content"]
        except httpx.ConnectError:
            raise LLMFallbackError("Ollama: not running on localhost:11434")

    def _providers(self):
        return [
            ("gemini", self._call_gemini),
            ("groq", self._call_groq),
            ("ollama", self._call_ollama),
            ("openai", self._call_openai),
            ("anthropic", self._call_anthropic),
        ]

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=8),
           retry=retry_if_exception_type(LLMFallbackError))
    async def generate_response(self, messages: list[dict], customer_input: str,
                                rag_context: str | None = None) -> str:
        if rag_context:
            messages = list(messages) + [{"role": "system", "content": f"Relevant info:\n{rag_context}"}]

        last_error = None
        for name, caller in self._providers():
            try:
                text = await caller(messages, customer_input)
                logger.info("llm_ok", provider=name)
                return text
            except LLMFallbackError as e:
                logger.warning("llm_fallback", provider=name, error=str(e))
                last_error = e
                if settings.LLM_FALLBACK_ENABLED:
                    continue
                raise

        raise LLMFallbackError(f"All providers failed. Last: {last_error}")

    async def generate_summary(self, transcript: list[dict]) -> str:
        return await self.generate_response(
            [{"role": "system", "content": "Summarize this insurance call in 2-3 sentences: customer interest, concerns, next action."}],
            str(transcript),
        )

    async def analyze_sentiment(self, transcript: list[dict]) -> float:
        result = await self.generate_response(
            [{"role": "system", "content": "Return a number -1.0 to 1.0 for sentiment in this call."}],
            str(transcript),
        )
        try:
            return float(result.strip())
        except ValueError:
            return 0.0
