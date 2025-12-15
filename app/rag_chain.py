import os
from typing import Iterable

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.config import settings
from app.schemas import AskResult


def get_vectorstore() -> Chroma:
    embeddings = OpenAIEmbeddings(
        model=settings.openai_embeddings_model,
        api_key=settings.openai_api_key,
    )
    return Chroma(
        collection_name="kb",
        embedding_function=embeddings,
        persist_directory=settings.chroma_dir,
    )


def retrieve(question: str, k: int = 4) -> list[Document]:
    vs = get_vectorstore()
    return vs.similarity_search(question, k=k)


def build_chain():
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
