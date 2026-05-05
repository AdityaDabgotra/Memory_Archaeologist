from langchain_community.document_loaders import (
    PyMuPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
from storage.vector_store import get_ingested_files, mark_as_ingested
from langchain_core.documents import Document
from pathlib import Path
from datetime import datetime
import os

LOADER_MAP = {
    ".pdf":  PyMuPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt":  TextLoader,
    ".md":   UnstructuredMarkdownLoader,
}

def infer_date_from_path(filepath:str)->str:
    import re
    text = filepath.replace("\\","/")

    match = re.search(r"(\d{4}[-_]\d{2}[-_]\d{2})", text)
    if match:
        return match.group(1).replace("_","-")
    
    match = re.search(r"(\d{4}[-_]\d{2})", text)
    if match:
        return match.group(1).replace("_", "-") + "-01"
    
    match = re.search(r"(20\d{2})", text)
    if match:
        return match.group(1) + "-01-01"
    
    mod_time = os.path.getmtime(filepath)
    return datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d")


def infer_source_type(filepath:str)->str:
    path_lower = filepath.lower()

    if any(k in path_lower for k in ["journal", "diary", "daily"]):
        return "journal"
    if any(k in path_lower for k in ["email", "mail", "gmail"]):
        return "email"
    if any(k in path_lower for k in ["note", "notes", "obsidian", "notion"]):
        return "note"
    if any(k in path_lower for k in ["book", "highlight", "kindle"]):
        return "book_highlight"
    return "document"


def load_file(filepath:str)->list[Document]:
    ext = Path(filepath).suffix.lower()
    loader_class = LOADER_MAP.get(ext)

    if not loader_class:
        print(f"Skipping unsupported file type :{filepath}")
        return[]
    
    try:
        loader = loader_class(filepath)
        docs = loader.load()
    except Exception as e:
        print(f"Failed to load {filepath}: {e}")
        return []
    
    date = infer_date_from_path(filepath)
    source_type = infer_source_type(filepath)
    filename = Path(filepath).name

    for doc in docs:
        doc.metadata.update({
            "source":      filepath,
            "filename":    filename,
            "source_type": source_type,
            "date":        date,
            "year":        date[:4],
            "month":       date[:7],
        })
    
    return docs


def load_directory(directory: str) -> list[Document]:
    all_docs = []
    supported_exts = set(LOADER_MAP.keys()) | {".txt", ".md"}
    already_ingested = get_ingested_files()

    for path in Path(directory).rglob("*"):
        if path.suffix.lower() not in supported_exts:
            continue
        if str(path) in already_ingested:
            print(f"  Skipping already ingested: {path.name}")
            continue

        print(f" Loading: {path.name}")
        docs = load_file(str(path))
        if docs:
            all_docs.extend(docs)
            mark_as_ingested(str(path))  # record it

    print(f"\n Loaded {len(all_docs)} new document pages from {directory}")

    return all_docs