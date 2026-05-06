<div align="center">

# Memory Archaeologist

**Excavate your past thoughts. Trace how your ideas evolved. Rediscover what you forgot.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-1C3C3C?style=flat-square&logo=chainlink&logoColor=white)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-FF6B35?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-AuraDB-008CC1?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com)

<br/>

> *"Most RAG apps retrieve documents. Memory Archaeologist reconstructs your cognitive history."*

</div>

---

## What Is This?

Memory Archaeologist is an AI-powered personal knowledge system that ingests your **journals, notes, emails, and documents** — then lets you have a conversation with your past self.

Unlike a basic search tool or RAG chatbot, it builds a **living knowledge graph** of your thinking over time. Every chunk of text you have ever written is linked to concepts, people, and ideas — forming a web of thought you can explore, question, and learn from.

```
Your files  ->  Ingestion Pipeline  ->  Vector Store + Knowledge Graph  ->  Multi-Agent System  ->  Chat Interface
```

---

## Features

| Feature | Description |
|---|---|
| Memory Retrieval | Semantic search across all your documents with date-aware context |
| Idea Timeline | Trace how any concept or opinion evolved month by month |
| Contradiction Detector | Find where you changed your mind and what caused the shift |
| Regret Miner | Surface abandoned ideas and forgotten projects worth revisiting |
| Knowledge Graph | Interactive D3.js visualization of your concepts and their connections |
| File Upload | Upload documents directly from the UI, instantly ingested |
| Additive Ingestion | Add new files without wiping existing memory |
| Smart Date Extraction | Infers document dates from filename, content, or LLM fallback |

---

## Architecture

```
+--------------------------------------------------------------+
|                       Frontend (React)                        |
|            Chat Interface        D3.js Knowledge Graph        |
+------------------------------+-------------------------------+
                               | HTTP
+------------------------------v-------------------------------+
|                       FastAPI Backend                         |
|    /query  /ingest  /upload  /concepts  /stats  /reset        |
+------+-------------------------------------------+-----------+
       |                                           |
+------v---------------------------+   +-----------v-----------+
|     LangGraph Agent System       |   |   Ingestion Pipeline   |
|                                  |   |                        |
|   Router  -->  Archaeologist     |   |   Loaders              |
|               Timeline           |   |   Chunker              |
|               Contrast           |   |   Entity Extractor     |
|               Regret Miner       |   |   Graph Builder        |
+----------------------------------+   +-----------+-----------+
                                                   |
                                       +-----------v-----------+
                                       |        Storage         |
                                       |                        |
                                       |   FAISS Vector Store   |
                                       |   Neo4j Knowledge Graph|
                                       +------------------------+
```

### Agent Roster

| Agent | Triggered When | What It Does |
|---|---|---|
| Router | Every query | Classifies intent, routes to specialist |
| Archaeologist | General memory search | Semantic + graph retrieval, synthesizes answer |
| Timeline | "How did X evolve?" | Chronological narrative of idea evolution |
| Contrast | "Have I contradicted myself?" | Finds changed opinions, explains the shift |
| Regret Miner | "What did I abandon?" | Surfaces forgotten ideas with revival plan |

---

## Project Structure

```
memory-archaeologist/
|
+-- ingestion/                  # Document processing pipeline
|   +-- loaders.py              # Multi-format loaders with date inference
|   +-- chunker.py              # Smart text splitter
|   +-- entity_extractor.py     # LLM-powered concept/person extraction
|   +-- graph_builder.py        # Builds Neo4j knowledge graph from chunks
|
+-- storage/                    # Persistence layer
|   +-- vector_store.py         # FAISS vector store (additive)
|   +-- graph_store.py          # Neo4j graph queries and mutations
|
+-- agents/                     # LangGraph multi-agent system
|   +-- state.py                # Shared AgentState schema
|   +-- router.py               # Intent classifier
|   +-- archaeologist.py        # Core retrieval agent
|   +-- timeline_agent.py       # Chronological analysis agent
|   +-- contrast_agent.py       # Contradiction detection agent
|   +-- regret_miner.py         # Abandoned idea recovery agent
|   +-- graph_pipeline.py       # LangGraph workflow builder
|
+-- api/
|   +-- main.py                 # FastAPI backend (9 endpoints)
|
+-- frontend/                   # React application
|   +-- src/
|       +-- App.js
|       +-- api.js
|       +-- components/
|           +-- ChatMessage.jsx
|           +-- KnowledgeGraph.jsx
|           +-- StatsBar.jsx
|
+-- data/
|   +-- sample/                 # Sample documents to get started
|   +-- uploads/                # Files uploaded via UI
|   +-- vector_store/           # FAISS index (auto-generated)
|
+-- .env                        # API keys, never commit this
+-- requirements.txt
+-- main.py                     # CLI entry point
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Hugging Face Access Token
- [Neo4j AuraDB](https://neo4j.com/cloud/aura/) free account

### 1. Clone and install

```bash
git clone https://github.com/AdityaDabgotra/Memory_Archaeologist.git
cd Memory_Archaeologist

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the root:

