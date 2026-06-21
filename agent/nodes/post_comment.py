from agent.state import ReviewState
from dotenv import load_dotenv
import os
import httpx

GITHUB_API = "https://api.github.com"
load_dotenv()

def post_comment(state: ReviewState) -> dict:
    pr_url = state["pr_url"]
    body = state["final_comments"]
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        return {"error": "GITHUB_TOKEN not set"}

    _, _, _, owner, repo, _, number = pr_url.split("/")

    try:
        response = httpx.post(
            f"{GITHUB_API}/repos/{owner}/{repo}/issues/{number}/comments",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json"
            },
            json={"body": body}
        )

        response.raise_for_status()
        return {"error": None}
    except httpx.HTTPStatusError as e:
        return {"error": f"{e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}