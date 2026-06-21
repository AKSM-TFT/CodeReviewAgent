from agent.state import ReviewState
from dotenv import load_dotenv
import os
import httpx

GITHUB_API = "https://api.github.com"
load_dotenv()

def _call_github_api(pr_url: str, token: str) -> str:    
    _, _, _, owner, repo, _, number = pr_url.split("/")

    response = httpx.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{number}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff", 
        }
    )
    response.raise_for_status()
    return response.text

def fetch_diff(state: ReviewState) -> dict:
    pr_url = state["pr_url"]
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        return {"error": "GITHUB_TOKEN not set"}

    try:
        diff = _call_github_api(pr_url, token)
        return {"raw_diff": diff}
    except httpx.HTTPStatusError as e:
        return {"error": f"{e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}