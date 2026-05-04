from dotenv import load_dotenv
load_dotenv()

from ingestion.loaders import load_directory
from ingestion.chunker import chunk_documents
from storage.vector_store import build_vector_store, similarity_search
from ingestion.graph_builder import build_graph
from storage.graph_store import MemoryGraphStore


def ingest(directory: str = "data/sample"):
    print(f"\n{'='*50}")
    print("🏺 Memory Archaeologist — Full Pipeline")
    print(f"{'='*50}\n")

    # Phase 2: Load and chunk
    docs   = load_directory(directory)
    chunks = chunk_documents(docs)

    # Phase 2: Vector store
    build_vector_store(chunks)

    # Phase 3: Knowledge graph
    build_graph(chunks)

    # Test the graph
    print("\n📊 Testing graph queries...")
    graph = MemoryGraphStore()

    print("\n🔍 Concept timeline: 'startup'")
    timeline = graph.get_concept_timeline("startup")
    for entry in timeline:
        print(f"  [{entry['date']}] {entry['file']}")
        print(f"   {entry['content'][:100]}...")

    print("\n👤 Person timeline: 'Arjun'")
    person = graph.get_person_timeline("Arjun")
    for entry in person:
        print(f"  [{entry['date']}] {entry['file']}")

    print("\n🗺️  All concepts in graph:")
    concepts = graph.get_all_concepts()
    for c in concepts:
        print(f"  - {c['concept']} (appears {c['frequency']}x)")

    graph.close()
    print("\n✅ Phase 3 complete! Ready for agents.")


if __name__ == "__main__":
    ingest()