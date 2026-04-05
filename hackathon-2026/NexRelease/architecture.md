# 🏗️ NexRelease — System Architecture

## Overview

NexRelease is an MCP-based AI release coordination agent that automatically transforms merged GitHub Pull Requests into structured Jira tasks, Slack notifications, and scheduled calendar meetings — with zero manual effort from the development team.

---

## High-Level Architecture

```
Developer merges PR on GitHub
           ↓
    GitHub Webhook fires POST to /webhook
           ↓
    Flask Server (app.py)
           ↓
    Security Check (claude_brain.py)
           ↓
    ┌──────────────────────────────────────────────┐
    │              MCP Agent Pipeline               │
    │                                              │
    │  1. github_tool.py   → Read PR metadata      │
    │  2. claude_brain.py  → Groq AI summarize     │
    │  3. jira_tool.py     → Create Jira ticket    │
    │  4. slack_tool.py    → Post to #releases     │
    │  5. calendar_tool.py → Schedule meeting      │
    └──────────────────────────────────────────────┘
           ↓
    Notification stored per-user
           ↓
    Live feed updates via 5s polling
```

---

## Component Breakdown

### 1. `github_tool.py` — GitHub Integration
- Connects to GitHub REST API using Personal Access Token
- Reads PR title, body, author, and CI check status
- Makes two API calls per PR: one for PR data, one for CI check-runs
- Returns a structured dict: `{title, body, ci_status, author, pr_url}`
- Works for any PR in any repo — no hardcoded values

### 2. `claude_brain.py` — AI Summarization (Groq)
- Connects to Groq API using OpenAI-compatible client
- Model: `llama-3.3-70b-versatile`
- Sends PR title, body, and CI status in a structured prompt
- Returns 6 parsed fields:
  - `summary` — plain English 2-3 sentence explanation
  - `jira_title` — clean ticket title
  - `checklist` — acceptance criteria bullet points
  - `risks` — open items and blockers identified
  - `slack_message` — formatted notification text
  - `meeting_title` — go/no-go meeting name
- Also handles whitelist contributor checking via `check_contributor()`

### 3. `jira_tool.py` — Jira Integration
- Connects to Jira REST API v3 using Base64 Basic Auth
- Checks `processed_prs.json` for existing PR ID before creating — prevents duplicates
- Creates Task with title, description, checklist, risks, and High priority
- Saves PR ID → ticket key mapping to `processed_prs.json` after creation
- Returns ticket key (e.g. `KAN-8`) and full browse URL

### 4. `slack_tool.py` — Slack Integration
- Connects to Slack API using Bot Token (`xoxb-`)
- Posts formatted markdown message to `#releases` channel
- Message includes PR title, author, CI status, AI summary, and Jira link
- Bot must be invited to the channel with `chat:write` scope
- Returns `{success: True/False}`

### 5. `calendar_tool.py` — Meeting Scheduler
- Detects risk level from AI-generated risks text using keyword matching:
  - HIGH: security, auth, payment, vulnerability, no guard → same day meeting
  - MEDIUM: default → next working day
  - LOW: ui, readme, typo, cosmetic → 2 working days later
- Skips weekends using `get_next_weekday()`
- Creates real Google Calendar event via OAuth if `token.pickle` exists
- Falls back to pre-filled Google Calendar URL if not connected
- Returns `{time, day, risk, urgency, cal_link, google_integrated}`

### 6. `agent.py` — MCP Orchestrator
- Implements Model Context Protocol pattern
- Registers all 5 tools with full JSON schema definitions
- `execute_tool()` dispatches calls to real implementations
- `run_agent()` chains all tools in sequence with logging at each step
- Handles errors at each step without crashing the full pipeline

### 7. `app.py` — Flask Web Interface + OAuth
- Serves the dark-themed dashboard at `/app`
- **GitHub OAuth routes:** `/oauth/login`, `/oauth/callback`, `/oauth/logout`
- **Google Calendar OAuth routes:** `/oauth/google`, `/oauth/google/callback`, `/oauth/google/status`
- **Agent routes:** `/run` (manual trigger), `/webhook` (GitHub auto-trigger)
- **Notification routes:** `/notifications`, `/notifications/delete`, `/notifications/clear`
- **Whitelist routes:** `/whitelist`, `/whitelist/add`, `/whitelist/remove`
- **Approval route:** `/approve` — runs full pipeline on a pending unauthorized PR
- Per-user notification files stored in `user_notifications/<username>.json`
- Session management via Flask sessions with secret key

---

## Data Flow — Complete Example

