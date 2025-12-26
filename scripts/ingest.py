import os
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config import settings


def load_kb_docs() -> list[Document]:
    kb_dir = Path(settings.kb_dir)
    docs: list[Document] = []

    for path in kb_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".txt"}:
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        docs.append(Document(page_content=text, metadata={"source": str(path)}))

    return docs


def main() -> None:
    if settings.mock_mode:
        print("Mock mode enabled; skipping Chroma ingest.")
        return

    raw_docs = load_kb_docs()
    if not raw_docs:
        print(f"No docs found in {settings.kb_dir}")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = []
    for doc in raw_docs:
        for i, chunk in enumerate(splitter.split_text(doc.page_content)):
            chunks.append(
                Document(
                    page_content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_id": f"{Path(doc.metadata['source']).name}:{i}",
                    },
                )
            )

    embeddings = OpenAIEmbeddings(
        model=settings.openai_embeddings_model,
        api_key=settings.openai_api_key,
    )

    vs = Chroma(
        collection_name="kb_docs",
        embedding_function=embeddings,
        persist_directory=settings.chroma_dir,
    )

    # Reset and re-add using public API
    vs.delete_collection()
    vs = Chroma(
        collection_name="kb_docs",
        embedding_function=embeddings,
        persist_directory=settings.chroma_dir,
    )
    vs.add_documents(chunks)
    print(f"Ingested {len(chunks)} chunks into Chroma at {settings.chroma_dir}")


if __name__ == "__main__":
    main()
