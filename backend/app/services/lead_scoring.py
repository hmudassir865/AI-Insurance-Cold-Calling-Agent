"""Lead scoring engine that ranks leads by conversion likelihood."""
import math
from datetime import datetime, timezone


class LeadScoringEngine:
    WEIGHTS = {
        "language_match": 15,
        "call_history": 25,
        "time_of_day": 10,
        "previous_interest": 30,
        "response_rate": 20,
    }

    def score(self, lead: dict) -> dict:
        score = 0
        signals = {}

        lang = lead.get("language", "urdu")
        if lang == "urdu":
            signals["language_match"] = 15
        elif lang == "punjabi":
            signals["language_match"] = 12
        else:
            signals["language_match"] = 10

        status = lead.get("status", "pending")
        status_scores = {
            "callback": 80, "interested": 70, "pending": 50,
            "busy": 30, "not_interested": 10, "wrong_number": 0, "dnc": 0,
        }
        signals["previous_interest"] = status_scores.get(status, 50)

        if lead.get("call_count", 0) > 0:
            signals["call_history"] = max(0, 100 - (lead["call_count"] * 10))
        else:
            signals["call_history"] = 50

        now = datetime.now(timezone.utc)
        hour = now.hour
        if 9 <= hour <= 12 or 16 <= hour <= 19:
            signals["time_of_day"] = 15
        elif 13 <= hour <= 15:
            signals["time_of_day"] = 10
        else:
            signals["time_of_day"] = 5

        signals["response_rate"] = max(0, 100 - (lead.get("call_count", 0) * 20))

        for key, weight in self.WEIGHTS.items():
            score += signals.get(key, 0) * (weight / 100)

        score = min(100, max(0, score))
        tier = self._tier(score)

        return {
            "score": round(score, 1),
            "tier": tier,
            "signals": signals,
            "recommendation": self._recommendation(tier),
        }

    def _tier(self, score: float) -> str:
        if score >= 75:
            return "hot"
        elif score >= 50:
            return "warm"
        elif score >= 25:
            return "cool"
        return "cold"

    def _recommendation(self, tier: str) -> str:
        return {
            "hot": "Call immediately — high conversion probability",
            "warm": "Call within next campaign batch",
            "cool": "Call during off-peak or SMS first",
            "cold": "Skip or remove from active campaign",
        }.get(tier, "No recommendation")

    def rank_leads(self, leads: list[dict]) -> list[dict]:
        scored = []
        for lead in leads:
            result = self.score(lead)
            scored.append({**lead, "lead_score": result["score"], "lead_tier": result["tier"]})
        return sorted(scored, key=lambda x: x["lead_score"], reverse=True)
