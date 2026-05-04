from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def chunk_documents(docs: list[Document]) -> list[Document]:
    docs = [d for d in docs if d.page_content.strip()]
    print(f"Non-empty documents to chunk: {len(docs)}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
    )

    chunks = splitter.split_documents(docs)

    source_chunk_count = {}
    for chunk in chunks:
        src = chunk.metadata.get("source", "unknown")
        source_chunk_count[src] = source_chunk_count.get(src, 0) + 1
        chunk.metadata["chunk_index"] = source_chunk_count[src]

    print(f"Created {len(chunks)} chunks from {len(docs)} pages")
    return chunks