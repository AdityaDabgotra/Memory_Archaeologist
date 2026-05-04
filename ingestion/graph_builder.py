from langchain_core.documents import Document
from storage.graph_store import MemoryGraphStore
from ingestion.entity_extractor import extract_entities
import hashlib

def build_chunk_id(doc: Document,index:int) ->str:
    raw = f"{doc.metadata.get('source', '')}_chunk_{index}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def build_graph(chunks: list[Document]):
    graph = MemoryGraphStore()
    graph.create_indexes()
    graph.clear_all()
    
    print(f"\nBuilding knowledge graph from {len(chunks)} chunks...")

    concept_to_docs = {}

    for i,chunk in enumerate(chunks):
        chunk_id = build_chunk_id(chunk,i)
        date = chunk.metadata.get("date","unknown")

        graph.add_document_node(chunk, chunk_id)

        print(f"Extracting entities from chunk {i+1}/{len(chunks)}...")
        entities = extract_entities(chunk)

        for concept in entities.get("concepts", []):
            if concept.strip():
                graph.add_concept(concept, chunk_id, date)
                if concept not in concept_to_docs:
                    concept_to_docs[concept] = []
                concept_to_docs[concept].append(chunk_id)
        
        for person in entities.get("people", []):
            if person.strip():
                graph.add_person(person, chunk_id, date)
        
        print("\n🔗 Linking related documents...")
        for concept, doc_ids in concept_to_docs.items():
            if len(doc_ids) > 1:
                for j in range(len(doc_ids) - 1):
                    graph.link_related_documents(doc_ids[j], doc_ids[j+1], concept)
                    print(f"  ↔️  Linked docs via concept: '{concept}'")

        graph.close()
        print("\nKnowledge graph built successfully!")
        return concept_to_docs