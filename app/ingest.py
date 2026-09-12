from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import EMBEDDING_MODEL, KB_DIR, VECTOR_DIR


def load_documents():
    from langchain_core.documents import Document

    documents = []
    for path in sorted(Path(KB_DIR).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        source = ""
        for line in text.splitlines():
            if line.startswith("Source URL:"):
                source = line.split(":", 1)[1].strip()
                break
        documents.append(Document(
            page_content=text,
            metadata={"source": source, "file": path.name},
        ))
    return documents


def build_vector_store():
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    chunks = splitter.split_documents(load_documents())
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma.from_documents(chunks, embeddings, persist_directory=str(VECTOR_DIR))


if __name__ == "__main__":
    build_vector_store()
    print(f"Vector store written to {VECTOR_DIR}")
