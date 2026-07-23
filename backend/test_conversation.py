import asyncio
from app.services.conversation_service import ConversationService


async def test():
    svc = ConversationService()
    transcript = []

    result1 = await svc.process_text_input("Assalam-o-Alaikum", transcript)
    print("AI:", result1["ai_response"])
    print()

    result2 = await svc.process_text_input("Mujhe health insurance ke baare mein janna hai", transcript)
    print("AI:", result2["ai_response"])
    print()

    result3 = await svc.process_text_input("Kitna kharcha hai?", transcript)
    print("AI:", result3["ai_response"])
    print()

    final = await svc.finalize_conversation(transcript)
    print("Summary:", final["summary"])
    print("Sentiment:", final["sentiment_score"])
    print("Lead Status:", final["lead_status"])


asyncio.run(test())
