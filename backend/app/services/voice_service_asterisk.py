import asyncio
import os
import tempfile
from app.config import settings
from app.services.conversation_service import ConversationService
from app.services.llm_service import LLMService
from app.services.multi_llm_service import MultiLLMService
from app.services.stt_service import SpeechToTextService
from app.services.tts_service import TextToSpeechService
from app.database import async_session
from app.models.call_log import CallLog
from app.models.lead import Lead, LeadStatus
from sqlalchemy import select


class VoiceServiceAsterisk:
    @classmethod
    async def test_conversation(cls, lead_id: str, campaign_id: str):
        async with async_session() as db:
            result = await db.execute(select(Lead).where(Lead.id == lead_id))
            lead = result.scalar_one_or_none()
            if not lead:
                return {"error": "Lead not found"}

            call_log = CallLog(
                lead_id=lead.id,
                campaign_id=campaign_id,
                direction="outbound",
                status="in-progress",
            )
            db.add(call_log)
            await db.commit()
            await db.refresh(call_log)

            transcript = []
            greeting = "Hello! I'm calling from NCAI Insurance about our health insurance plans."

            tts = TextToSpeechService()
            first_audio = await tts.synthesize(greeting)
            greeting_file = os.path.join(tempfile.gettempdir(), f"greeting_{call_log.id}.mp3")
            with open(greeting_file, "wb") as f:
                f.write(first_audio)

            transcript.append({"role": "ai", "text": greeting})

            print(f"\n{'='*60}")
            print(f"📞 AI Agent calling {lead.name} ({lead.phone})")
            print(f"🎙️  Playing: {greeting}")
            print(f"   Audio file: {greeting_file}")
            print(f"{'='*60}\n")

            turn = 0
            max_turns = 5
            while turn < max_turns:
                print(f"\n[Turn {turn + 1}] Speak into the microphone after pressing Enter...")
                input("Press Enter when ready to speak... ")

                stt_service = SpeechToTextService()
                user_text = await stt_service.transcribe_mic()
                print(f"🗣️  You said: {user_text}")

                transcript.append({"role": "user", "text": user_text})

                llm_service = MultiLLMService()
                context = "\n".join([f"{t['role']}: {t['text']}" for t in transcript])
                ai_reply = await llm_service.generate_response([{"role": "system", "content": "You are a health insurance agent. Respond naturally and concisely. Ask if they have questions."}], context + "\nAI:")
                print(f"🤖 AI: {ai_reply}")

                transcript.append({"role": "ai", "text": ai_reply})

                audio_data = await tts.synthesize(ai_reply)
                reply_file = os.path.join(tempfile.gettempdir(), f"reply_{call_log.id}_{turn}.mp3")
                with open(reply_file, "wb") as f:
                    f.write(audio_data)
                print(f"   Audio file: {reply_file}")

                if "goodbye" in ai_reply.lower() or "thank you" in ai_reply.lower():
                    print("\n✅ AI ended the conversation.")
                    break
                turn += 1

            call_log.transcript = transcript
            call_log.status = "completed"
            await db.commit()

            print(f"\n{'='*60}")
            print(f"✅ Call complete! {turn + 1} turns")
            print(f"📝 Transcript saved to database")
            print(f"{'='*60}")

            return {"status": "ok", "turns": turn + 1, "transcript": transcript}

    @classmethod
    async def handle_agi_request(cls, data: dict):
        """Handle Asterisk AGI webhook requests."""
        pass
