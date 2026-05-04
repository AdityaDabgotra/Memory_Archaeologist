from dotenv import load_dotenv
load_dotenv()

from ingestion.loaders import load_directory
from ingestion.chunker import chunk_documents
from storage.vector_store import build_vector_store, similarity_search
from ingestion.graph_builder import build_graph
from storage.graph_store import MemoryGraphStore
from ingestion.loaders import load_directory
from ingestion.chunker import chunk_documents
from storage.vector_store import build_vector_store
from ingestion.graph_builder import build_graph
from agents.graph_pipeline import ask


def ingest(directory: str = "data/sample"):
    print(f"\n{'='*50}")
    print("Memory Archaeologist — Full Pipeline")
    print(f"{'='*50}\n")

    # Phase 2: Load and chunk
    docs   = load_directory(directory)
    chunks = chunk_documents(docs)
    chunks = list(chunks)
    print(f"Confirmed chunk count before pipeline: {len(chunks)}")

    # Phase 2: Vector store
    build_vector_store(chunks)

    # Phase 3: Knowledge graph
    build_graph(chunks)

    # Test the graph
    print("\nTesting graph queries...")
    graph = MemoryGraphStore()

    print("\nConcept timeline: 'startup'")
    timeline = graph.get_concept_timeline("startup")
    for entry in timeline:
        print(f"  [{entry['date']}] {entry['file']}")
        print(f"   {entry['content'][:100]}...")

    print("\n Person timeline: 'Arjun'")
    person = graph.get_person_timeline("Arjun")
    for entry in person:
        print(f"  [{entry['date']}] {entry['file']}")

    print("\nAll concepts in graph:")
    concepts = graph.get_all_concepts()
    for c in concepts:
        print(f"  - {c['concept']} (appears {c['frequency']}x)")

    graph.close()
    print("\nPhase 3 complete! Ready for agents.")

def debug_chunks():
    from ingestion.loaders import load_directory
    from ingestion.chunker import chunk_documents

    docs   = load_directory("data/sample")
    chunks = chunk_documents(docs)

    print(f"\nTotal chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ---")
        print(f"  File: {chunk.metadata.get('filename')}")
        print(f"  Date: {chunk.metadata.get('date')}")
        print(f"  Length: {len(chunk.page_content)}")
        print(f"  Preview: {chunk.page_content[:60]}")


def ingest(directory: str = "data/sample"):
    docs   = load_directory(directory)
    chunks = list(chunk_documents(docs))
    build_vector_store(chunks)
    build_graph(chunks)


def chat():
    print("\n🏺 Memory Archaeologist — Agent System")
    print("Type 'quit' to exit\n")

    test_queries = [
        "What was I thinking about starting a business?",
        "How did my startup idea evolve over time?",
        "Have I ever contradicted myself about my career?",
        "What ideas did I mention but never follow up on?",
    ]

    for query in test_queries:
        answer = ask(query)
        print(f"\n💬 Answer:\n{answer}")
        print("\n" + "—"*50)



if __name__ == "__main__":
    # debug_chunks()
    # ingest()
    chat()