"""
Test the full AI conversation pipeline locally without any telephony service.

Usage:
  1. Ensure backend .env has GOOGLE_API_KEY and ELEVENLABS_API_KEY set
  2. pip install sounddevice numpy scipy (or use text-only mode)
  3. python test_ai_pipeline.py

This will:
  - Fetch a lead from the database
  - Simulate an AI conversation (text-in, text-out)
  - Generate TTS audio via ElevenLabs
  - Save transcript to the call_logs table
"""

import asyncio
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
os.environ["ENVIRONMENT"] = "development"

from app.database import async_session
from app.models.call_log import CallLog
from app.models.lead import Lead
from app.services.multi_llm_service import MultiLLMService
from app.services.tts_service import TextToSpeechService
from app.services.stt_service import SpeechToTextService
from sqlalchemy import select


def play_audio(filepath: str):
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pass
        pygame.mixer.quit()
        return True
    except ImportError:
        try:
            from playsound import playsound
            playsound(filepath)
            return True
        except ImportError:
            print(f"  [Audio saved to: {filepath}]")
            return False


async def test_conversation():
    print("=" * 60)
    print("  AI Health Insurance Cold Calling - Pipeline Test")
    print("=" * 60)

    async with async_session() as db:
        result = await db.execute(
            select(Lead).where(Lead.status == "pending").limit(1)
        )
        lead = result.scalar_one_or_none()

        if not lead:
            print("No pending leads found. Please seed some leads first.")
            print("Run: python scripts/seed_data.py")
            return

        print(f"\n📋 Lead: {lead.name} ({lead.phone})")
        print(f"   Language: {lead.language}")
        print(f"   Campaign: {lead.assigned_campaign_id}")

        call_log = CallLog(
            lead_id=lead.id,
            campaign_id=lead.assigned_campaign_id,
            direction="outbound",
            status="in-progress",
        )
        db.add(call_log)
        await db.commit()
        await db.refresh(call_log)

        tts = TextToSpeechService()
        llm = MultiLLMService()
        transcript = []

        greeting = "Hello! I'm calling from NCAI Insurance about health insurance plans. We offer coverage from basic hospitalization to full family plans. Do you have a moment to discuss?"

        audio = await tts.synthesize(greeting)
        greeting_file = os.path.join(tempfile.gettempdir(), f"test_greeting_{call_log.id}.mp3")
        with open(greeting_file, "wb") as f:
            f.write(audio)
        transcript.append({"role": "ai", "text": greeting})

        print(f"\n🤖 AI: {greeting}")
        play_audio(greeting_file)

        turn = 0
        max_turns = 6
        use_mic = False

        try:
            import sounddevice
            use_mic = True
            print("\n🎤 Microphone available! Speak naturally after each prompt.")
        except ImportError:
            print("\n⌨️  Type your responses (or install sounddevice for voice input)")

        while turn < max_turns:
            turn += 1
            print(f"\n--- Turn {turn} ---")

            if use_mic:
                user_text = await SpeechToTextService.transcribe_mic()
            else:
                user_text = input("You: ").strip()
                if not user_text:
                    user_text = "I'm interested, tell me more."

            print(f"🗣️  You said: {user_text}")
            transcript.append({"role": "user", "text": user_text})

            context = "\n".join([f"{t['role']}: {t['text']}" for t in transcript])
            ai_reply = await llm.generate(
                system_prompt="You are a professional health insurance agent. Be concise, friendly, and informative. Answer questions about plans, coverage, and pricing. If they seem interested, offer to schedule a follow-up. End naturally with goodbye when appropriate.",
                user_message=context + "\nAI:",
            )
            print(f"🤖 AI: {ai_reply}")
            transcript.append({"role": "ai", "text": ai_reply})

            audio = await tts.synthesize(ai_reply)
            reply_file = os.path.join(tempfile.gettempdir(), f"test_reply_{call_log.id}_{turn}.mp3")
            with open(reply_file, "wb") as f:
                f.write(audio)
            play_audio(reply_file)

            if any(w in ai_reply.lower() for w in ["goodbye", "have a great day", "take care", "allah hafiz"]):
                print("\n✅ AI ended the conversation.")
                break

        call_log.transcript = transcript
        call_log.status = "completed"
        call_log.duration_seconds = turn * 15
        await db.commit()

        print("\n" + "=" * 60)
        print("  ✅ PIPELINE TEST COMPLETE")
        print(f"  📝 {turn} turns, transcript saved to DB")
        print("=" * 60)

        print("\n📄 Final transcript:")
        for t in transcript:
            role = "🤖 AI" if t["role"] == "ai" else "🗣️ You"
            print(f"  {role}: {t['text']}")


if __name__ == "__main__":
    asyncio.run(test_conversation())
