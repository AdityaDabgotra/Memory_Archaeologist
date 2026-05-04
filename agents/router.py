from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from agents.state import AgentState
from dotenv import load_dotenv
import os

load_dotenv()

model = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation"
)
llm = model = ChatHuggingFace(llm=model,temperature = 0)

def router_agent(state: AgentState) ->AgentState:
    prompt = f"""You are a router for a personal memory system.
Given the user's query, classify their intent into exactly one of these:
- archaeologist  : searching for past thoughts, memories, or ideas
- timeline       : asking how something evolved or changed over time  
- contrast       : looking for contradictions or changed opinions
- regret_miner   : looking for abandoned, forgotten, or dropped ideas

Query: "{state['query']}"

Respond with ONLY the intent word, nothing else."""

    response = llm.invoke(prompt)
    intent = response.content.strip().lower()

    if intent not in ["archaeologist", "timeline", "contrast", "regret_miner"]:
        intent = "archaeologist"

    print(f"Router → intent: {intent}")
    return {**state, "intent": intent}