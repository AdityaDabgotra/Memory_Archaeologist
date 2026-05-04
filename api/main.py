from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.graph_pipeline import ask
from storage.graph_store import MemoryGraphStore
from ingestion.loaders import load_directory
from ingestion.chunker import chunk_documents
from storage.vector_store import build_vector_store
from ingestion.graph_builder import build_graph
from dotenv import load_dotenv
import asyncio
import json
import os

load_dotenv()

app = FastAPI(
    title="Memory Archaeologist API",
    description="Excavate your past thoughts and ideas using AI",
    version="1.0.0"
)

#middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request and Response Model

class QueryRequest(BaseModel):
    query:str

class QueryResponse(BaseModel):
    query:str
    intent: str
    answer:str

class IngestRequest(BaseModel):
    directory: str = "data/sample"

class ConceptTimelineRequest(BaseModel):
    concept: str

class PersonTimelineRequest(BaseModel):
    person: str


# Routes

@app.get("/")
def root():
    return {
        "name":    "Memory Archaeologist",
        "status":  "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    
    try:
        graph = MemoryGraphStore()
        concepts = graph.get_all_concepts()
        graph.close()
        return {
            "status":         "healthy",
            "concepts_in_db": len(concepts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query",response_model=QueryResponse)
def query_memories(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        from agents.graph_pipeline import build_agent_pipeline
        from agents.state import AgentState

        pipeline = build_agent_pipeline()

        initial_state: AgentState = {
            "query":           request.query,
            "intent":          "",
            "vector_results":  [],
            "graph_results":   [],
            "timeline":        [],
            "contradictions":  [],
            "abandoned_ideas": [],
            "final_answer":    "",
            "reasoning":       "",
        }

        result = pipeline.invoke(initial_state)
        return QueryResponse(
            query=request.query,
            intent=result["intent"],
            answer=result["final_answer"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

