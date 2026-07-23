from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config import settings

SYSTEM_PROMPT = """You are an AI calling assistant for a health insurance company in Pakistan.
Your role is to conduct professional outbound cold calls in a natural, conversational manner.

Key Guidelines:
1. Language: Speak in Urdu primarily, mix with English when needed. Be warm and respectful.
2. Purpose: Introduce health insurance plans, explain benefits, qualify leads.
3. Tone: Professional, friendly, and empathetic. Never aggressive.
4. Objection Handling: If customer says not interested, politely ask for feedback. If price concern, explain value. If busy, offer callback.
5. Data Privacy: Never ask for CNIC, bank details, or sensitive personal information.
6. Compliance: Always mention this is a courtesy call. Respect "not interested" decisions.
7. Lead Qualification: Assess interest level (High/Medium/Low), affordability, and decision timeline.
8. Call Flow: Greeting → Introduction → Problem/Pain Point → Solution/Plan → Objection Handling → Call to Action → Closing.

Insurance Plan Information:
- Plans range from basic hospitalization (PKR 2,000/month) to comprehensive family plans (PKR 15,000/month)
- Coverage includes: hospitalization, day-care procedures, maternity, pre-existing conditions (after 1 year)
- Claim process: Cashless at 500+ hospitals across Pakistan
- Network hospitals: All major cities including Karachi, Lahore, Islamabad, Peshawar, Quetta

If the customer asks something you don't know, politely say you'll have a human expert call them back with details.
Always end the call by summarizing next steps and thanking the customer."""


class LLMService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=0.7,
            max_tokens=300,
            google_api_key=settings.GOOGLE_API_KEY,
        )

    def _build_prompt(self, transcript: list[dict] | None = None) -> list:
        messages = [SystemMessage(content=SYSTEM_PROMPT)]

        if transcript:
            for entry in transcript:
                role = entry.get("role", "user")
                content = entry.get("content", "")
                if role == "assistant":
                    messages.append(AIMessage(content=content))
                else:
                    messages.append(HumanMessage(content=content))

        return messages

    async def generate_response(
        self,
        transcript: list[dict],
        customer_input: str,
        rag_context: str | None = None,
    ) -> str:
        messages = self._build_prompt(transcript)

        if rag_context:
            messages.append(
                SystemMessage(
                    content=f"Relevant information from insurance documents:\n{rag_context}"
                )
            )

        messages.append(HumanMessage(content=customer_input))

        response = await self.llm.ainvoke(messages)
        return response.content

    async def generate_summary(self, transcript: list[dict]) -> str:
        messages = [
            SystemMessage(
                content="Summarize this insurance cold call conversation in 2-3 Urdu/English sentences. "
                "Include: customer interest level, key concerns, and recommended next action."
            ),
            HumanMessage(content=str(transcript)),
        ]

        response = await self.llm.ainvoke(messages)
        return response.content

    async def analyze_sentiment(self, transcript: list[dict]) -> float:
        messages = [
            SystemMessage(
                content="Analyze the customer's sentiment in this call. "
                "Return only a number between -1.0 (very negative) and 1.0 (very positive)."
            ),
            HumanMessage(content=str(transcript)),
        ]

        response = await self.llm.ainvoke(messages)
        try:
            return float(response.content.strip())
        except ValueError:
            return 0.0
