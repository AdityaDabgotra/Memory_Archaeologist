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
    
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(500)  # read first 500 chars only
        return extract_date_from_content(content)
    except:
        pass
    
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

def extract_date_from_content(content: str) -> str:
    
    import re

    # Try regex on content first
    match = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", content)
    if match:
        return match.group(1).replace("/", "-")

    # Try natural language dates in content
    month_map = {
        "january":"01","february":"02","march":"03","april":"04",
        "may":"05","june":"06","july":"07","august":"08",
        "september":"09","october":"10","november":"11","december":"12",
        "jan":"01","feb":"02","mar":"03","apr":"04","jun":"06",
        "jul":"07","aug":"08","sep":"09","oct":"10","nov":"11","dec":"12",
    }
    pattern = re.search(
        r"(january|february|march|april|may|june|july|august|september|"
        r"october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)"
        r"\s+(\d{1,2}),?\s+(\d{4})",
        content.lower()
    )
    if pattern:
        month = month_map[pattern.group(1)]
        day   = pattern.group(2).zfill(2)
        year  = pattern.group(3)
        return f"{year}-{month}-{day}"

    # LLM fallback for messy formats
    try:
        from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
        from dotenv import load_dotenv
        import os
        load_dotenv()
        model = HuggingFaceEndpoint(
            repo_id="Qwen/Qwen2.5-7B-Instruct",
            task="text-generation"
        )
        llm = model = ChatHuggingFace(llm=model)
        
        response = llm.invoke(
            f"""Extract the date from this document excerpt.
Return ONLY a date in YYYY-MM-DD format. If no date found, return 'unknown'.
Do not explain. Just the date.

Document:
\"\"\"{content[:300]}\"\"\"
"""
        )
        result = response.content.strip()
        if re.match(r"\d{4}-\d{2}-\d{2}", result):
            return result
    except:
        pass

    return datetime.now().strftime("%Y-%m-%d")