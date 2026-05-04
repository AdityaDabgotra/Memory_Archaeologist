from langchain_core.documents import Document
from storage.graph_store import MemoryGraphStore
from ingestion.entity_extractor import extract_entities
import hashlib

def build_chunk_id(doc: Document,index:int) ->str:
    raw = f"{doc.metadata.get('source', '')}_chunk_{index}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]

