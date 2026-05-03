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