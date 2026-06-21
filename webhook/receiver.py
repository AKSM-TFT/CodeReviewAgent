from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from agent.graph import graph
import hmac, hashlib, os
from dotenv import load_dotenv
import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

app = FastAPI()

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

print(f"TOKEN LENGTH: {len(os.getenv('GITHUB_TOKEN', ''))}")
print(f"TOKEN PREFIX: {os.getenv('GITHUB_TOKEN', '')[:4]}")
    
if not WEBHOOK_SECRET:
    raise RuntimeError("GITHUB_WEBHOOK_SECRET not set")

# def _verify_signature(payload: bytes, signature: str) -> bool:
#     expected = "sha256=" + hmac.new(
#         WEBHOOK_SECRET.encode(),
#         payload,
#         hashlib.sha256  
#     ).hexdigest()

#     print(f"EXPECTED: {expected}")
#     print(f"RECEIVED: {signature}")
    
#     return hmac.compare_digest(expected, signature)

async def run_graph(pr_url: str):
    try:
        logger.info(f"Starting graph for {pr_url}")
        graph.invoke({"pr_url": pr_url})
        logger.info(f"Graph completed for {pr_url}")
    except Exception as e:
        logger.error(f"Graph failed: {e}", exc_info=True)

def _verify_signature(payload: bytes, signature: str) -> bool:
    if os.getenv("SKIP_SIG_VALIDATION") == "true":
        return True
    
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.body() 
    signature = request.headers.get("X-Hub-Signature-256")

    if not signature:
        raise HTTPException(status_code=403, detail="Missing signature")

    if not _verify_signature(payload, signature):  # ✅
        raise HTTPException(status_code=403, detail="Invalid signature")

    data = json.loads(payload)
    
    if data.get("action") not in ["opened", "synchronize"]:
        return {"status": "skipped"}

    pr_url = data["pull_request"]["html_url"]
    
    background_tasks.add_task(run_graph, pr_url)
    return {"status": "ok"}