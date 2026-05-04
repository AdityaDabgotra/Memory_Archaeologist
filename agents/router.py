from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import AgentState
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model = os.getenv("LLM_MODEL", "gemini-2.5-flash"),
    temperature = 0
)

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