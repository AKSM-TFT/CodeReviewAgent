from agent.state import ReviewState
from dotenv import load_dotenv
import os
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
load_dotenv(override=True)

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
        logger.info(f"RAW DIFF: {diff[:500]}")
        return {"raw_diff": diff}
    except httpx.HTTPStatusError as e:
        return {"error": f"{e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}