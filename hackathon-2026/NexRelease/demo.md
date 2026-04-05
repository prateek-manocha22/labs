# Demo Guide

This document provides a step-by-step walkthrough of how to run and verify NexRelease — an MCP-based AI Release Coordinator that automates Jira tickets, Slack notifications, and meeting scheduling when a PR is merged.

---

## ⚙️ Setup Steps

1. Clone the repository
```bash
git clone https://github.com/prateek-manocha22/hackathon-agent.git
cd hackathon-agent
```

2. Install all dependencies
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root folder with your credentials
```
GITHUB_TOKEN=your_github_personal_access_token
GROQ_API_KEY=your_groq_api_key
JIRA_DOMAIN=your-domain.atlassian.net
JIRA_EMAIL=your-email@gmail.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=KAN
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
GITHUB_CLIENT_ID=your_github_oauth_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_client_secret
SECRET_KEY=any-random-long-string
```

4. Set up your GitHub OAuth App
   - Go to `github.com` → Settings → Developer settings → OAuth Apps → New OAuth App
   - Homepage URL: `http://localhost:5000`
   - Callback URL: `http://localhost:5000/oauth/callback`
   - Copy the Client ID and Client Secret into your `.env`

5. Start the Flask server
```bash
python app.py
```

6. Open your browser at `http://localhost:5000`

7. Sign in with your GitHub account via OAuth

8. Connect your Jira email and Slack bot token on the setup page

---

## 🏃 Run Commands

```bash
# Run the full agent pipeline from terminal (no UI)
python agent.py

# Run the web UI with full dashboard
python app.py

# Run the standalone demo script
python Demo.py
```

---

## 📥 Sample Input

The agent reads from a merged GitHub Pull Request. The sample PR used in this demo:

```
Repository:  prateek-manocha22/demo-app
PR Number:   1
PR Title:    feat: integrate Stripe payment gateway
Branch:      feature/stripe-payments → main
Author:      prateek-manocha22

PR Description:
  Integrates Stripe as our payment gateway. Users can now initiate
  payments, confirm status, and request refunds via REST API.
  Webhook handler added to process async Stripe events securely.

Changes:
  - payments.py: create_payment_intent(), confirm_payment(), create_refund()
  - webhook_handler.py: verifies Stripe signatures, handles 3 event types
  - app.py: 4 new routes added

Risks:
  - Stripe keys must be set as environment variables before deploying
  - Refund route has no auth guard — follow-up ticket needed

CI Status: no CI configured
```

---

## 📤 Expected Output

When the agent runs on the above PR, it produces the following outputs automatically:

### Jira Ticket Created
```
Title:       Integrate Stripe Payment Gateway
Project:     KAN
Priority:    High
Status:      To Do
Description: AI-generated summary with acceptance criteria checklist and risk analysis
URL:         https://your-domain.atlassian.net/browse/KAN-1
```

### Slack Message Posted to #releases
```
New Release — feat: integrate Stripe payment gateway
Author: prateek-manocha22
CI Status: no CI configured

This PR integrates Stripe as the payment gateway, allowing users to
initiate payments, confirm status, and request refunds via REST API.

Jira: https://your-domain.atlassian.net/browse/KAN-1
PR:   https://github.com/prateek-manocha22/demo-app/pull/1
```

### Go/No-Go Meeting Scheduled
```
Title: Go/No-Go Meeting for Stripe Payment Gateway Release
Time:  Tomorrow 02:30 PM
Risk:  HIGH — same day meeting triggered by security risk in PR
```

### Terminal Output (agent.py)
```
==================================================
RELEASE AGENT STARTED
==================================================
Step 1: Reading PR from GitHub...
  Title:     feat: integrate Stripe payment gateway
  Author:    prateek-manocha22
  CI Status: no CI configured

Step 2: Summarizing with Groq AI...
  Summary:   This pull request integrates Stripe as the payment gateway...

Step 3: Creating Jira ticket...
  Ticket: https://your-domain.atlassian.net/browse/KAN-1

Step 4: Posting to Slack...
  Slack: posted successfully

Step 5: Scheduling go/no-go meeting...
  Meeting: Go/No-Go Meeting for Stripe Payment Gateway Release
  Time:    2026-04-06 02:30 PM
==================================================
AGENT COMPLETE
==================================================
```

---

## 🔗 Webhook Auto-Trigger (optional)

To make the agent fire automatically on every PR merge without any manual input:

1. Run ngrok to expose your local server
```bash
ngrok http 5000
```

2. Copy the public URL shown by ngrok (e.g. `https://abc123.ngrok-free.app`)

3. Go to your GitHub repo → Settings → Webhooks → Add webhook
```
Payload URL:  https://abc123.ngrok-free.app/webhook
Content type: application/json
Events:       Pull requests only
```

4. Merge any PR — the agent fires automatically with zero manual input

---

## 👥 Team

**Team Schrodingers** — Gen-AI Hackathon 2026
