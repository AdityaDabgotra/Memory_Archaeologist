from langchain_core.documents import Document
from storage.graph_store import MemoryGraphStore
from ingestion.entity_extractor import extract_entities
import hashlib
import time


def build_chunk_id(doc: Document, index: int) -> str:
    raw = f"{doc.metadata.get('source', '')}_chunk_{index}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def build_graph(chunks: list[Document]):
    chunks = list(chunks)
    print(f"Graph builder receiving {len(chunks)} chunks")

    graph = MemoryGraphStore()
    graph.create_indexes()

    print(f"\nBuilding knowledge graph from {len(chunks)} chunks...")

    concept_to_docs = {}

    for i, chunk in enumerate(chunks):
        print(f"\n--- Processing chunk {i+1}/{len(chunks)} ---")
        try:
            print(f"    Source: {chunk.metadata.get('filename', 'unknown')}")
            print(f"    Content preview: {chunk.page_content[:80]}")
            chunk_id = build_chunk_id(chunk, i)
            date = chunk.metadata.get("date", "unknown")
            print(f"    Chunk ID: {chunk_id} | Date: {date}")
        except Exception as e:
            print(f"    FAILED at metadata step: {e}")
            continue

        try:
            graph.add_document_node(chunk, chunk_id)
            print(f"    Document node added to Neo4j")
        except Exception as e:
            print(f"    FAILED at add_document_node: {e}")
            continue

        try:
            print(f"  Extracting entities...")
            entities = extract_entities(chunk)
            time.sleep(0.5)
            print(f"    Concepts: {entities.get('concepts', [])}")
            print(f"    People:   {entities.get('people', [])}")
        except Exception as e:
            print(f"    FAILED at entity extraction: {e}")
            entities = {"concepts": [], "people": []}

        try:
            for concept in entities.get("concepts", []):
                if concept.strip():
                    graph.add_concept(concept, chunk_id, date)
                    if concept not in concept_to_docs:
                        concept_to_docs[concept] = []
                    concept_to_docs[concept].append(chunk_id)
            print(f"    Concepts added")
        except Exception as e:
            print(f"    FAILED at add_concept: {e}")

        try:
            for person in entities.get("people", []):
                if person.strip():
                    graph.add_person(person, chunk_id, date)
            print(f"    People added")
        except Exception as e:
            print(f"    FAILED at add_person: {e}")

        print(f"  Chunk {i+1} done")

    # ← these three blocks are OUTSIDE the loop now
    print("\nLinking related documents...")
    for concept, doc_ids in concept_to_docs.items():
        if len(doc_ids) > 1:
            for j in range(len(doc_ids) - 1):
                graph.link_related_documents(doc_ids[j], doc_ids[j+1], concept)
                print(f"  ↔️  Linked docs via concept: '{concept}'")

    graph.close()
    print("\nKnowledge graph built successfully!")
    return concept_to_docs