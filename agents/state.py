from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    query: str                            
    intent: str                      
    vector_results: list             
    graph_results: list                
    timeline: list                 
    contradictions: list             
    abandoned_ideas: list            
    final_answer: str             
    reasoning: str 