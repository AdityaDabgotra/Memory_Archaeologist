from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.router import router_agent
from agents.archaeologist import archaeologist_agent
from agents.timeline_agent import timeline_agent
from agents.contrast_agent import contrast_agent
from agents.regret_miner import regret_miner_agent


def route_to_agent(state: AgentState) ->str:
    intent_map = {
        "archaeologist": "archaeologist",
        "timeline":      "timeline",
        "contrast":      "contrast",
        "regret_miner":  "regret_miner",
    }
    return intent_map.get(state["intent"], "archaeologist")

