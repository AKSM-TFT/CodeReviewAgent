from agent.state import ReviewState

def route_after_fetch(state: ReviewState) -> str:
    if state["error"]:
        return "handle_error"
    return "classify"