```
Input (from GitHub webhook):
{
  "action": "closed",
  "pull_request": {
    "merged": true,
    "number": 1,
    "title": "feat: integrate Stripe payment gateway",
    "body": "## Summary\nIntegrates Stripe...\n## Risks\n- Refund route has no auth guard",
    "user": {"login": "prateek-manocha22"},
    "head": {"sha": "abc123"}
  },
  "repository": {"full_name": "prateek-manocha22/demo-app"}
}

Step 1 — github_tool.py reads PR:
{
  title:     "feat: integrate Stripe payment gateway",
  body:      "## Summary\nIntegrates Stripe...",
  ci_status: "no CI configured",
  author:    "prateek-manocha22",
  pr_url:    "https://github.com/prateek-manocha22/demo-app/pull/1"
}

Step 2 — claude_brain.py (Groq AI) outputs:
{
  summary:       "This PR integrates Stripe as the payment gateway...",
  jira_title:    "Integrate Stripe Payment Gateway",
  checklist:     "- Verify Stripe integration\n- Test refund flow\n- Check env vars",
  risks:         "- Refund route has no auth guard\n- Stripe keys must be env vars",
  slack_message: "PR merged: feat: integrate Stripe payment gateway...",
  meeting_title: "Go/No-Go: Stripe Payment Gateway Release"
}

Step 3 — jira_tool.py creates:
  Ticket: KAN-8
  URL: https://prateekmanocha22.atlassian.net/browse/KAN-8

Step 4 — slack_tool.py posts to #releases:
  Message with PR title, Jira link, risks summary

Step 5 — calendar_tool.py schedules:
  Risk detected: HIGH (refund route, no auth guard)
  Meeting: same day at 14:30
  Google Calendar event created automatically
```

---

## Security Design

```
PR opened/merged
       ↓
check_contributor(author) in claude_brain.py
       ↓
Load whitelist.json → check if author in list
       ↓
┌─────────────┬──────────────────────────────────┐
│  VERIFIED   │  Run full pipeline immediately    │
├─────────────┼──────────────────────────────────┤
│ UNAUTHORIZED│  Create pending=True notification │
│             │  Block Jira, Slack, Calendar      │
│             │  Fire security alert modal on UI  │
│             │  Wait for owner approval          │
└─────────────┴──────────────────────────────────┘
       ↓ (on approval via /approve route)
Run full pipeline on the pending PR
Update notification with results
```

All API keys stored in `.env` — never committed. `.gitignore` excludes `.env`, `token.pickle`, `credentials.json`, `processed_prs.json`, `whitelist.json`, `user_profiles.json`, and `user_notifications/`.

---

## MCP Pattern Explanation

Traditional automation hardcodes the sequence:

```python
# Traditional — rigid, hardcoded
def run():
    pr = read_pr()
    summary = summarize(pr)
    create_ticket(summary)
    notify_slack(summary)
```

NexRelease uses the MCP pattern where tools are registered and the agent orchestrates them:

```python
# MCP Pattern — tool registration
TOOLS = [
    {"name": "get_pr_info",        "description": "..."},
    {"name": "create_jira_ticket", "description": "..."},
    {"name": "post_slack_message", "description": "..."},
    {"name": "create_calendar_event", "description": "..."},
]

def execute_tool(name, args):
    # dispatcher — routes to real implementations
    ...

def run_agent(user_query):
    # agent decides which tools to call and in what order
    ...
```

This makes the agent adaptable — it can handle any PR type, skip steps when appropriate, and reason about risk level before deciding meeting urgency.

---

## Webhook Auto-Trigger Flow

```
GitHub PR merged
       ↓
GitHub sends POST to:
https://xxxx.ngrok-free.app/webhook
(or Railway URL in production)
       ↓
Flask /webhook receives JSON payload
       ↓
Checks: action == "closed" AND merged == true
       ↓
Extracts: repo, pr_number, author
       ↓
Security check → whitelist verification
       ↓
If authorized: full pipeline fires
If unauthorized: pending notification created
       ↓
Zero developer intervention required
```

---

## Google Calendar OAuth Flow

```
User clicks "Connect Google Calendar" in dashboard
       ↓
/oauth/google → generates auth URL from credentials.json
       ↓
Popup opens → user authorizes via Google
       ↓
/oauth/google/callback → fetches token, saves to token.pickle
       ↓
All future create_calendar_event() calls use real API
       ↓
If token.pickle missing → falls back to pre-fill URL
```

---

## APIs Used

| API | Purpose | Auth Method |
|-----|---------|-------------|
| GitHub REST API v3 | Read PR data, CI status | Personal Access Token |
| GitHub OAuth 2.0 | User login, repo access | OAuth Client ID + Secret |
| Groq API | LLM summarization | API Key |
| Jira REST API v3 | Ticket creation | Base64 Basic Auth |
| Slack Web API | Channel messaging | Bot Token (xoxb-) |
| Google Calendar API | Meeting creation | OAuth 2.0 (token.pickle) |

---

## AI Model Usage

**Model:** `llama-3.3-70b-versatile` via Groq API

**Input:** PR title + body + CI status (raw text from GitHub API)

**Prompt strategy:** Single structured prompt requesting 6 labeled sections. The parser in `claude_brain.py` splits the response by section headers and maps each to a dict key.

**Risk detection:** `calendar_tool.py` scans the `risks` field returned by the AI for keywords like "security", "auth", "payment", "no guard" to classify risk level and determine meeting urgency — no second LLM call needed.

**Output quality:** The richer the PR description written by the developer, the better the AI output. This incentivizes good PR hygiene as a side effect of using NexRelease.

---

*Built with ❤️ by Team Schrodingers at Gen-AI Hackathon 2026*