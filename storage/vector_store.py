from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from dotenv import load_dotenv
import os
import pickle

load_dotenv()

VECTOR_STORE_PATH = "data/vector_store"
INGESTED_LOG = "data/ingested_files.txt"

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    )


def build_vector_store(chunks : list[Document]) -> FAISS:
    chunks = list(chunks)
    print(f"Vector store receiving {len(chunks)} chunks")
    print("Embedding chunks (this may take a minute)...")
    embeddings = get_embeddings()
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

    if os.path.exists(f"{VECTOR_STORE_PATH}/index.faiss"):
        print(" Existing vector store found — merging new chunks...")
        existing = FAISS.load_local(
            VECTOR_STORE_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        new_store = FAISS.from_documents(chunks, embeddings)
        existing.merge_from(new_store)
        existing.save_local(VECTOR_STORE_PATH)
        print(f" Merged {len(chunks)} new chunks into existing store")
        return existing
    else:
        print(" Creating new vector store...")
        store = FAISS.from_documents(chunks, embeddings)
        store.save_local(VECTOR_STORE_PATH)
        print(f" Vector store saved with {len(chunks)} chunks")
        return store


def load_vector_store() -> FAISS:
    embeddings = get_embeddings()
    return FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


def similarity_search(query: str ,k:int = 5, filters: dict = None):
    store = load_vector_store()

    if filter:
        results = store.similarity_search(
            query,k=k,
            filter=filters
        )
    else:
        results = store.similarity_search(
            query,k=k
        )
    
    return results


def get_ingested_files() -> set:
    """Return set of already-ingested file paths."""
    if not os.path.exists(INGESTED_LOG):
        return set()
    with open(INGESTED_LOG, "r") as f:
        return set(line.strip() for line in f.readlines())


def mark_as_ingested(filepath: str):
    """Record that a file has been ingested."""
    os.makedirs("data", exist_ok=True)
    with open(INGESTED_LOG, "a") as f:
        f.write(filepath + "\n")