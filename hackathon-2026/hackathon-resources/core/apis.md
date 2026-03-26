# 🔌 APIs & JSON Handling

## 1. REST APIs
The standard way for your app to talk to other services (GitHub, Slack, etc.).
- **Resources**:
  - [REST API Tutorial](https://restfulapi.net/)
  - [FastAPI Documentation (Python)](https://fastapi.tiangolo.com/)

## 2. Authentication
Most real-world APIs require auth. The 3 common patterns:

| Type | How | Example |
|---|---|---|
| **API Key** | Add `?api_key=...` or `Authorization: Bearer ...` header | OpenAI, OpenWeather |
| **OAuth 2.0** | Multi-step redirect flow — get a token | GitHub, Slack |
| **Personal Access Token (PAT)** | Like an API key but scoped to your account | GitHub, Jira |

```python
# API Key example
headers = {"Authorization": f"Bearer {API_KEY}"}
response = requests.get(url, headers=headers)
```
> **Tip**: Store keys in `.env` files, never hardcode them.

## 3. Rate Limiting & Retries
APIs limit how many requests you can make per minute. Handle it:

```python
import time, requests
from requests.exceptions import HTTPError

def safe_get(url, headers, retries=3):
    for attempt in range(retries):
        r = requests.get(url, headers=headers)
        if r.status_code == 429:  # Too Many Requests
            time.sleep(2 ** attempt)  # exponential backoff
            continue
        r.raise_for_status()
        return r.json()
    raise Exception("Max retries exceeded")
```

## 4. JSON Parsing
LLMs often output JSON — validate it before using it:

```python
import json

raw = '{"name": "TrafficBot", "score": 92}'
data = json.loads(raw)  # fails loudly if malformed — always wrap in try/except
```

- **Resources**:
  - [Parsing JSON in Python (Real Python)](https://realpython.com/python-json/)
  - [Python-dotenv for .env files](https://pypi.org/project/python-dotenv/)

## 5. Webhooks
How services push real-time events to your app (e.g., GitHub PR opened → trigger your agent).
- **Resources**:
  - [What are Webhooks? (Zapier)](https://zapier.com/blog/what-are-webhooks/)
