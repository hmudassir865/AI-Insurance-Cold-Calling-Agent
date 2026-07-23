from typing import Callable

from app.services.multi_llm_service import MultiLLMService
from app.services.rag_service import RAGService
from app.services.stt_service import SpeechToTextService
from app.services.tts_service import TextToSpeechService
from app.services.lead_scoring import LeadScoringEngine
from app.services.cache_service import CacheService
from app.config import settings

SYSTEM_PROMPT = """You are an AI calling assistant for NCAI Insurance, a health insurance company in the United States.
Your role is to conduct professional outbound cold calls in a natural, conversational manner.

Key Guidelines:
1. Language: Speak in English only. Be warm and respectful.
2. Purpose: Introduce health insurance plans, explain benefits, qualify leads.
3. Tone: Professional, friendly, and empathetic. Never aggressive.
4. Objection Handling: If customer says not interested, politely ask for feedback. If price concern, explain value. If busy, offer callback.
5. Data Privacy: Never ask for SSN, bank details, or sensitive personal information.
6. Compliance: Always mention this is a courtesy call. Respect "not interested" decisions.
7. Lead Qualification: Assess interest level (High/Medium/Low), affordability, and decision timeline.
8. Call Flow: Greeting → Introduction → Problem/Pain Point → Solution/Plan → Objection Handling → Call to Action → Closing.

Insurance Plan Information:
- Plans range from basic hospitalization ($150/month) to comprehensive family plans ($500/month)
- Coverage includes: hospitalization, day-care procedures, maternity, pre-existing conditions (after 1 year)
- Claim process: Cashless at 5,000+ hospitals across the United States
- Network hospitals: All major cities including New York, Los Angeles, Chicago, Houston, Phoenix

If the customer asks something you don't know, politely say you'll have a human expert call them back with details.
Always end the call by summarizing next steps and thanking the customer. Keep responses concise (2-4 sentences)."""


class ConversationService:
    def __init__(self):
        self.llm = MultiLLMService()
        self.rag = RAGService()
        self.stt = SpeechToTextService()
        self.tts = TextToSpeechService()
        self.scorer = LeadScoringEngine()
        self.cache = CacheService()

    async def process_audio_input(
        self,
        audio_bytes: bytes,
        transcript: list[dict],
        language: str = "ur",
        on_progress: Callable | None = None,
    ):
        if on_progress:
            on_progress("Transcribing audio...")

        customer_text = await self.stt.transcribe(audio_bytes, language=language)
        transcript.append({"role": "user", "content": customer_text})

        if on_progress:
            on_progress("Generating AI response...")

        rag_context = await self.rag.query(customer_text)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for entry in transcript[:-1]:
            messages.append({
                "role": entry.get("role", "user"),
                "content": entry.get("content", ""),
            })

        ai_response = await self.llm.generate_response(
            messages=messages,
            customer_input=customer_text,
            rag_context=rag_context,
        )
        transcript.append({"role": "assistant", "content": ai_response})

        if on_progress:
            on_progress("Synthesizing speech...")

        audio_response = await self.tts.synthesize(ai_response)

        return {
            "customer_text": customer_text,
            "ai_response": ai_response,
            "audio_bytes": audio_response,
            "rag_context": rag_context if rag_context else None,
        }

    async def process_text_input(
        self,
        customer_input: str,
        transcript: list[dict],
    ):
        transcript.append({"role": "user", "content": customer_input})

        rag_context = await self.rag.query(customer_input)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for entry in transcript[:-1]:
            messages.append({
                "role": entry.get("role", "user"),
                "content": entry.get("content", ""),
            })

        ai_response = await self.llm.generate_response(
            messages=messages,
            customer_input=customer_input,
            rag_context=rag_context,
        )
        transcript.append({"role": "assistant", "content": ai_response})

        return {
            "customer_text": customer_input,
            "ai_response": ai_response,
            "rag_context": rag_context if rag_context else None,
        }

    async def finalize_conversation(self, transcript: list[dict]) -> dict:
        summary = await self.llm.generate_summary(transcript)
        sentiment = await self.llm.analyze_sentiment(transcript)

        last_user_message = ""
        for msg in reversed(transcript):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break

        interested_keywords = [
            "interested", "yes", "sure", "tell me more", "price",
            "cost", "plan",
        ]
        not_interested_keywords = [
            "not interested", "no", "busy", "later", "no thanks",
        ]
        lead_status = "callback"
        for kw in interested_keywords:
            if kw in last_user_message.lower():
                lead_status = "interested"
                break
        for kw in not_interested_keywords:
            if kw in last_user_message.lower():
                lead_status = "not_interested"
                break

        return {
            "summary": summary,
            "sentiment_score": sentiment,
            "lead_status": lead_status,
        }

