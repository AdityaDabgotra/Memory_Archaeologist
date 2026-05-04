from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import AgentState
from storage.vector_store import similarity_search
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model = os.getenv("LLM_MODEL", "gemini-2.5-flash"),
    temperature = 0.3
)


def contrast_agent(state:AgentState) ->AgentState:
    query = state["query"]
    print(f"Contrast Agent Processing: {query}")

    results = similarity_search(query,k=6)

    entries = "\n\n".join([
        f"[{r.metadata.get('date', '?')}] {r.page_content}"
        for r in results
    ])

    contrast_prompt = f"""You are analyzing someone's personal writings to find 
contradictions, changed opinions, or evolved perspectives.

User query: "{query}"

Their writings over time:
{entries}

Identify:
1. Any direct contradictions between entries
2. Opinions or beliefs that changed significantly
3. What might have caused the shift

Be specific about dates and be empathetic — changing your mind is growth,
not failure.
"""
    response = llm.invoke(contrast_prompt)
    print(f" Contrast Agent done")

    return{
        **state,
        "contradictions":[r.page_content for r in results],
        "final_answer":   response.content,
    }
