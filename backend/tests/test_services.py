"""Unit tests for the AI Cold Calling backend."""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4


class TestLeadScoring:
    @pytest.fixture
    def scorer(self):
        from app.services.lead_scoring import LeadScoringEngine
        return LeadScoringEngine()

    def test_score_new_lead(self, scorer):
        lead = {"status": "pending", "language": "urdu", "call_count": 0}
        result = scorer.score(lead)
        assert 0 <= result["score"] <= 100
        assert result["tier"] in ("hot", "warm", "cool", "cold")
        assert "signals" in result

    def test_score_interested_lead(self, scorer):
        lead = {"status": "interested", "language": "urdu", "call_count": 0}
        result = scorer.score(lead)
        assert result["score"] >= 30
        assert result["tier"] in ("cool", "warm", "hot")

    def test_score_dnc_lead(self, scorer):
        lead = {"status": "dnc", "language": "urdu", "call_count": 5}
        result = scorer.score(lead)
        assert result["score"] < 50

    def test_rank_leads(self, scorer):
        leads = [
            {"status": "interested", "language": "urdu", "call_count": 0},
            {"status": "not_interested", "language": "urdu", "call_count": 3},
            {"status": "pending", "language": "english", "call_count": 0},
        ]
        ranked = scorer.rank_leads(leads)
        assert len(ranked) == 3
        assert ranked[0]["lead_score"] >= ranked[1]["lead_score"] >= ranked[2]["lead_score"]


class TestAuthUtils:
    def test_hash_and_verify_password(self):
        from app.utils.auth import hash_password, verify_password
        pw = "TestPassword123!"
        hashed = hash_password(pw)
        assert hashed != pw
        assert verify_password(pw, hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    @patch("app.utils.auth.settings")
    def test_create_and_decode_token(self, mock_settings):
        from app.utils.auth import create_access_token, decode_token
        mock_settings.JWT_SECRET_KEY = "test-secret-key"
        mock_settings.JWT_ALGORITHM = "HS256"
        mock_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60

        user_id = uuid4()
        token = create_access_token(user_id, "agent")
        assert token is not None

        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["role"] == "agent"
        assert payload["type"] == "access"


class TestHelpers:
    def test_sanitize_phone(self):
        from app.utils.helpers import sanitize_phone
        assert sanitize_phone("+923001234567") == "+923001234567"
        assert sanitize_phone("03001234567").endswith("3001234567")

    def test_truncate(self):
        from app.utils.helpers import truncate
        assert truncate("short") == "short"
        assert len(truncate("x" * 1000)) <= 503

    def test_pagination_meta(self):
        from app.utils.helpers import pagination_meta
        meta = pagination_meta(1, 50, 120)
        assert meta["total_pages"] == 3
        assert meta["has_next"] is True
        assert meta["has_prev"] is False


class TestRAGService:
    @pytest.mark.asyncio
    async def test_query_returns_results(self):
        from app.services.rag_service import RAGService
        svc = RAGService()
        result = await svc.query("health insurance")
        assert isinstance(result, str)
        assert len(result) > 0


class TestCacheService:
    @pytest.mark.asyncio
    async def test_set_and_get(self):
        from app.services.cache_service import CacheService
        svc = CacheService()
        await svc.set("test_key", {"data": 123})
        result = await svc.get("test_key")
        assert result == {"data": 123}

    @pytest.mark.asyncio
    async def test_delete(self):
        from app.services.cache_service import CacheService
        svc = CacheService()
        await svc.set("del_key", "value")
        await svc.delete("del_key")
        assert await svc.get("del_key") is None
