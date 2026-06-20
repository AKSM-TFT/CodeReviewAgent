from openai import OpenAI
from agent.state import ReviewState
from agent.utils import get_diff

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def _review(diff: str, prompt: str) -> list:
    try:
        response = client.chat.completions.create(
            model="llama3.2",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": diff}
            ]
        )
        raw = response.choices[0].message.content
        return raw.splitlines()
    except Exception as e:
        return []

def security_review(state: ReviewState) -> dict:
    try:
        diff = get_diff(state)
        comments = _review(diff, """You are a security-focused code reviewer. Identify vulnerabilities, auth issues, injection risks, exposed secrets. 
                        Be specific — reference line numbers if possible. Return a plain list of issues, one per line.""")
        return {"security_comments": comments}
    except Exception as e:
        return {"error": str(e), "security_comments": []}
    
def logic_review(state: ReviewState) -> dict:
    try:
        diff = get_diff(state)
        comments = _review(diff, """You are a logic-focused code review. Identify bugs, edge cases, incorrect assumptions, broken flows. 
                        Be specific — reference line numbers if possible. Return a plain list of issues, one per line.""")
        return {"logic_comments": comments}
    except Exception as e:
        return {"error": str(e), "logic_comments": []}