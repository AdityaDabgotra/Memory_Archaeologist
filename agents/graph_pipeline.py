from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.router import router_agent
from agents.archaeologist import archaeologist_agent
from agents.timeline_agent import timeline_agent
from agents.contrast_agent import contrast_agent
from agents.regret_miner import regret_miner


def route_to_agent(state: AgentState) ->str:
    intent_map = {
        "archaeologist": "archaeologist",
        "timeline":      "timeline",
        "contrast":      "contrast",
        "regret_miner":  "regret_miner",
    }
    return intent_map.get(state["intent"], "archaeologist")

def build_agent_pipeline() ->StateGraph:

    workflow = StateGraph(AgentState)

    # Add all nodes
    workflow.add_node("router",        router_agent)
    workflow.add_node("archaeologist", archaeologist_agent)
    workflow.add_node("timeline",      timeline_agent)
    workflow.add_node("contrast",      contrast_agent)
    workflow.add_node("regret_miner",  regret_miner)

    # Entry point
    workflow.set_entry_point("router")

    # Conditional routing based on intent
    workflow.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "archaeologist": "archaeologist",
            "timeline":      "timeline",
            "contrast":      "contrast",
            "regret_miner":  "regret_miner",
        }
    )

    # All agents lead to END
    workflow.add_edge("archaeologist", END)
    workflow.add_edge("timeline",      END)
    workflow.add_edge("contrast",      END)
    workflow.add_edge("regret_miner",  END)

    return workflow.compile()