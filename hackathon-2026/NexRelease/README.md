# ⚡ NexRelease: MCP-Powered AI Release Coordinator

## 📋 Project Submission

| Field | Details |
|---|---|
| **Project Name** | NexRelease |
| **Team Name** | Team Schrodingers |
| **Team Members** | Prateek Manocha · Krish Bhandari · Niraj Basel · Dhanush Rajakumar |
| **Track** | Gen-AI Hackathon 2026 |

---

## 🚀 Project Overview

Modern software teams waste significant time on repetitive release coordination tasks — manually filing Jira tickets, posting Slack notifications, scheduling go/no-go meetings, and reviewing contributor access after every merged PR.

**NexRelease** solves this by deploying an AI agent that triggers automatically when a PR is merged on GitHub. Within 10 seconds, it:

- Reads and summarizes the PR using **Groq AI**
- Creates a structured **Jira ticket** (summary, checklist, risks)
- Posts a release note to **Slack #releases**
- Schedules a **go/no-go meeting** on Google Calendar
- Performs a **security check** against a contributor whitelist — unauthorized contributors are flagged and held for owner approval before any Jira/Slack actions fire

The entire workflow is orchestrated via **MCP (Model Context Protocol)** agents, with a polished dark-themed Flask dashboard for real-time monitoring and manual control.

---

## 🏗️ Architecture

### Inference
- **Groq AI** (LLM backend) powers `claude_brain.py`, which summarizes PR diffs and generates structured outputs: Jira title, description, acceptance checklist, risk assessment, Slack message, and meeting title — all in a single prompt call returning JSON.

### Data Pipeline
```
GitHub PR Event
       │
       ▼
  github_tool.py  ──── fetches PR metadata, diff, CI status via GitHub REST API
       │
       ▼
  claude_brain.py ──── Groq AI summarizes PR → structured JSON output
       │
       ├──► jira_tool.py     ──── creates Jira ticket (deduplication via JQL query)
       ├──► slack_tool.py    ──── posts formatted message to #releases channel
       └──► calendar_tool.py ──── schedules go/no-go meeting on Google Calendar
                │
                ▼
         notifications stored per-user in user_notifications/<username>.json
```

- **Security Layer:** Every PR author is checked against a global whitelist (`whitelist.json`). Unauthorized contributors create a `pending=True` notification — Jira/Slack/Calendar are blocked until the repo owner explicitly approves via the dashboard or security alert modal.
- **Deduplication:** `jira_tool.py` uses a JQL query to check for existing tickets by PR ID before creating a new one, preventing duplicate ticket spam.
- **Per-user Notifications:** Each GitHub user gets their own notification feed scoped to their session.

### Frontend
- **Flask** serves the single-page dashboard at `/app`
- Dark-themed UI with live PR feed (polls every 5 seconds), animated pipeline visualizer, terminal-style agent log, and a step-by-step result breakdown
- **GitHub OAuth** flow for authentication (dev mode available without OAuth credentials)
- **Security Alert Modal** pops on unauthorized contributors with one-click Approve / Add to Whitelist actions
- **Detail Panel** (slide-in drawer) shows full AI summary, checklist, risks, Jira link, Slack message, and meeting info per PR
- Responsive layout: feed on the left, main content on the right

---

## 📹 Demo

> 🎬https://www.loom.com/share/643f50dec02643ccbbcf88594a110603

**What to show in the demo:**
1. Login via GitHub OAuth (or dev mode)
2. Connect Jira + Slack + repo in the setup screen
3. Trigger the agent manually with a PR number — watch the terminal animate through all 5 steps
4. Trigger via GitHub webhook on a real PR merge — observe the live feed update
5. Submit a PR from a non-whitelisted account — show the security alert modal and approval flow

---

## ✅ Pre-Submission Checklist

- [x] **Code Runs:** All modules in the project root execute without error
- [x] **Dependencies:** All external libraries listed in `requirements.txt`
- [x] **Environment:** `.env.example` provided with all required API key names
- [x] **Screenshots:** Visual proof added to `/screenshots` folder
- [x] **Demo Instructions:** README clearly explains how to run the prototype

---

## 🛠️ How to Run Locally

### 1. Clone this repo
```bash
git clone https://github.com/<your-org>/nexrelease.git
cd nexrelease
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your keys to `.env`
```bash
cp .env.example .env
# then fill in your values
```

Required keys in `.env`:

```env
# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_CLIENT_ID=        # optional — only needed for OAuth login
GITHUB_CLIENT_SECRET=    # optional — only needed for OAuth login

# Groq AI
GROQ_API_KEY=gsk_...

# Jira
JIRA_EMAIL=you@company.atlassian.net
JIRA_API_TOKEN=...
JIRA_BASE_URL=https://yourorg.atlassian.net
JIRA_PROJECT_KEY=NEX

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=#releases

# Google Calendar
GOOGLE_CALENDAR_ID=primary
GOOGLE_CREDENTIALS_JSON=credentials.json

# Flask
SECRET_KEY=your-secret-key
```

### 4. Run the app
```bash
python app.py
```

Open `http://localhost:5000` in your browser.

### 5. (Optional) Set up GitHub webhook
In your GitHub repo → Settings → Webhooks → Add webhook:
- **Payload URL:** `https://<your-tunnel>/webhook` (use ngrok for local dev)
- **Content type:** `application/json`
- **Events:** Pull requests

```bash
# Example with ngrok
ngrok http 5000
# Copy the HTTPS URL and paste into GitHub webhook settings
```

---

## 📁 Project Structure

```
nexrelease/
├── app.py               # Flask app — all routes, OAuth, session management
├── github_tool.py       # GitHub REST API — fetch PR metadata, diff, CI status
├── claude_brain.py      # Groq AI — PR summarization, whitelist check
├── jira_tool.py         # Jira REST API — create tickets with JQL deduplication
├── slack_tool.py        # Slack API — post release messages
├── calendar_tool.py     # Google Calendar API — schedule go/no-go meetings
├── whitelist.json       # Approved contributor usernames (auto-created)
├── user_profiles.json   # Per-user Jira/Slack config (auto-created)
├── user_notifications/  # Per-user PR notification feeds (auto-created)
├── requirements.txt
├── .env.example
└── screenshots/
```

---

## 🔑 Key Features

| Feature | Description |
|---|---|
| **Auto PR Summarization** | Groq AI reads PR title, body, diff, and CI status — outputs structured JSON |
| **Jira Deduplication** | JQL check prevents duplicate tickets for the same PR |
| **Security Whitelist** | Unauthorized contributors are blocked and held for owner approval |
| **Pending Approval Flow** | One-click approve / whitelist from dashboard or alert modal |
| **Per-user Feeds** | Each GitHub user sees only their own PR notifications |
| **GitHub OAuth** | Secure login — no passwords stored |
| **Webhook Support** | Auto-triggers on PR open and merge events |
| **Live Dashboard** | Polls every 5s, animated pipeline, terminal log, detail drawer |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| AI / LLM | Groq AI (LLaMA 3) |
| Backend | Python · Flask |
| Auth | GitHub OAuth 2.0 |
| Integrations | GitHub REST API · Jira REST API · Slack Web API · Google Calendar API |
| Agent Protocol | MCP (Model Context Protocol) |
| Frontend | Vanilla JS · CSS custom properties · Google Fonts |
| Storage | JSON file store (notifications, whitelist, profiles) |

---

*Built with ❤️ by Team Schrodingers at Gen-AI Hackathon 2026*
