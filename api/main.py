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
from fastapi import UploadFile, File
import shutil
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

@app.post("/ingest")
def ingest_document(request: IngestRequest):

    if not os.path.exists(request.directory):
        raise HTTPException(
            status_code=404,
            detail=f"Directory not found: {request.directory}"
        )
    
    try:
        docs   = load_directory(request.directory)
        chunks = list(chunk_documents(docs))
        build_vector_store(chunks)
        build_graph(chunks)

        return {
            "status":       "success",
            "documents":    len(docs),
            "chunks":       len(chunks),
            "directory":    request.directory,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/concepts")
def get_all_concepts():
    """Return all concepts in the knowledge graph with frequencies."""
    try:
        graph    = MemoryGraphStore()
        concepts = graph.get_all_concepts()
        graph.close()
        return {"concepts": concepts, "total": len(concepts)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/concepts/timeline")
def concept_timeline(request: ConceptTimelineRequest):
    """Trace how a concept evolved across all your documents."""
    try:
        graph    = MemoryGraphStore()
        timeline = graph.get_concept_timeline(request.concept)
        graph.close()
        return {
            "concept":  request.concept,
            "timeline": timeline,
            "entries":  len(timeline)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/people/timeline")
def person_timeline(request: PersonTimelineRequest):
    """Find all entries mentioning a specific person."""
    try:
        graph    = MemoryGraphStore()
        timeline = graph.get_person_timeline(request.person)
        graph.close()
        return {
            "person":   request.person,
            "timeline": timeline,
            "entries":  len(timeline)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
def get_stats():
    """Overview of everything stored in the system."""
    try:
        graph    = MemoryGraphStore()
        concepts = graph.get_all_concepts()
        graph.close()

        from storage.vector_store import load_vector_store
        vs            = load_vector_store()
        vector_count  = vs.index.ntotal

        return {
            "total_concepts":  len(concepts),
            "top_concepts":    concepts[:5],
            "total_vectors":   vector_count,
            "vector_store":    "loaded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_and_ingest(file: UploadFile = File(...)):
    allowed = {".txt", ".md", ".pdf", ".docx"}
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not supported. Use: {allowed}"
        )

    # Save uploaded file to data/uploads/
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, file.filename)

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    print(f" Saved uploaded file: {save_path}")

    # Ingest immediately
    try:
        from ingestion.loaders import load_file
        docs   = load_file(save_path)
        if not docs:
            raise HTTPException(status_code=400, detail="File was empty or could not be parsed")

        chunks = list(chunk_documents(docs))
        build_vector_store(chunks)
        build_graph(chunks)

        return {
            "status":   "ingested",
            "filename": file.filename,
            "chunks":   len(chunks),
            "dates_found": list(set(c.metadata.get("date","unknown") for c in chunks)),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))