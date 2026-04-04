# 🏗️ NexRelease — System Architecture

## Overview

NexRelease is an MCP-based AI release coordination agent that automatically transforms merged GitHub Pull Requests into structured Jira tasks, Slack notifications, and scheduled meetings — with zero manual effort from the development team.

---

## High-Level Architecture

```
Developer merges PR on GitHub
           ↓
    GitHub Webhook fires
           ↓
    Flask Server (app.py)
           ↓
    ┌──────────────────────────────────────────┐
    │              Agent Pipeline               │
    │                                          │
    │  1. github_tool.py  → Read PR data       │
    │  2. claude_brain.py → Groq AI summarize  │
    │  3. jira_tool.py    → Create ticket      │
    │  4. slack_tool.py   → Post message       │
    │  5. calendar_tool.py→ Schedule meeting   │
    └──────────────────────────────────────────┘
           ↓
    Results returned to UI
```

---

## Component Breakdown

### 1. `github_tool.py` — GitHub Integration
- Connects to GitHub REST API
- Reads PR title, body, author, and CI status
- Uses Personal Access Token for authentication
- Returns structured PR data dict to the agent

### 2. `claude_brain.py` — AI Summarization (Groq)
- Connects to Groq API using `llama-3.3-70b-versatile` model
- Takes raw PR data as input
- Returns 6 structured fields:
  - `summary` — plain English explanation
  - `jira_title` — ticket title
  - `checklist` — acceptance criteria
  - `risks` — open items and blockers
  - `slack_message` — formatted notification
  - `meeting_title` — go/no-go meeting name

### 3. `jira_tool.py` — Jira Integration
- Connects to Jira REST API v3
- Checks for duplicate tickets using JQL query before creating
- Creates task with title, description, checklist, risks, and High priority
- Adds comment after meeting is scheduled
- Updates ticket status to In Progress
- Returns ticket key and URL

### 4. `slack_tool.py` — Slack Integration
- Connects to Slack API using Bot Token
- Posts formatted message to `#releases` channel
- Includes PR title, author, CI status, Jira link
- Returns success or failure status

### 5. `calendar_tool.py` — Meeting Scheduler
- Schedules go/no-go review meeting
- Uses PR risk level to determine meeting urgency
- Returns meeting title and scheduled time

### 6. `agent.py` — MCP Orchestrator
- Implements Model Context Protocol pattern
- Registers all 5 tools for Claude to orchestrate
- Chains tools in correct sequence
- Handles errors at each step gracefully

### 7. `app.py` — Flask Web Interface
- Serves the dark-themed UI at `localhost:5000`
- Exposes `/run` endpoint for manual trigger
- Exposes `/webhook` endpoint for GitHub auto-trigger
- Returns JSON results to the frontend

---

## Data Flow

```
PR Data (GitHub)
      ↓
{
  title:     "feat: integrate Stripe payment gateway"
  body:      "## Summary..."
  ci_status: "no CI configured"
  author:    "prateek-manocha22"
  pr_url:    "https://github.com/.../pull/1"
}
      ↓
Groq AI Processing
      ↓
{
  summary:       "This PR integrates Stripe..."
  jira_title:    "Integrate Stripe Payment Gateway"
  checklist:     "- Verify integration\n- Test refund..."
  risks:         "- Refund route has no auth guard..."
  slack_message: "PR merged: feat: integrate Stripe..."
  meeting_title: "Go/No-Go: Stripe Payment Release"
}
      ↓
Jira Ticket Created → KAN-8
Slack Message Posted → #releases
Meeting Scheduled → 2026-04-05 10:00 AM
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3.1 |
| AI Brain | Groq API (llama-3.3-70b-versatile) |
| Source Control | GitHub REST API v3 |
| Project Tracking | Jira REST API v3 |
| Team Notifications | Slack Bot API |
| Protocol | Model Context Protocol (MCP) |
| Auto-trigger | GitHub Webhooks + ngrok |

---

## MCP Pattern Explanation

Traditional automation scripts hardcode the sequence:

```python
# Traditional — hardcoded sequence
read_pr() → summarize() → create_ticket() → notify()
```

NexRelease uses MCP where the AI decides the sequence:

```python
# MCP Pattern — AI orchestrated
agent.register_tool(get_pr_info)
agent.register_tool(create_jira_ticket)
agent.register_tool(post_slack_message)
agent.register_tool(schedule_meeting)
# Claude decides when and how to call each tool
```

This makes the agent adaptable — it can handle different PR types, skip steps when appropriate, and reason about what actions to take.

---

## Webhook Auto-Trigger Flow

```
GitHub PR merged
      ↓
GitHub sends POST request to:
https://xxxx.ngrok-free.app/webhook
      ↓
Flask /webhook route receives payload
      ↓
Checks: action == "closed" AND merged == true
      ↓
Agent pipeline fires automatically
      ↓
Zero developer intervention required
```

---

## Security Design

- All API keys stored in `.env` file — never committed to GitHub
- `.env.example` provided with placeholder values
- Jira uses Base64 encoded Basic Auth
- Slack uses Bearer token authentication
- GitHub uses Personal Access Token
- `.gitignore` excludes all sensitive files

---

## Why This Architecture Works

- **Modular** — each tool is independent and testable alone
- **Scalable** — new tools can be added without changing existing ones
- **Reliable** — duplicate check in Jira prevents repeated tickets
- **Observable** — live terminal UI shows every step in real time
- **Automated** — webhook trigger means zero manual work after PR merge
