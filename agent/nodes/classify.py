from openai import OpenAI
from agent.state import ReviewState
from agent.utils import get_diff
import json, re

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def classify(state: ReviewState) -> dict:
    diff = get_diff(state)
    try:
        response = client.chat.completions.create(
            model="llama3.2",
            messages=[
                {"role": "system", 
                 "content": """You are a code review classifier. Given a PR diff, identify which review categories apply 
                 Respond ONLY with a JSON array containing any of: "security", "logic", "style", "performance" Example: ["security", "logic"]"""},
                {"role": "user", "content": diff}
            ]
        )

        raw = response.choices[0].message.content
        match = re.search(r'\[.*?\]', raw, re.DOTALL)
        categories = json.loads(match.group()) if match else []

        return {"categories": categories}

    except Exception as e:
        return {"error": str(e), "categories": []}