from agent.state import ReviewState

def fetch_diff(state: ReviewState) -> dict:
    pr_url = state["pr_url"]
    try:
        diff = call_github_api(pr_url)
        return { "raw_diff": diff }
    except Exception as e:
        return { "error": str(e) }