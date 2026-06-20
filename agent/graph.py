from langgraph.graph import StateGraph, END
from agent.state import ReviewState
from agent.router import route_after_fetch
from agent.nodes.fetch_diff import fetch_diff

def build_graph():
    g = StateGraph(ReviewState)

    # register nodes
    g.add_node("fetch_diff", fetch_diff)
    g.add_node("classify", classify)
    g.add_node("review_logic", review_logic)
    g.add_node("review_security", review_security)
    g.add_node("review_style", review_style)
    g.add_node("aggregate", aggregate)
    g.add_node("post_comment", post_comment)

    # entry point
    g.set_entry_point("fetch_diff")

    # conditional edge after fetch_diff
    g.add_conditional_edges("fetch_diff", route_after_fetch)

    # fan-out from classify
    g.add_edge("classify", "review_logic")
    g.add_edge("classify", "review_security")
    g.add_edge("classify", "review_style")

    # fan-in to aggregate
    g.add_edge(["review_logic", "review_security", "review_style"], "aggregate")

    # finish line
    g.add_edge("aggregate", "post_comment")
    g.add_edge("post_comment", END)

    return g.compile()