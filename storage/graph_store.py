load_dotenv()

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
    
    