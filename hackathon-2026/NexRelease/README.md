# ⚡ NexRelease: MCP-Powered AI Release Coordinator

## 📋 Project Submission

| Field | Details |
|---|---|
| **Project Name** | NexRelease |
| **Team Name** | Team Schrodingers |
| **Team Members** | Prateek Manocha · Krish Bhandari · Niraj Basel · Dhanush Rajakumar |
| **Track** | MCP Workflow AI — Gen-AI Hackathon 2026 |

---

## 🚀 Project Overview

Modern software teams waste significant time on repetitive release coordination tasks — manually filing Jira tickets, posting Slack notifications, scheduling go/no-go meetings, and reviewing contributor access after every merged PR.

**NexRelease** solves this by deploying an MCP-based AI agent that triggers automatically the moment a PR is merged on GitHub. Within 10 seconds, it:

- Reads and summarizes the PR using **Groq AI** (LLaMA 3.3-70b)
- Creates a structured **Jira ticket** with summary, acceptance checklist, and risk analysis
- Posts a formatted release note to **Slack #releases**
- Schedules a **go/no-go meeting** — timing determined by AI-assessed risk level (HIGH = same day, MEDIUM = next working day, LOW = 2 days out)
- Performs a **security check** against a contributor whitelist — unauthorized contributors are flagged, all Jira/Slack/Calendar actions are blocked, and the repo owner is alerted for one-click approval

The entire workflow is orchestrated via **MCP (Model Context Protocol)** agents, with a polished dark-themed Flask dashboard for real-time monitoring, per-user notification feeds, and manual control.

---

## 🏗️ Architecture

### Inference
**Groq AI** (llama-3.3-70b-versatile) powers `claude_brain.py`. It receives raw PR data and returns 6 structured fields in a single prompt call: plain English summary, Jira ticket title, acceptance criteria checklist, risk analysis, Slack message, and meeting title.

### Data Pipeline
```
GitHub PR Event (merge or open)
       │
       ▼
  app.py /webhook  ──── receives GitHub webhook POST
       │
       ▼
  github_tool.py   ──── fetches PR title, body, author, CI status via GitHub REST API
       │
       ▼
  claude_brain.py  ──── Groq AI summarizes PR → 6 structured output fields
       │
       ├──► jira_tool.py      ──── creates Jira ticket (deduplication via PR ID cache)
       ├──► slack_tool.py     ──── posts formatted message to #releases channel
       └──► calendar_tool.py  ──── schedules go/no-go meeting (risk-based timing)
                │
                ▼
         notification stored in user_notifications/<username>.json
                │
                ▼
         live feed updates via 5-second polling
```

### Security Layer
Every PR author is checked against `whitelist.json` before any tools run. Unauthorized contributors create a `pending=True` notification — Jira, Slack, and Calendar are completely blocked until the repo owner explicitly approves via the dashboard security alert modal or the detail drawer. Approval can also auto-whitelist the contributor for future PRs.

### Deduplication
`jira_tool.py` caches every created ticket by PR number in `processed_prs.json`. Before creating any ticket, it checks this cache first — preventing duplicate ticket spam when the agent runs multiple times on the same PR.

### Frontend
- **Flask** serves the single-page dashboard at `/app`
- Dark-themed UI with animated pipeline visualizer, terminal-style agent log, step-by-step result cards
- **GitHub OAuth 2.0** authentication — repo owner is auto-whitelisted on login
- **Live PR feed** on the right panel — polls every 5 seconds, shows per-user notifications
- **Security Alert Modal** — pops immediately on unauthorized contributor detection with Approve / Whitelist / View Details actions
- **Detail Panel** — slide-in drawer showing full AI summary, checklist, risks, Jira link, Slack message, and meeting info per PR
- **Repo dropdown** — auto-loads all user repos and their merged PRs after GitHub OAuth login
- Responsive layout with mobile support

---

## 📹 Demo

> 🎬https://www.loom.com/share/643f50dec02643ccbbcf88594a110603

**What to show in the demo:**
1. Login via GitHub OAuth — auto-whitelisting and repo loading
2. Setup screen — connect Jira + Slack credentials
3. Manual trigger — select repo, select PR, watch terminal animate through all 5 steps
4. Show real Jira ticket created and Slack message posted
5. Webhook auto-trigger — merge a PR on GitHub, watch live feed update automatically
6. Security alert — PR from non-whitelisted account triggers modal, show approval flow
7. Google Calendar — show auto-created meeting event in calendar

