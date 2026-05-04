from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from agents.state import AgentState
from storage.vector_store import similarity_search
from storage.graph_store import MemoryGraphStore
from dotenv import load_dotenv
import os

load_dotenv()

model = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation"
)

llm = model = ChatHuggingFace(llm=model,temperature = 0.5)

def regret_miner(state:AgentState) -> AgentState:
    query = state["query"]
    print(f" Regret Miner processing: '{query}'")

    graph = MemoryGraphStore()
    all_concepts = graph.get_all_concepts()
    graph.close()

    # Find concepts that only appear once — likely abandoned ideas
    abandoned = [c for c in all_concepts if c["frequency"] == 1]
    all_memories = similarity_search(query, k=6)

    concepts_text = ", ".join([c["concept"] for c in abandoned[:10]])
    memories_text = "\n\n".join([
        f"[{r.metadata.get('date', '?')}] {r.page_content}"
        for r in all_memories
    ])

    mining_prompt = f"""You are helping someone rediscover ideas they mentioned 
once and never returned to — their forgotten treasures.

Concepts that appeared only once in their writings:
{concepts_text}

Related memories:
{memories_text}

User query: "{query}"

Identify 2-3 ideas that seem promising but were abandoned.
For each one:
- What was the idea?
- When did they mention it?  
- Why might it be worth revisiting now?
- What would be a concrete next step?

Be encouraging and specific.
"""
    
    response = llm.invoke(mining_prompt)
    print(f"   Regret Miner done")

    return {
        **state,
        "abandoned_ideas": abandoned,
        "final_answer":    response.content,
    }
