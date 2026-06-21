from langgraph.graph import StateGraph, END
from agent.state import ReviewState
from agent.router import route_after_fetch
from agent.nodes.fetch_diff import fetch_diff
from agent.nodes.classify import classify
from agent.nodes.reviewers import security_review, logic_review
from agent.nodes.aggregate import aggregate
from agent.nodes.post_comment import post_comment

def build_graph():
    g = StateGraph(ReviewState)

    # register nodes
    g.add_node("fetch_diff", fetch_diff)
    g.add_node("classify", classify)
    g.add_node("review_security", security_review)
    g.add_node("review_logic", logic_review)
    # g.add_node("review_style", review_style)
    g.add_node("aggregate", aggregate)
    g.add_node("post_comment", post_comment)


    # entry point
    g.set_entry_point("fetch_diff")

    # conditional edge after fetch_diff
    g.add_conditional_edges("fetch_diff", route_after_fetch)

    # fan-out from classify
    g.add_edge("classify", "review_logic")
    g.add_edge("classify", "review_security")
    # g.add_edge("classify", "review_style")

    # fan-in to aggregate
    # g.add_edge(["review_logic", "review_security", "review_style"], "aggregate")
    g.add_edge(["review_logic", "review_security"], "aggregate")

    # finish line
    g.add_edge("aggregate", "post_comment")
    g.add_edge("post_comment", END)

    return g.compile()

graph = build_graph()