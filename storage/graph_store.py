from neo4j import GraphDatabase
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

load_dotenv()

class MemoryGraphStore:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth = (os.getenv("NEO4J_USERNAME"),os.getenv("NEO4J_PASSWORD"))
        )
    
    def close(self):
        self.driver.close()
    
    def clear_all(self):
        with self.driver.session() as session:
           session.run("MATCH (n) DETACH DELETE n")
        print("Graph cleared")
    
    def create_indexes(self):
        with self.driver.session() as session:
            session.run("CREATE INDEX doc_id IF NOT EXISTS FOR (d:Document) ON (d.id)")
            session.run("CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name)")
            session.run("CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name)")
        print("Graph indexes created")
    
    def add_document_node(self,doc: Document,chunk_id:str):
        with self.driver.session() as session:
            session.run("""
                MERGE (d:Document {id: $id})
                SET d.content    = $content,
                    d.source     = $source,
                    d.filename   = $filename,
                    d.date       = $date,
                    d.year       = $year,
                    d.month      = $month,
                    d.source_type = $source_type
            """, {
                "id":          chunk_id,
                "content":     doc.page_content[:500],
                "source":      doc.metadata.get("source", ""),
                "filename":    doc.metadata.get("filename", ""),
                "date":        doc.metadata.get("date", ""),
                "year":        doc.metadata.get("year", ""),
                "month":       doc.metadata.get("month", ""),
                "source_type": doc.metadata.get("source_type", "document"),
            })
    
    def add_concept(self,concept:str,doc_id:str,date:str):
        with self.driver.session() as session:
            session.run("""
                MERGE (c:Concept {name: $concept})
                WITH c
                MATCH (d:Document {id: $doc_id})
                MERGE (d)-[:CONTAINS_IDEA {date: $date}]->(c)
            """, {"concept": concept.lower().strip(),
                  "doc_id": doc_id, "date": date})
    
    def add_person(self,person:str, doc_id:str, date: str):
        with self.driver.session() as session:
            session.run("""
                MERGE (p:Person {name: $person})
                WITH p
                MATCH (d:Document {id: $doc_id})
                MERGE (d)-[:MENTIONS {date: $date}]->(p)
            """, {"person": person.strip(),
                  "doc_id": doc_id, "date": date})
    
    