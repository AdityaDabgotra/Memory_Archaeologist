from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from agents.state import AgentState
from storage.graph_store import MemoryGraphStore
from storage.vector_store import similarity_search
from dotenv import load_dotenv
import os

load_dotenv()

model = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation"
)
llm = model = ChatHuggingFace(llm=model,temperature = 0.3)

def timeline_agent(state: AgentState) -> AgentState:
    query = state["query"]
    print(f" Timeline agent processing: '{query}'")

    # Extract the subject to trace
    subject_prompt = f"""What is the main subject (concept, person, or idea) 
the user wants to trace over time?
Return ONLY 1-3 words, nothing else.
Query: "{query}" """
    
    subject = llm.invoke(subject_prompt).content.strip().lower()
    print(f"  Tracing subject: '{subject}'")

    graph = MemoryGraphStore()
    timeline = graph.get_concept_timeline(subject)

    if not timeline:
        timeline = graph.get_person_timeline(subject)
    
    if not timeline:
        # Fall back to vector search ordered by date
        vector_results = similarity_search(query, k=6)
        timeline = sorted([
            {
                "date":    r.metadata.get("date", "unknown"),
                "file":    r.metadata.get("filename", ""),
                "content": r.page_content,
                "type":    r.metadata.get("source_type", "doc"),
            }
            for r in vector_results
        ], key=lambda x: x["date"])
    
    graph.close()

    # Build narrative
    timeline_text = "\n".join([
        f"• {e.get('date', '?')}: {e.get('content', '')[:200]}"
        for e in timeline
    ])

    narrative_prompt = f"""You are helping someone understand how their 
thinking about "{subject}" evolved over time.

Chronological entries:
{timeline_text}

Write a clear narrative (3-5 sentences) that:
- Shows how thinking changed from earliest to latest entry
- Highlights key turning points
- Notes what stayed consistent and what shifted
"""
    narrative = llm.invoke(narrative_prompt).content
    print(f"  Timeline agent done — {len(timeline)} entries found")

    return {
        **state,
        "timeline":     timeline,
        "final_answer": narrative,
    }