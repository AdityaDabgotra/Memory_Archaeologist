from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from dotenv import load_dotenv
import os
import pickle

load_dotenv()

VECTOR_STORE_PATH = "data/vector_store"

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    )


def build_vector_store(chunks : list[Document]) -> FAISS:
    print("Embedding chunks (this may take a minute) ...")
    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(chunks,embeddings)

    os.makedirs(VECTOR_STORE_PATH,exist_ok=True)
    vector_store.save_local(VECTOR_STORE_PATH)
    print(f"Vector Store saved to {VECTOR_STORE_PATH}")
    return vector_store


def load_vector_store() -> FAISS:
    embeddings = get_embeddings()
    return FAISS.load_local(
        VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

