from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import AgentState
from storage.vector_store import similarity_search
from storage.graph_store import MemoryGraphStore
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model = os.getenv("LLM_MODEL", "gemini-2.5-flash"),
    temperature = 0
)

def archaeologist_agent(state:AgentState) -> AgentState:
    query = state["query"]
    print(f"🏺 Archaeologist searching for: '{query}'")

    # Vector search — semantic similarity
    vector_results = similarity_search(query, k=4)
    print(f"  Found {len(vector_results)} vector results")

    # Graph search — concept and person mentions
    graph = MemoryGraphStore()
    graph_results = []

    keywords_prompt = f"""Extract 1-3 key concepts or person names from this query.
Return ONLY a comma-separated list, nothing else.
Query: "{query}" """

    keywords_response = llm.invoke(keywords_prompt)
    keywords = [k.strip().lower() for k in
                keywords_response.content.split(",")]
    
    for keyword in keywords:
        concept_hits = graph.get_concept_timeline(keyword)
        person_hits  = graph.get_person_timeline(keyword)
        graph_results.extend(concept_hits)
        graph_results.extend(person_hits)
    
    graph.close()
    print(f"  Found {len(graph_results)} graph results")

    # Format context for synthesis
    context_parts = []
    for r in vector_results:
        context_parts.append(
            f"[{r.metadata.get('date', '?')}] "
            f"({r.metadata.get('source_type', 'doc')}) "
            f"{r.page_content}"
        )
    for r in graph_results:
        context_parts.append(
            f"[{r.get('date', '?')}] "
            f"({r.get('type', 'doc')}) "
            f"{r.get('content', '')}"
        )
    
    context = "\n\n".join(context_parts[:6])

    synthesis_prompt = f"""You are a personal memory assistant helping someone 
excavate their past thoughts and ideas.

User asked: "{query}"

Relevant memories found:
{context}

Provide a thoughtful, insightful response that:
- Directly answers the question
- References specific dates and sources
- Connects related ideas across time
- Feels like a wise friend helping them remember, not a search engine
"""

    response = llm.invoke(synthesis_prompt)
    print(f"  Archaeologist done")

    return {
        **state,
        "vector_results": [r.page_content for r in vector_results],
        "graph_results":  graph_results,
        "final_answer":   response.content,
    }