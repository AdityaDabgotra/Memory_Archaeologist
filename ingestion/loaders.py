from langchain_community.document_loaders import (
    PyMuPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)

from langchain.schema import Document
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


