from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class Citation(BaseModel):
    source: str
    chunk_id: str
    excerpt: str


class AskResult(BaseModel):
    answer: str
    citations: list[Citation] = []
    confidence: float = Field(ge=0.0, le=1.0)


class AskResponse(BaseModel):
    task_id: str
    run_id: str


class RunResponse(BaseModel):
    run_id: str
    status: str
    question: str
    result: dict | None
    error: str | None
