from dotenv import load_dotenv
load_dotenv()

from ingestion.loaders import load_directory
from ingestion.chunker import chunk_documents
from storage.vector_store import build_vector_store, similarity_search

def ingest(directory: str = "data/sample"):
    print(f"\n{'='*50}")
    print("Memory Archaeologist — Ingestion Pipeline")
    print(f"{'='*50}\n")

    # Step 1: Load all files
    docs = load_directory(directory)

    # Step 2: Split into chunks
    chunks = chunk_documents(docs)

    # Step 3: Embed and store
    vector_store = build_vector_store(chunks)

    # Step 4: Quick test search
    print("\n Test search: 'startup idea'")
    results = similarity_search("startup idea", k=2)
    for i, r in enumerate(results):
        print(f"\n[{i+1}] Date: {r.metadata['date']} | Source: {r.metadata['filename']}")
        print(f"    {r.page_content[:150]}...")

    print("\n Ingestion complete! Ready for Phase 3.")

if __name__ == "__main__":
    ingest()