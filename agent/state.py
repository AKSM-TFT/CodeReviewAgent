from typing import TypedDict

class ReviewState(TypedDict):
    pr_url: str
    raw_diff: str
    chunks: list        
    categories: list
    security_comments: list
    logic_comments: list
    style_comments: list
    final_comments: list
    error: str | None