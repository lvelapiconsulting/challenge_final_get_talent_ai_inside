from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=10)


class Source(BaseModel):
    document: str
    page: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]