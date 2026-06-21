from agent.state import ReviewState

def aggregate(state: ReviewState) -> dict:
    sections = []

    security = state.get("security_comments", [])
    logic = state.get("logic_comments", [])

    if security:
        sections.append("## Security\n" + "\n".join(security))

    if logic:
        sections.append("## Logic\n" + "\n".join(logic))

    final = "\n\n".join(sections) if sections else "No issues found."

    return {"final_comments": final }