---

## ✅ Pre-Submission Checklist

- [x] **Code Runs:** All modules execute without error
- [x] **Dependencies:** All external libraries listed in `requirements.txt`
- [x] **Environment:** `.env.example` provided with all required key names
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
JIRA_DOMAIN=yourname.atlassian.net
JIRA_EMAIL=you@company.com
JIRA_API_TOKEN=...
JIRA_PROJECT_KEY=KAN

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_CHANNEL=releases

# Google Calendar (optional — falls back to pre-fill link if not connected)
GOOGLE_CREDENTIALS_JSON=credentials.json

# Flask
SECRET_KEY=your-secret-key
```

### 4. Run the app
```bash
python app.py
```

Open `http://localhost:5000` in your browser.

### 5. Set up GitHub webhook (for auto-trigger)
```bash
# Start ngrok in a second terminal
ngrok http 5000
# Copy the HTTPS URL shown
```

In your GitHub repo → Settings → Webhooks → Add webhook:
- **Payload URL:** `https://<your-ngrok-url>/webhook`
- **Content type:** `application/json`
- **Events:** Pull requests only
- **Active:** checked

Now every PR merge fires the agent automatically — no button clicking needed.

### 6. Connect Google Calendar (optional)
- Go to `http://localhost:5000/app`
- Scroll to the Google Calendar panel
- Click **Connect Google Calendar**
- Authorize via Google OAuth
- Meeting events will now be created automatically in your calendar

---

## 📁 Project Structure

```
nexrelease/
├── app.py                  # Flask app — all routes, GitHub OAuth, session management
├── agent.py                # MCP orchestrator — registers tools, runs agentic loop
├── github_tool.py          # GitHub REST API — fetch PR metadata, CI status
├── claude_brain.py         # Groq AI — PR summarization, whitelist check
├── jira_tool.py            # Jira REST API — create tickets with deduplication
├── slack_tool.py           # Slack API — post release messages
├── calendar_tool.py        # Google Calendar API — schedule risk-based meetings
├── run_agent.py            # Terminal pipeline runner for testing
├── whitelist.json          # Approved contributor usernames (auto-created)
├── user_profiles.json      # Per-user Jira/Slack config (auto-created)
├── processed_prs.json      # Jira deduplication cache (auto-created)
├── user_notifications/     # Per-user PR notification feeds (auto-created)
├── screenshots/            # Demo screenshots
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔑 Key Features

| Feature | Description |
|---|---|
| **Auto PR Summarization** | Groq AI reads PR title, body, and CI status — outputs 6 structured fields |
| **Risk-Based Meeting Scheduling** | HIGH risk = same day, MEDIUM = next working day, LOW = 2 days out |
| **Jira Deduplication** | PR ID cache prevents duplicate tickets on repeated agent runs |
| **Security Whitelist** | Unauthorized contributors blocked, held for owner approval |
| **Pending Approval Flow** | One-click approve / whitelist from alert modal or detail drawer |
| **Per-user Notification Feeds** | Each GitHub user sees only their own PR notifications |
| **GitHub OAuth Login** | Secure authentication — repo owner auto-whitelisted on login |
| **Webhook Auto-trigger** | Fires on both PR open (security check) and PR merge (full pipeline) |
| **Google Calendar Integration** | Real OAuth — meeting events created automatically in your calendar |
| **Live Dashboard** | 5s polling, animated pipeline, terminal log, slide-in detail drawer |
| **Repo & PR Dropdown** | Auto-loads all user repos and merged PRs after login |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| AI / LLM | Groq API — LLaMA 3.3-70b-versatile |
| Backend | Python 3.11 · Flask 3.1 |
| Auth | GitHub OAuth 2.0 · Google OAuth 2.0 |
| Integrations | GitHub REST API · Jira REST API v3 · Slack Web API · Google Calendar API |
| Agent Protocol | MCP (Model Context Protocol) |
| Frontend | Vanilla JS · CSS custom properties · Google Fonts (Outfit + DM Mono) |
| Storage | JSON file store — notifications, whitelist, profiles, deduplication cache |
| Tunnel | ngrok (local dev) / Railway (production) |

---

*Built with ❤️ by Team Schrodingers at Gen-AI Hackathon 2026*