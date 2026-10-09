from fastapi import APIRouter, HTTPException

from app.rag.pipeline import RAGPipeline
from app.schemas.chat import ChatRequest, ChatResponse


router = APIRouter()

# Inicializamos el pipeline una sola vez
pipeline = RAGPipeline()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:
        result = pipeline.ask(
            question=request.question
        )

        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )