from agent.state import ReviewState
from langgraph.graph import END

def route_after_fetch(state: ReviewState) -> str:
    if state.get("error"):
        return END
    return "classify"