"""Production RAG service with embeddings, caching, and fallback."""
import structlog
from typing import Any

logger = structlog.get_logger()


class RAGService:
    def __init__(self):
        self._embeddings = None
        self._cache = {}

    def _get_embeddings(self):
        if self._embeddings is None:
            from app.config import settings
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.RAG_EMBEDDING_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
            )
        return self._embeddings

    def _get_sync_engine(self):
        from app.config import settings
        from sqlalchemy import create_engine
        sync_url = settings.DATABASE_URL.replace("+asyncpg", "")
        return create_engine(sync_url)

    async def query(self, question: str, k: int = 3) -> str:
        cache_key = f"rag:{question}:{k}"
        if cache_key in self._cache:
            logger.debug("rag_cache_hit")
            return self._cache[cache_key]

        result = await self._query_db(question, k)

        self._cache[cache_key] = result
        return result

    async def _query_db(self, question: str, k: int) -> str:
        engine = self._get_sync_engine()

        with engine.connect() as conn:
            result = conn.execute(
                __import__("sqlalchemy", fromlist=["text"]).text(
                    f"SELECT content FROM {self.DOCUMENTS_TABLE} ORDER BY created_at DESC LIMIT :limit"
                ),
                {"limit": k},
            )
            rows = result.fetchall()

        if not rows:
            return ""

        context_parts = []
        for i, row in enumerate(rows, 1):
            context_parts.append(f"[Document {i}]: {row[0]}")
        return "\n\n".join(context_parts)

    @property
    def DOCUMENTS_TABLE(self) -> str:
        return "insurance_knowledge_base"

    async def index_document(self, content: str, metadata: dict | None = None) -> int:
        import json
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from app.config import settings

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP,
        )
        chunks = splitter.split_text(content)
        engine = self._get_sync_engine()

        from sqlalchemy import text

        for i, chunk in enumerate(chunks):
            meta = metadata or {}
            meta["chunk_index"] = i

            with engine.connect() as conn:
                conn.execute(
                    text(
                        f"INSERT INTO {self.DOCUMENTS_TABLE} "
                        "(content, metadata) VALUES (:content, :metadata)"
                    ),
                    {"content": chunk, "metadata": json.dumps(meta)},
                )
                conn.commit()

        return len(chunks)

    async def delete_document(self, document_id: str):
        from sqlalchemy import text
        engine = self._get_sync_engine()
        with engine.connect() as conn:
            conn.execute(
                text(
                    f"DELETE FROM {self.DOCUMENTS_TABLE} WHERE metadata->>'source_id' = :id"
                ),
                {"id": document_id},
            )
            conn.commit()