```env

NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password-here

EMBEDDING_MODEL=text-embedding-3-small

HUGGINGFACEHUB_ACCESS_TOKEN = your-huggingface-token-if-needed
```

### 3. Add your documents

Drop `.txt`, `.md`, `.pdf`, or `.docx` files into `data/sample/`.

Naming files with dates gives the best results:

```
2023-01-10_journal.txt
2024-03-15_meeting-notes.md
```

### 4. Ingest documents

```bash
python main.py
```

### 5. Start the backend

```bash
uvicorn api.main:app --reload --port 8000
```

### 6. Start the frontend

```bash
cd frontend
npm install
npm start
```

Open **http://localhost:3000**

---

## Example Queries

```
"What was I thinking about starting a business?"
  -> Archaeologist agent retrieves and connects relevant memories across time

"How did my views on remote work evolve?"
  -> Timeline agent builds a chronological narrative of your perspective shift

"Have I ever contradicted myself about my career goals?"
  -> Contrast agent finds the tension and explains what changed

"What ideas did I mention but never follow up on?"
  -> Regret Miner surfaces abandoned ideas with a concrete revival plan
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health + Neo4j connectivity |
| `POST` | `/query` | Ask anything, routes to the right agent |
| `POST` | `/ingest` | Ingest documents from a directory |
| `POST` | `/upload` | Upload a single file via multipart form |
| `GET` | `/concepts` | All concepts in the knowledge graph |
| `POST` | `/concepts/timeline` | Trace a concept across time |
| `POST` | `/people/timeline` | Find all entries mentioning a person |
| `GET` | `/stats` | Document count, concept count, vector count |
| `DELETE` | `/reset` | Wipe graph + ingestion log for a fresh start |

Interactive docs available at `http://localhost:8000/docs`

---

## Supported File Types

| Format | Extension |
|---|---|
| Plain text | `.txt` |
| Markdown | `.md` |
| PDF | `.pdf` |
| Word Document | `.docx` |

---

## How Date Inference Works

When a file has no date in its name, the system tries five fallback strategies in order:

```
1. Filename pattern       2023-01-10_journal.txt         most reliable
2. Content regex          "2023-01-10" anywhere in text  fast
3. Natural language       "January 10, 2023" variants    flexible
4. LLM extraction         GPT reads first 300 chars      handles anything
5. File modified time     OS filesystem timestamp        last resort
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI GPT-4o-mini |
| Orchestration | LangChain 0.2 + LangGraph |
| Vector Store | FAISS (local, no server needed) |
| Knowledge Graph | Neo4j AuraDB (free cloud tier) |
| Embeddings | OpenAI text-embedding-3-small |
| Backend | FastAPI + Uvicorn |
| Frontend | React 18 + D3.js |
| File Parsing | PyPDF, python-docx, LangChain loaders |

---

## Resetting the System

```bash
# Clear graph and ingestion log
curl -X DELETE http://localhost:8000/reset

# Delete vector store
rm -rf data/vector_store/        # Mac/Linux
rd /s /q data\vector_store       # Windows

# Re-ingest from scratch
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"directory": "data/sample"}'
```

---

## Roadmap

- [ ] Multi-user support with authentication
- [ ] Gmail, Notion, Obsidian direct connectors
- [ ] Weekly rediscovery digest via email
- [ ] Mood and sentiment tracking over time
- [ ] Mobile app (React Native)
- [ ] Local LLM support via Ollama
- [ ] Export knowledge graph as PNG or SVG

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you would like to change.

```bash
git checkout -b feature/your-feature
git commit -m "feat: describe your change"
git push origin feature/your-feature
```

---

## License

MIT 2024

---

<div align="center">

Built with LangChain · LangGraph · Neo4j · FastAPI · React

**[Star this repo](https://github.com/yourusername/memory-archaeologist)** if it helped you rediscover something worth keeping.

</div>