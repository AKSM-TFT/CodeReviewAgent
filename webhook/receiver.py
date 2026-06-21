from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from agent.graph import graph
import hmac, hashlib, os
from dotenv import load_dotenv
import json

load_dotenv()
app = FastAPI()

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
    
if not WEBHOOK_SECRET:
    raise RuntimeError("GITHUB_WEBHOOK_SECRET not set")

def _verify_signature(payload: bytes, signature: str) -> bool:
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
    
    background_tasks.add_task(graph.invoke, {"pr_url": pr_url})
    return {"status": "ok"}