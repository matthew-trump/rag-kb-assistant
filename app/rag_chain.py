import os
from pathlib import Path
from typing import Iterable

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.config import settings
from app.schemas import AskResult


def get_vectorstore() -> Chroma:
    if settings.mock_mode:
        raise RuntimeError("Vector store is not used in mock mode")
    embeddings = OpenAIEmbeddings(
        model=settings.openai_embeddings_model,
        api_key=settings.openai_api_key,
    )
    return Chroma(
        collection_name="kb_docs",
        embedding_function=embeddings,
        persist_directory=settings.chroma_dir,
    )


def retrieve(question: str, k: int = 4) -> list[Document]:
    if settings.mock_mode:
        return retrieve_mock(k=k)
    vs = get_vectorstore()
    return vs.similarity_search(question, k=k)


def build_chain():
    if settings.mock_mode:
        return MockChain()

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )
    parser = PydanticOutputParser(pydantic_object=AskResult)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful KB assistant. Answer ONLY using the provided context. "
                "If the answer is not in the context, say you don't know.\n\n{format_instructions}",
            ),
            ("human", "Question:\n{question}\n\nContext:\n{context}\n"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())

    return prompt | llm | parser


def format_context(docs: Iterable[Document]) -> str:
    parts = []
    for i, d in enumerate(docs):
        source = d.metadata.get("source", "unknown")
        chunk_id = d.metadata.get("chunk_id", str(i))
        parts.append(f"[{i}] source={source} chunk_id={chunk_id}\n{d.page_content}")
    return "\n\n---\n\n".join(parts)


def retrieve_mock(k: int = 4) -> list[Document]:
    docs: list[Document] = []
    kb_dir = Path(settings.kb_dir)
    for path in kb_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        docs.append(
            Document(
                page_content=text,
                metadata={"source": str(path), "chunk_id": f"{path.name}:0"},
            )
        )
    return docs[:k]


class MockChain:
    """Minimal stand-in for LLM chain when mock_mode is enabled."""

    def invoke(self, inputs: dict) -> AskResult:
        return AskResult(
            answer=f"[MOCK ANSWER] {inputs.get('question', '')}".strip(),
            citations=[],
            confidence=0.0,
        )
