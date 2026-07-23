from fastapi import APIRouter, Depends, Query
from app.services.rag_service import RAGService
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/api/rag", tags=["RAG"], dependencies=[Depends(get_current_user)])
rag_service = RAGService()


@router.get("/query")
async def query_knowledge(
    question: str = Query(..., min_length=3, description="The question to ask the knowledge base"),
    k: int = Query(3, ge=1, le=10),
):
    answer = await rag_service.query(question, k=k)
    return {"answer": answer, "sources": k}
