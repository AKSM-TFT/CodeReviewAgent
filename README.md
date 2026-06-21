# Code Review Agent

An autonomous code review agent built with LangGraph. When a PR is opened or updated, the agent fetches the diff, classifies the changes, runs specialist reviewers, and posts a structured comment directly on the PR.

---

## How It Works

```
GitHub PR opened/updated
        ↓
  FastAPI webhook receiver
        ↓
  fetch_diff → GitHub REST API
        ↓
  classify → Ollama (llama3.2)
        ↓
  ┌─────────────────────┐
  │ security_review     │  (fan-out)
  │ logic_review        │
  └─────────────────────┘
        ↓
  aggregate comments
        ↓
  post_comment → GitHub PR
```

---

## Stack

| Layer | Tool |
|-------|------|
| Agent orchestration | LangGraph |
| LLM backend | Ollama (llama3.2) — local, free |
| Webhook server | FastAPI + uvicorn |
| GitHub integration | GitHub REST API (httpx) |
| Webhook forwarding (local dev) | Smee.io |
| Config | python-dotenv |

---

## Project Structure

```
CodeReviewAgent/
├── agent/
│   ├── state.py          # ReviewState TypedDict
│   ├── graph.py          # LangGraph graph definition
│   ├── router.py         # Conditional routing logic
│   ├── utils.py          # Shared helpers (get_diff, DIFF_CHAR_LIMIT)
│   └── nodes/
│       ├── fetch_diff.py     # Fetches PR diff from GitHub API
│       ├── classify.py       # Classifies diff into categories
│       ├── reviewers.py      # Security + logic reviewer nodes
│       ├── aggregate.py      # Merges comments into final output
│       └── post_comment.py   # Posts comment to GitHub PR
├── webhook/
│   └── receiver.py       # FastAPI webhook endpoint
├── .env
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running
- `llama3.2` model pulled: `ollama pull llama3.2`
- A GitHub account with a personal access token

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/your-username/CodeReviewAgent.git
cd CodeReviewAgent
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=github_pat_your_token_here
GITHUB_WEBHOOK_SECRET=your_generated_secret_here
SKIP_SIG_VALIDATION=false
```

**GitHub Token** — go to GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens. Required permissions:
- Contents: Read
- Pull requests: Read and write

**Webhook Secret** — generate a random secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Start Ollama

```bash
ollama serve
```

### 4. Start the server

```bash
uvicorn webhook.receiver:app --reload --port 8000
```

---

## Local Development (Webhook Forwarding)

GitHub can't reach `localhost` directly. Use [Smee.io](https://smee.io) to forward webhooks locally:

**1.** Go to [smee.io](https://smee.io) → click "Start a new channel" → copy the URL.

**2.** Start the forwarder:
```bash
npx smee-client --url https://smee.io/your-channel --target http://localhost:8000/webhook
```

**3.** Add the webhook to your GitHub repo:
- Repo → Settings → Webhooks → Add webhook
- Payload URL: your Smee URL
- Content type: `application/json`
- Secret: same value as `GITHUB_WEBHOOK_SECRET` in `.env`
- Events: Pull requests only

> **Note:** Smee.io modifies the raw payload bytes, which breaks HMAC signature validation. For local dev only, set `SKIP_SIG_VALIDATION=true` in `.env`. Never use this in production.

---

## Usage

1. Open a pull request in the repository where you configured the webhook.
2. The agent automatically fetches the diff, classifies it, and posts a review comment.

Example output on a PR with SQL injection vulnerabilities:

```
## 🔒 Security
- SQL injection vulnerability in login(): user input directly interpolated into query string
- Passwords stored in plaintext — should be hashed with bcrypt or argon2
- No input validation on user_id parameter in get_user()

## 🧠 Logic
- Database connection never closed — resource leak on every call
- login() returns all matching rows instead of a single user
- No error handling on db.execute() — unhandled exceptions will crash the caller
```

---

## Known Limitations

- Large PRs are hard-truncated at 8,000 characters — chunking strategy not yet implemented
- Style reviewer not implemented (deferred)
- Duplicate comments posted if webhook is redelivered — no idempotency check yet
- `graph.invoke()` is synchronous internally — slow Ollama responses may time out on large diffs

---

## Roadmap

- [ ] Idempotency — check for existing bot comment before posting
- [ ] Style reviewer node
- [ ] Chunking strategy for large diffs
- [ ] Async graph execution
- [ ] Support for multiple models (swap Ollama for Anthropic/OpenAI)