"""
PR Release Coordinator — MCP-Based AI Agent
Automates release coordination when a GitHub PR is merged.
Tools: GitHub, Jira, Slack, Calendar
LLM: Groq (llama-3.3-70b-versatile)
"""
import json
import os
from openai import OpenAI
from github_tool import get_pr_info
from jira_tool import create_jira_ticket
from slack_tool import post_slack_message
from calendar_tool import create_calendar_event

# ── Groq client ───────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ── Tool definitions (MCP tools spec) ────────────────────────────────────────
TOOLS = [
    {
        "name": "get_pr_info",
        "description": "Reads a GitHub pull request — returns title, body, CI status, author, and URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo":      {"type": "string",  "description": "Owner/repo e.g. user/demo-app"},
                "pr_number": {"type": "integer", "description": "PR number to read"}
            },
            "required": ["repo", "pr_number"]
        }
    },
    {
        "name": "create_jira_ticket",
        "description": "Creates a Jira task ticket. Skips if ticket already exists.",
        "parameters": {
            "type": "object",
            "properties": {
                "title":       {"type": "string"},
                "description": {"type": "string"},
                "checklist":   {"type": "string"},
                "risks":       {"type": "string"}
            },
            "required": ["title", "description"]
        }
    },
    {
        "name": "post_slack_message",
        "description": "Posts a release notification to the #releases Slack channel.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        }
    },
    {
        "name": "create_calendar_event",
        "description": "Schedules a go/no-go meeting for release review.",
        "parameters": {
            "type": "object",
            "properties": {
                "meeting_title": {"type": "string"},
                "pr_url":        {"type": "string"}
            },
            "required": ["meeting_title"]
        }
    }
]


# ── Tool dispatcher ───────────────────────────────────────────────────────────
def execute_tool(name: str, args: dict) -> str:
    """Dispatch tool calls to real implementations."""
    print(f"  [TOOL CALL] {name}")

    if name == "get_pr_info":
        return json.dumps(get_pr_info(**args))

    if name == "create_jira_ticket":
        return json.dumps(create_jira_ticket(**args))

    if name == "post_slack_message":
        return json.dumps(post_slack_message(**args))

    if name == "create_calendar_event":
        return json.dumps(create_calendar_event(**args))

    return json.dumps({"error": f"Unknown tool: {name}"})


# ── LLM summarizer ────────────────────────────────────────────────────────────
def summarize_pr(pr_data: dict) -> dict:
    """Send PR data to Groq LLM, get structured summary back."""
    prompt = f"""
You are a release coordinator assistant. A developer just merged a pull request.

TITLE: {pr_data['title']}
DESCRIPTION:
{pr_data['body']}
CI STATUS: {pr_data['ci_status']}

Respond in this exact format and nothing else:

SUMMARY:
(2-3 sentences explaining what this PR does in plain English)

JIRA_TITLE:
(one line suitable as a Jira ticket title)

CHECKLIST:
- (acceptance criteria item 1)
- (acceptance criteria item 2)
- (acceptance criteria item 3)
- (acceptance criteria item 4)

RISKS:
- (risk or open item 1)
- (risk or open item 2)

SLACK_MESSAGE:
(2-3 sentences for the #releases Slack channel)

MEETING_TITLE:
(title for the go/no-go calendar meeting)
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content
    return parse_response(raw)


def parse_response(raw_text: str) -> dict:
    sections = {}
    current_key = None
    current_lines = []
    for line in raw_text.strip().split("\n"):
        line = line.strip()
        if line.endswith(":") and line.replace("_","").replace(" ","").isupper():
            if current_key:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = line[:-1]
            current_lines = []
        elif current_key:
            current_lines.append(line)
    if current_key:
        sections[current_key] = "\n".join(current_lines).strip()
    return {
        "summary":       sections.get("SUMMARY", "No summary generated"),
        "jira_title":    sections.get("JIRA_TITLE", "Release review needed"),
        "checklist":     sections.get("CHECKLIST", ""),
        "risks":         sections.get("RISKS", ""),
        "slack_message": sections.get("SLACK_MESSAGE", ""),
        "meeting_title": sections.get("MEETING_TITLE", "Go/no-go review")
    }


# ── Main agent loop ───────────────────────────────────────────────────────────
def run_agent(user_query: str):
    """
    MCP agentic loop:
    1. Parse repo and PR number from query
    2. Read PR from GitHub
    3. Summarize with Groq LLM
    4. Create Jira ticket
    5. Post to Slack
    6. Schedule meeting
    """
    print(f"\n[Agent] Received: {user_query}")

    # Parse repo and PR number from query string
    # Expected format: "repo=owner/repo pr=1" or just use defaults
    repo = "prateek-manocha22/demo-app"
    pr_number = 1
    if "repo=" in user_query:
        for part in user_query.split():
            if part.startswith("repo="):
                repo = part.split("=")[1]
            if part.startswith("pr="):
                pr_number = int(part.split("=")[1])

    print(f"\n{'='*55}")
    print(f"  PR RELEASE AGENT — STARTED")
    print(f"  Repo: {repo}  |  PR: #{pr_number}")
    print(f"{'='*55}\n")

    # Step 1: Read PR
    print("Step 1: Reading PR from GitHub...")
    pr_data = json.loads(execute_tool("get_pr_info", {
        "repo": repo,
        "pr_number": pr_number
    }))
    print(f"  Title:     {pr_data['title']}")
    print(f"  Author:    {pr_data['author']}")
    print(f"  CI Status: {pr_data['ci_status']}\n")

    # Step 2: Summarize with Groq LLM
    print("Step 2: Summarizing with Groq AI...")
    summary = summarize_pr(pr_data)
    print(f"  Summary: {summary['summary'][:80]}...\n")

    # Step 3: Create Jira ticket
    print("Step 3: Creating Jira ticket...")
    ticket = json.loads(execute_tool("create_jira_ticket", {
        "title":       summary["jira_title"],
        "description": summary["summary"],
        "checklist":   summary["checklist"],
        "risks":       summary["risks"]
    }))
    print(f"  Ticket: {ticket.get('url', 'failed')}\n")

    # Step 4: Post to Slack
    print("Step 4: Posting to Slack...")
    slack_msg = f"""*New Release* — `{pr_data['title']}`
*Author:* {pr_data['author']}
*CI Status:* {pr_data['ci_status']}

{summary['slack_message']}

*Jira:* {ticket.get('url', 'N/A')}
*PR:* {pr_data['pr_url']}"""

    slack_result = json.loads(execute_tool("post_slack_message", {
        "message": slack_msg
    }))
    print(f"  Slack: {'posted ✅' if slack_result.get('success') else 'failed ❌'}\n")

# Step 5: Schedule meeting
    print("Step 5: Scheduling go/no-go meeting...")
    meeting = json.loads(execute_tool("create_calendar_event", {
        "meeting_title": summary["meeting_title"],
        "pr_url":        pr_data["pr_url"],
        "risks":         summary["risks"]
    }))

    print(f"\n{'='*55}")
    print(f"  AGENT COMPLETE ✅")
    print(f"{'='*55}\n")

    result = {
        "pr_title":    pr_data["title"],
        "summary":     summary["summary"],
        "jira_url":    ticket.get("url", ""),
        "slack_posted": slack_result.get("success", False),
        "meeting":     meeting["time"],
        "pr_url":      pr_data["pr_url"]
    }

    print(f"[Tool Result] {json.dumps(result, indent=2)}")
    return result


if __name__ == "__main__":
    run_agent("repo=prateek-manocha22/demo-app pr=1")


# ===============================================================================================================================================
# from flask import Flask, jsonify, request
# from github_tool import get_pr_info
# from claude_brain import summarize_pr, check_contributor, load_whitelist, save_whitelist
# from jira_tool import create_jira_ticket
# from slack_tool import post_slack_message
# from calendar_tool import create_calendar_event
# import json
# import os
# import re
# import requests
# from datetime import datetime

# app = Flask(__name__)
# REPO = ""
# NOTIFICATIONS_FILE = "notifications.json"
# GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# # ── SECRET SCANNING ────────────────────────────────────────────────────────────

# SECRET_PATTERNS = [
#     (r'(?i)(api[_-]?key|apikey)\s*=\s*["\']?[\w\-]{8,}',         "API Key"),
#     (r'(?i)(secret[_-]?key|secret)\s*=\s*["\']?[\w\-]{8,}',      "Secret Key"),
#     (r'(?i)(password|passwd|pwd)\s*=\s*["\']?.{4,}',              "Password"),
#     (r'(?i)(token)\s*=\s*["\']?[\w\-\.]{8,}',                     "Token"),
#     (r'(?i)(aws_access_key_id)\s*=\s*["\']?[A-Z0-9]{16,}',        "AWS Access Key"),
#     (r'(?i)(aws_secret_access_key)\s*=\s*["\']?[\w\+\/]{30,}',    "AWS Secret"),
#     (r'sk-[a-zA-Z0-9]{20,}',                                       "OpenAI Key"),
#     (r'ghp_[a-zA-Z0-9]{36}',                                       "GitHub Token"),
#     (r'xox[baprs]-[0-9A-Za-z\-]{10,}',                            "Slack Token"),
#     (r'(?i)(database_url|db_url|mongo_uri)\s*=\s*["\']?\w+:\/\/', "DB Connection String"),
# ]

# def get_pr_diff(repo, pr_number):
#     url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
#     headers = {
#         "Authorization": f"token {GITHUB_TOKEN}",
#         "Accept": "application/vnd.github.v3+json"
#     }
#     try:
#         res = requests.get(url, headers=headers, timeout=10)
#         if res.status_code != 200:
#             return []
#         return res.json()
#     except Exception:
#         return []

# def scan_for_secrets(repo, pr_number):
#     files = get_pr_diff(repo, pr_number)
#     findings = []
#     for f in files:
#         filename = f.get("filename", "")
#         patch = f.get("patch", "")
#         if not patch:
#             continue
#         added_lines = [
#             (i + 1, line[1:])
#             for i, line in enumerate(patch.splitlines())
#             if line.startswith("+") and not line.startswith("+++")
#         ]
#         for line_num, content in added_lines:
#             for pattern, secret_type in SECRET_PATTERNS:
#                 match = re.search(pattern, content)
#                 if match:
#                     raw = match.group(0)
#                     redacted = raw[:18] + "..." if len(raw) > 18 else raw
#                     findings.append({
#                         "file":   filename,
#                         "line":   line_num,
#                         "type":   secret_type,
#                         "detail": redacted,
#                     })
#                     break
#     return {
#         "found":    len(findings) > 0,
#         "findings": findings
#     }

# # ── NOTIFICATIONS ──────────────────────────────────────────────────────────────

# def load_notifications():
#     if not os.path.exists(NOTIFICATIONS_FILE):
#         return []
#     with open(NOTIFICATIONS_FILE, "r") as f:
#         return json.load(f)

# def save_notifications(notifications):
#     with open(NOTIFICATIONS_FILE, "w") as f:
#         json.dump(notifications, f)

# def add_notification(pr_title, author, jira_url, slack_posted, meeting, security, pr_url, secret_scan=None):
#     notifications = load_notifications()
#     notifications.insert(0, {
#         "time":        datetime.now().strftime("%H:%M"),
#         "pr_title":    pr_title,
#         "author":      author,
#         "jira_url":    jira_url,
#         "slack_posted": slack_posted,
#         "meeting":     meeting,
#         "security":    security,
#         "pr_url":      pr_url,
#         "secret_scan": secret_scan or {"found": False, "findings": []},
#     })
#     save_notifications(notifications)

# # ── ROUTES ─────────────────────────────────────────────────────────────────────

# @app.route("/")
# def home():
#     return """<!DOCTYPE html>
# <html lang="en">
# <head>
# <meta charset="UTF-8"/>
# <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
# <title>NexRelease — AI Release Agent</title>
# <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet"/>
# <style>
# :root {
#   --bg:       #05060a;
#   --surface:  #0c0e15;
#   --card:     #111420;
#   --border:   #1e2235;
#   --accent:   #00f5a0;
#   --accent2:  #00c3ff;
#   --warn:     #ff6b35;
#   --text:     #e8eaf6;
#   --muted:    #555d7a;
#   --mono:     'Space Mono', monospace;
#   --sans:     'Syne', sans-serif;
# }
# *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
# html { scroll-behavior: smooth; }
# body {
#   font-family: var(--sans);
#   background: var(--bg);
#   color: var(--text);
#   min-height: 100vh;
#   overflow-x: hidden;
# }
# body::before {
#   content: '';
#   position: fixed;
#   inset: 0;
#   background-image:
#     linear-gradient(rgba(0,245,160,0.03) 1px, transparent 1px),
#     linear-gradient(90deg, rgba(0,245,160,0.03) 1px, transparent 1px);
#   background-size: 40px 40px;
#   pointer-events: none;
#   z-index: 0;
# }
# .orb { position: fixed; border-radius: 50%; filter: blur(120px); pointer-events: none; z-index: 0; opacity: 0.18; }
# .orb1 { width:500px; height:500px; background:#00f5a0; top:-150px; left:-150px; }
# .orb2 { width:400px; height:400px; background:#00c3ff; bottom:-100px; right:-100px; }
# .outer { position: relative; z-index: 1; display: grid; grid-template-columns: 340px 1fr; gap: 24px; max-width: 1300px; margin: 0 auto; padding: 0 24px 80px; }
# .notif-col { padding-top: 28px; }
# .notif-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
# .notif-title { font-family: var(--mono); font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; }
# .clear-btn { font-family: var(--mono); font-size: 10px; color: var(--warn); background: transparent; border: 1px solid var(--warn); border-radius: 6px; padding: 4px 10px; cursor: pointer; transition: background 0.15s; }
# .clear-btn:hover { background: rgba(255,107,53,0.1); }
# .notif-feed { display: flex; flex-direction: column; gap: 10px; }
# .notif-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; transition: border-color 0.3s; animation: fadeUp 0.4s ease both; }
# .notif-card.threat  { border-color: rgba(255,107,53,0.5); background: rgba(255,107,53,0.04); }
# .notif-card.safe    { border-color: rgba(0,245,160,0.3); }
# .notif-card.secrets { border-color: rgba(255,180,0,0.5); background: rgba(255,180,0,0.04); }
# .notif-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
# .notif-time { font-family: var(--mono); font-size: 10px; color: var(--muted); }
# .notif-del { background: transparent; border: none; color: var(--muted); cursor: pointer; font-size: 14px; line-height: 1; padding: 0 4px; }
# .notif-del:hover { color: var(--warn); }
# .notif-pr { font-size: 12px; font-weight: 600; color: var(--text); margin-bottom: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
# .notif-meta { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-bottom: 8px; }
# .notif-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
# .nbadge { font-family: var(--mono); font-size: 10px; padding: 3px 8px; border-radius: 5px; font-weight: 700; }
# .nbadge.ok     { background: rgba(0,245,160,0.1);  color: var(--accent);  border: 1px solid rgba(0,245,160,0.2); }
# .nbadge.warn   { background: rgba(255,107,53,0.1); color: var(--warn);    border: 1px solid rgba(255,107,53,0.2); }
# .nbadge.blue   { background: rgba(0,195,255,0.1);  color: var(--accent2); border: 1px solid rgba(0,195,255,0.2); }
# .nbadge.secret { background: rgba(255,180,0,0.1);  color: #ffb400;        border: 1px solid rgba(255,180,0,0.3); }
# .more-btn { font-family: var(--mono); font-size: 10px; color: var(--accent2); background: transparent; border: 1px solid rgba(0,195,255,0.2); border-radius: 6px; padding: 4px 10px; cursor: pointer; width: 100%; transition: background 0.15s; }
# .more-btn:hover { background: rgba(0,195,255,0.05); }
# .notif-detail { display: none; margin-top: 10px; border-top: 1px solid var(--border); padding-top: 10px; font-family: var(--mono); font-size: 11px; color: var(--muted); line-height: 1.8; }
# .notif-detail a { color: var(--accent2); text-decoration: none; word-break: break-all; }
# .secret-finding { background: rgba(255,180,0,0.07); border: 1px solid rgba(255,180,0,0.2); border-radius: 6px; padding: 6px 10px; margin-top: 6px; font-size: 10px; }
# .secret-finding .sf-file { color: #ffb400; font-weight: 700; }
# .secret-finding .sf-detail { color: var(--muted); margin-top: 2px; }
# .empty-feed { font-family: var(--mono); font-size: 12px; color: var(--muted); text-align: center; padding: 32px 0; }
# .main-col { min-width: 0; }
# header { display: flex; align-items: center; justify-content: space-between; padding: 28px 0 48px; border-bottom: 1px solid var(--border); margin-bottom: 56px; animation: fadeDown 0.6s ease both; }
# .logo { display: flex; align-items: center; gap: 12px; }
# .logo-icon { width: 36px; height: 36px; background: linear-gradient(135deg, var(--accent), var(--accent2)); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
# .logo-text { font-size: 20px; font-weight: 800; letter-spacing: -0.5px; }
# .logo-text span { color: var(--accent); }
# .status-pill { font-family: var(--mono); font-size: 11px; padding: 5px 12px; border-radius: 20px; border: 1px solid var(--accent); color: var(--accent); display: flex; align-items: center; gap: 6px; }
# .pulse-dot { width: 7px; height: 7px; background: var(--accent); border-radius: 50%; animation: pulse 1.5s infinite; }
# .hero { margin-bottom: 56px; animation: fadeUp 0.7s 0.1s ease both; }
# .hero-eyebrow { font-family: var(--mono); font-size: 11px; color: var(--accent); letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 16px; }
# .hero h1 { font-size: clamp(28px, 4vw, 48px); font-weight: 800; line-height: 1.1; letter-spacing: -1.5px; margin-bottom: 16px; }
# .hero h1 .grad { background: linear-gradient(90deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
# .hero p { font-size: 15px; color: var(--muted); line-height: 1.7; max-width: 540px; }
# .pipeline { display: flex; align-items: center; gap: 0; margin-bottom: 48px; animation: fadeUp 0.7s 0.2s ease both; overflow-x: auto; padding-bottom: 4px; }
# .pipe-step { display: flex; flex-direction: column; align-items: center; gap: 6px; flex-shrink: 0; }
# .pipe-icon { width: 48px; height: 48px; background: var(--card); border: 1px solid var(--border); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; transition: border-color 0.3s, transform 0.3s; }
# .pipe-step.active .pipe-icon { border-color: var(--accent); box-shadow: 0 0 20px rgba(0,245,160,0.2); transform: translateY(-3px); }
# .pipe-step.done .pipe-icon { border-color: var(--accent); background: rgba(0,245,160,0.08); }
# .pipe-label { font-family: var(--mono); font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
# .pipe-step.active .pipe-label, .pipe-step.done .pipe-label { color: var(--accent); }
# .pipe-arrow { width: 32px; height: 2px; background: var(--border); flex-shrink: 0; margin-bottom: 20px; position: relative; transition: background 0.3s; }
# .pipe-arrow.lit { background: var(--accent); }
# .pipe-arrow::after { content: ''; position: absolute; right: -4px; top: -3px; border: 4px solid transparent; border-left-color: inherit; }
# .panel { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 28px; margin-bottom: 24px; animation: fadeUp 0.7s 0.3s ease both; }
# .panel-title { font-size: 13px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 20px; display: flex; align-items: center; gap: 8px; }
# .panel-title::before { content: ''; width: 3px; height: 14px; background: var(--accent); border-radius: 2px; }
# .fields { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; margin-bottom: 20px; }
# .field { display: flex; flex-direction: column; gap: 6px; }
# .field label { font-family: var(--mono); font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; }
# input[type="text"], input[type="number"] { background: var(--surface); border: 1px solid var(--border); color: var(--text); padding: 10px 14px; border-radius: 8px; font-family: var(--mono); font-size: 13px; outline: none; transition: border-color 0.2s, box-shadow 0.2s; }
# input[type="text"] { width: 260px; }
# input[type="number"] { width: 90px; }
# input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(0,245,160,0.1); }
# .run-btn { padding: 11px 28px; background: var(--accent); color: #000; border: none; border-radius: 8px; font-family: var(--sans); font-size: 14px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: transform 0.15s, box-shadow 0.15s; letter-spacing: 0.02em; }
# .run-btn:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(0,245,160,0.3); }
# .run-btn:disabled { background: var(--border); color: var(--muted); cursor: not-allowed; transform: none; box-shadow: none; }
# .secondary-btn { padding: 9px 18px; background: transparent; color: var(--accent); border: 1px solid var(--accent); border-radius: 8px; font-family: var(--sans); font-size: 13px; font-weight: 700; cursor: pointer; transition: background 0.15s; }
# .secondary-btn:hover { background: rgba(0,245,160,0.08); }
# .danger-btn { padding: 6px 12px; background: transparent; color: var(--warn); border: 1px solid var(--warn); border-radius: 6px; font-family: var(--mono); font-size: 11px; cursor: pointer; transition: background 0.15s; }
# .danger-btn:hover { background: rgba(255,107,53,0.1); }
# .terminal { background: #070910; border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
# .terminal-bar { background: var(--surface); border-bottom: 1px solid var(--border); padding: 10px 16px; display: flex; align-items: center; gap: 8px; }
# .dot { width: 10px; height: 10px; border-radius: 50%; }
# .dot.r { background: #ff5f57; } .dot.y { background: #ffbd2e; } .dot.g { background: #28c941; }
# .terminal-title { font-family: var(--mono); font-size: 11px; color: var(--muted); margin-left: 8px; }
# .terminal-body { padding: 20px; font-family: var(--mono); font-size: 12px; line-height: 2; min-height: 160px; }
# .t-muted { color: var(--muted); } .t-green { color: var(--accent); } .t-blue { color: var(--accent2); } .t-warn { color: var(--warn); } .t-white { color: var(--text); } .t-gold { color: #ffb400; }
# #results { display: none; animation: fadeUp 0.5s ease both; }
# .results-title { font-family: var(--mono); font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; margin: 32px 0 16px; display: flex; align-items: center; gap: 10px; }
# .results-title::after { content: ''; flex: 1; height: 1px; background: var(--border); }
# .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
# .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 18px 20px; transition: border-color 0.3s, transform 0.3s; }
# .card:hover { border-color: rgba(0,245,160,0.3); transform: translateY(-2px); }
# .card-label { font-family: var(--mono); font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px; }
# .card-val { font-size: 14px; color: var(--text); line-height: 1.5; }
# .card-val a { color: var(--accent2); text-decoration: none; font-family: var(--mono); font-size: 12px; word-break: break-all; }
# .badge { display: inline-flex; align-items: center; gap: 5px; padding: 4px 10px; border-radius: 6px; font-family: var(--mono); font-size: 11px; font-weight: 700; }
# .badge.ok  { background: rgba(0,245,160,0.1); color: var(--accent); border: 1px solid rgba(0,245,160,0.25); }
# .badge.err { background: rgba(255,107,53,0.1); color: var(--warn);  border: 1px solid rgba(255,107,53,0.25); }
# .summary-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px 22px; margin-bottom: 12px; }
# .summary-card p { font-size: 14px; color: var(--text); line-height: 1.8; }
# .security-card { border-radius: 12px; padding: 20px 22px; margin-bottom: 12px; border: 1px solid rgba(255,107,53,0.4); background: rgba(255,107,53,0.05); }
# .security-card.safe { border-color: rgba(0,245,160,0.4); background: rgba(0,245,160,0.05); }
# .secret-scan-card { border-radius: 12px; padding: 20px 22px; margin-bottom: 12px; border: 1px solid rgba(255,180,0,0.45); background: rgba(255,180,0,0.05); }
# .secret-scan-card.clean { border-color: rgba(0,245,160,0.4); background: rgba(0,245,160,0.05); }
# .secret-scan-card .scan-title { font-family: var(--mono); font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px; }
# .secret-scan-card .scan-headline { font-size: 14px; font-weight: 700; margin-bottom: 8px; }
# .scan-headline.danger { color: #ffb400; }
# .scan-headline.ok { color: var(--accent); }
# .finding-row { display: flex; flex-direction: column; gap: 3px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,180,0,0.15); border-radius: 8px; padding: 10px 14px; margin-top: 8px; }
# .finding-row .fr-file { font-family: var(--mono); font-size: 11px; color: #ffb400; }
# .finding-row .fr-type { font-family: var(--mono); font-size: 10px; color: var(--muted); }
# .finding-row .fr-detail { font-family: var(--mono); font-size: 11px; color: var(--text); word-break: break-all; }
# .scan-tip { margin-top: 12px; font-family: var(--mono); font-size: 10px; color: var(--muted); line-height: 1.6; }
# .hint { margin-top: 16px; background: rgba(0,195,255,0.05); border: 1px solid rgba(0,195,255,0.15); border-radius: 8px; padding: 12px 16px; font-family: var(--mono); font-size: 11px; color: #79c0ff; display: flex; align-items: center; gap: 8px; }
# .hint code { background: rgba(0,0,0,0.3); padding: 2px 7px; border-radius: 4px; }
# .spin { display: inline-block; width: 12px; height: 12px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.7s linear infinite; vertical-align: middle; margin-right: 4px; }
# .member-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); }
# .member-row:last-child { border-bottom: none; }
# .member-name { font-family: var(--mono); font-size: 13px; color: var(--text); }
# .add-row { display: flex; gap: 8px; margin-top: 16px; }
# .add-row input { flex: 1; }
# .sec-modal { position:fixed; inset:0; z-index:300; background:rgba(5,6,10,0.93); backdrop-filter:blur(12px); display:none; align-items:center; justify-content:center; }
# .sec-modal.open { display:flex; animation:fadeUp 0.3s ease; }
# .sec-panel { background:#0c0e15; border:2px solid rgba(255,107,53,0.7); border-radius:20px; padding:44px 40px; max-width:500px; width:92%; text-align:center; animation:fadeUp 0.4s ease; box-shadow:0 0 80px rgba(255,107,53,0.12); }
# .sec-icon { font-size:52px; margin-bottom:18px; display:block; animation:pulse 1s infinite; }
# .sec-title { font-family:var(--mono); font-size:12px; font-weight:700; color:var(--warn); letter-spacing:0.15em; text-transform:uppercase; margin-bottom:12px; }
# .sec-sub { font-size:15px; color:var(--text); line-height:1.8; margin-bottom:16px; }
# .sec-details { font-family:var(--mono); font-size:11px; color:var(--muted); background:rgba(255,107,53,0.06); border:1px solid rgba(255,107,53,0.2); border-radius:10px; padding:14px 16px; text-align:left; line-height:2.2; margin-bottom:6px; }
# .sec-actions { display:flex; gap:10px; justify-content:center; margin-top:24px; }
# .sec-dismiss { padding:11px 24px; background:transparent; color:var(--muted); border:1px solid var(--border); border-radius:8px; font-family:var(--sans); font-size:14px; font-weight:700; cursor:pointer; transition:background 0.15s; }
# .sec-dismiss:hover { background:var(--border); color:var(--text); }
# .sec-view { padding:11px 24px; background:var(--warn); color:#000; border:none; border-radius:8px; font-family:var(--sans); font-size:14px; font-weight:700; cursor:pointer; transition:transform 0.15s, box-shadow 0.15s; }
# .sec-view:hover { transform:translateY(-2px); box-shadow:0 8px 24px rgba(255,107,53,0.35); }
# #toast-container { position:fixed; top:20px; right:20px; z-index:200; display:flex; flex-direction:column; gap:8px; pointer-events:none; }
# .toast { padding:13px 16px; border-radius:10px; font-family:var(--mono); font-size:12px; display:flex; align-items:center; gap:10px; animation:fadeUp 0.3s ease; max-width:360px; pointer-events:all; line-height:1.5; }
# .toast.threat { background:#1c0d08; border:1px solid rgba(255,107,53,0.55); color:var(--warn); }
# .toast.ok     { background:#081c10; border:1px solid rgba(0,245,160,0.4);  color:var(--accent); }
# .toast-close  { margin-left:auto; opacity:0.5; cursor:pointer; font-size:14px; flex-shrink:0; }
# .toast-close:hover { opacity:1; }
# @keyframes fadeUp   { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
# @keyframes fadeDown { from { opacity:0; transform:translateY(-10px); } to { opacity:1; transform:translateY(0); } }
# @keyframes pulse    { 0%,100%{ opacity:1; transform:scale(1); } 50%{ opacity:0.4; transform:scale(0.85); } }
# @keyframes spin     { to { transform:rotate(360deg); } }
# @media(max-width:900px) {
#   .outer { grid-template-columns: 1fr; }
#   .notif-col { order: 2; }
#   .main-col  { order: 1; }
# }
# @media(max-width:600px) {
#   .cards { grid-template-columns: 1fr; }
#   input[type="text"] { width: 100%; }
#   .fields { flex-direction: column; }
# }
# </style>
# </head>
# <body>
# <div class="orb orb1"></div>
# <div class="orb orb2"></div>

# <div class="sec-modal" id="sec-modal">
#   <div class="sec-panel">
#     <span class="sec-icon">⚠️</span>
#     <div class="sec-title">Unauthorized Contributor Detected</div>
#     <div class="sec-sub" id="sec-modal-msg">A PR was submitted by a user not on your whitelist.</div>
#     <div class="sec-details" id="sec-modal-details"></div>
#     <div class="sec-actions">
#       <button class="sec-dismiss" onclick="dismissAlert()">Dismiss</button>
#       <button class="sec-view" id="sec-view-btn">View on GitHub →</button>
#     </div>
#   </div>
# </div>

# <div id="toast-container"></div>

# <div class="outer">

#   <div class="notif-col">
#     <div class="notif-header">
#       <span class="notif-title">🔔 Live PR Feed</span>
#       <button class="clear-btn" onclick="clearAll()">Clear All</button>
#     </div>
#     <div class="notif-feed" id="notif-feed">
#       <div class="empty-feed">No PR merges yet.<br>Merge a PR to see notifications.</div>
#     </div>
#   </div>

#   <div class="main-col">
#     <header>
#       <div class="logo">
#         <div class="logo-icon">⚡</div>
#         <div class="logo-text">Nex<span>Release</span></div>
#       </div>
#       <div class="status-pill"><div class="pulse-dot"></div>AGENT ONLINE</div>
#     </header>

#     <div class="hero">
#       <div class="hero-eyebrow">// MCP-Powered Automation</div>
#       <h1>Release coordination,<br><span class="grad">fully automated.</span></h1>
#       <p>Merge a PR and the AI agent reads it, files the Jira ticket, pings Slack, and schedules the go/no-go — all in under 10 seconds.</p>
#     </div>

#     <div class="pipeline" id="pipeline">
#       <div class="pipe-step" id="ps0"><div class="pipe-icon">🔀</div><div class="pipe-label">PR Merge</div></div>
#       <div class="pipe-arrow" id="pa0"></div>
#       <div class="pipe-step" id="ps1"><div class="pipe-icon">🧠</div><div class="pipe-label">AI Read</div></div>
#       <div class="pipe-arrow" id="pa1"></div>
#       <div class="pipe-step" id="ps2"><div class="pipe-icon">🎫</div><div class="pipe-label">Jira</div></div>
#       <div class="pipe-arrow" id="pa2"></div>
#       <div class="pipe-step" id="ps3"><div class="pipe-icon">💬</div><div class="pipe-label">Slack</div></div>
#       <div class="pipe-arrow" id="pa3"></div>
#       <div class="pipe-step" id="ps4"><div class="pipe-icon">📅</div><div class="pipe-label">Meeting</div></div>
#     </div>

#     <div class="panel">
#       <div class="panel-title">Trigger Agent Manually</div>
#       <div class="fields">
#         <div class="field">
#           <label>GitHub Repo</label>
#           <input type="text" id="repo" value="" placeholder="enter your repo e.g. john/my-project" onchange="saveRepo()"/>
#         </div>
#         <div class="field">
#           <label>PR Number</label>
#           <input type="number" id="pr-number" value="1" min="1"/>
#         </div>
#         <button class="run-btn" id="run-btn" onclick="runAgent()">
#           <span id="btn-icon">▶</span> Run Agent
#         </button>
#       </div>
#       <div class="terminal">
#         <div class="terminal-bar">
#           <div class="dot r"></div><div class="dot y"></div><div class="dot g"></div>
#           <span class="terminal-title">release-agent — bash</span>
#         </div>
#         <div class="terminal-body" id="log"><span class="t-muted">$ waiting for trigger...</span></div>
#       </div>
#       <div class="hint">🔗 Auto-trigger: point GitHub webhooks to <code>POST /webhook</code> — fires on every PR open or merge</div>
#     </div>

#     <div class="panel">
#       <div class="panel-title">🔐 Team Whitelist</div>
#       <p style="font-size:13px;color:var(--muted);margin-bottom:16px;">Add GitHub usernames of approved contributors. PRs from unknown users will trigger a security alert.</p>
#       <div id="member-list"></div>
#       <div class="add-row">
#         <input type="text" id="new-member" placeholder="github-username"/>
#         <button class="secondary-btn" onclick="addMember()">+ Add</button>
#       </div>
#     </div>

#     <div id="results">
#       <div class="results-title">Agent Output</div>
#       <div class="summary-card">
#         <div class="card-label">📋 PR Summary</div>
#         <p id="summary-text"></p>
#       </div>
#       <div id="secret-scan-section"></div>
#       <div id="security-section" style="margin-bottom:12px;"></div>
#       <div class="cards">
#         <div class="card">
#           <div class="card-label">🎫 Jira Ticket</div>
#           <div class="card-val"><a id="jira-link" href="#" target="_blank">—</a></div>
#         </div>
#         <div class="card">
#           <div class="card-label">💬 Slack</div>
#           <div class="card-val" id="slack-val">—</div>
#         </div>
#         <div class="card">
#           <div class="card-label">📅 Meeting</div>
#           <div class="card-val" id="meeting-val">—</div>
#         </div>
#         <div class="card">
#           <div class="card-label">🔗 Pull Request</div>
#           <div class="card-val"><a id="pr-link" href="#" target="_blank">View on GitHub →</a></div>
#         </div>
#       </div>
#     </div>
#   </div>
# </div>

# <script>
# const log = document.getElementById('log');
# let allNotifications = [];
# let lastSeenIds = new Set();

# // ── PERSISTENT REPO ────────────────────────────────────────────────────────────
# const savedRepo = localStorage.getItem('nexrelease_repo');
# if (savedRepo) {
#   document.getElementById('repo').value = savedRepo;
# }
# function saveRepo() {
#   const repo = document.getElementById('repo').value.trim();
#   if (repo) localStorage.setItem('nexrelease_repo', repo);
# }

# // ── TOAST ──────────────────────────────────────────────────────────────────────
# function showToast(msg, type='ok', duration=6000) {
#   const tc = document.getElementById('toast-container');
#   const t = document.createElement('div');
#   t.className = 'toast ' + type;
#   t.innerHTML = `<span>${type === 'threat' ? '⚠' : '✓'}</span><span style="flex:1">${msg}</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
#   tc.appendChild(t);
#   setTimeout(() => { if (t.parentElement) t.remove(); }, duration);
# }

# // ── SECURITY ALERT MODAL ───────────────────────────────────────────────────────
# function showSecurityAlert(n) {
#   document.getElementById('sec-modal-msg').textContent =
#     `PR "${n.pr_title}" was submitted by @${n.author} who is NOT on your whitelist.`;
#   document.getElementById('sec-modal-details').innerHTML =
#     `Author: &nbsp;&nbsp;@${n.author}<br>Time: &nbsp;&nbsp;&nbsp;${n.time}<br>Reason: &nbsp;${n.security ? n.security.message : 'Not on whitelist'}`;
#   document.getElementById('sec-view-btn').onclick = () => {
#     dismissAlert();
#     if (n.pr_url) window.open(n.pr_url, '_blank');
#   };
#   document.getElementById('sec-modal').classList.add('open');
# }
# function dismissAlert() {
#   document.getElementById('sec-modal').classList.remove('open');
# }

# // ── NOTIFICATION FEED ──────────────────────────────────────────────────────────
# async function loadNotifications() {
#   const res = await fetch('/notifications');
#   const data = await res.json();
#   allNotifications = data.notifications;
#   renderNotifications(allNotifications);

#   allNotifications.forEach((n) => {
#     const uid = `${n.pr_title}-${n.time}`;
#     if (!lastSeenIds.has(uid)) {
#       lastSeenIds.add(uid);
#       if (n.security && n.security.status === 'unauthorized') {
#         showSecurityAlert(n);
#         showToast(`Security threat: PR by @${n.author} is not whitelisted`, 'threat', 10000);
#       } else if (lastSeenIds.size > 1) {
#         showToast(`PR processed — Jira, Slack & Meeting done`, 'ok');
#       }
#     }
#   });
# }

# function renderNotifications(notifications) {
#   const feed = document.getElementById('notif-feed');
#   if (notifications.length === 0) {
#     feed.innerHTML = '<div class="empty-feed">No PR merges yet.<br>Merge a PR to see notifications.</div>';
#     return;
#   }
#   feed.innerHTML = notifications.map((n, i) => {
#     const isThreat   = n.security && n.security.status === 'unauthorized';
#     const isVerified = n.security && n.security.status === 'verified';
#     const hasSecrets = n.secret_scan && n.secret_scan.found;
#     const cardClass  = hasSecrets ? 'secrets' : isThreat ? 'threat' : isVerified ? 'safe' : '';

#     let secretDetail = '';
#     if (hasSecrets) {
#       secretDetail = n.secret_scan.findings.map(f => `
#         <div class="secret-finding">
#           <div class="sf-file">📄 ${f.file} — line ${f.line}</div>
#           <div class="sf-detail">${f.type}: <code>${f.detail}</code></div>
#         </div>`).join('');
#     }

#     return `
#     <div class="notif-card ${cardClass}">
#       <div class="notif-top">
#         <span class="notif-time">${n.time}</span>
#         <button class="notif-del" onclick="deleteNotif(${i})">✕</button>
#       </div>
#       <div class="notif-pr">${n.pr_title}</div>
#       <div class="notif-meta">by @${n.author}</div>
#       <div class="notif-badges">
#         <span class="nbadge blue">PR</span>
#         ${n.jira_url     ? '<span class="nbadge ok">Jira ✓</span>'           : ''}
#         ${n.slack_posted ? '<span class="nbadge ok">Slack ✓</span>'          : ''}
#         ${n.meeting      ? '<span class="nbadge ok">Meeting ✓</span>'        : ''}
#         ${isThreat       ? '<span class="nbadge warn">⚠ Unauthorized</span>' : ''}
#         ${isVerified     ? '<span class="nbadge ok">✓ Verified</span>'       : ''}
#         ${hasSecrets     ? '<span class="nbadge secret">🔑 Secrets</span>'   : ''}
#       </div>
#       <button class="more-btn" onclick="toggleDetail(${i})">More Info ▾</button>
#       <div class="notif-detail" id="detail-${i}">
#         ${n.jira_url ? `<div>🎫 Jira: <a href="${n.jira_url}" target="_blank">${n.jira_url}</a></div>` : ''}
#         ${n.meeting  ? `<div>📅 Meeting: ${n.meeting}</div>` : ''}
#         ${n.pr_url   ? `<div>🔗 PR: <a href="${n.pr_url}" target="_blank">View on GitHub</a></div>` : ''}
#         ${n.security ? `<div style="margin-top:6px;color:${isThreat ? 'var(--warn)' : 'var(--accent)'};">${n.security.message}</div>` : ''}
#         ${hasSecrets ? `<div style="margin-top:8px;color:#ffb400;font-weight:700;">⚠️ Potential secrets detected:</div>${secretDetail}` : ''}
#       </div>
#     </div>`;
#   }).join('');
# }

# function toggleDetail(i) {
#   const d = document.getElementById('detail-' + i);
#   d.style.display = d.style.display === 'block' ? 'none' : 'block';
# }

# async function deleteNotif(i) {
#   await fetch('/notifications/delete', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({index: i}) });
#   loadNotifications();
# }

# async function clearAll() {
#   await fetch('/notifications/clear', { method: 'POST' });
#   lastSeenIds.clear();
#   loadNotifications();
# }

# // Initial load — seed lastSeenIds without firing alerts for existing notifications
# (async () => {
#   const res = await fetch('/notifications');
#   const data = await res.json();
#   allNotifications = data.notifications;
#   allNotifications.forEach(n => lastSeenIds.add(`${n.pr_title}-${n.time}`));
#   renderNotifications(allNotifications);
# })();

# setInterval(loadNotifications, 5000);

# // ── WHITELIST ──────────────────────────────────────────────────────────────────
# async function loadMembers() {
#   const res = await fetch('/whitelist');
#   const data = await res.json();
#   renderMembers(data.members);
# }
# function renderMembers(members) {
#   const list = document.getElementById('member-list');
#   if (members.length === 0) {
#     list.innerHTML = '<p style="font-family:var(--mono);font-size:12px;color:var(--muted);">No members added yet.</p>';
#     return;
#   }
#   list.innerHTML = members.map((m, i) => `
#     <div class="member-row">
#       <span class="member-name">@${m}</span>
#       <button class="danger-btn" onclick="removeMember(${i})">Remove</button>
#     </div>`).join('');
# }
# async function addMember() {
#   const input = document.getElementById('new-member');
#   const name = input.value.trim();
#   if (!name) return;
#   await fetch('/whitelist/add', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({username: name}) });
#   input.value = '';
#   loadMembers();
# }
# async function removeMember(index) {
#   await fetch('/whitelist/remove', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({index: index}) });
#   loadMembers();
# }
# loadMembers();

# // ── AGENT ──────────────────────────────────────────────────────────────────────
# function addLine(html) {
#   log.innerHTML += '<br>' + html;
#   log.scrollTop = log.scrollHeight;
# }
# function setStep(idx) {
#   for (let i = 0; i < 5; i++) {
#     const s = document.getElementById('ps' + i);
#     s.classList.remove('active', 'done');
#     if (i < idx) s.classList.add('done');
#     if (i === idx) s.classList.add('active');
#     if (i < 4) document.getElementById('pa' + i).classList.toggle('lit', i < idx);
#   }
# }
# function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

# function renderSecretScan(scan) {
#   const el = document.getElementById('secret-scan-section');
#   if (!scan) { el.innerHTML = ''; return; }
#   if (scan.found) {
#     const rows = scan.findings.map(f => `
#       <div class="finding-row">
#         <div class="fr-file">📄 ${f.file} <span style="color:var(--muted);">— line ${f.line}</span></div>
#         <div class="fr-type">${f.type}</div>
#         <div class="fr-detail">${f.detail}</div>
#       </div>`).join('');
#     el.innerHTML = `
#       <div class="secret-scan-card">
#         <div class="scan-title">🔑 Secret Scan</div>
#         <div class="scan-headline danger">⚠️ Potential secret${scan.findings.length > 1 ? 's' : ''} detected in commit</div>
#         ${rows}
#         <div class="scan-tip">Remove these values immediately and rotate any exposed credentials.<br>Store secrets in environment variables or a vault — never in code.</div>
#       </div>`;
#   } else {
#     el.innerHTML = `
#       <div class="secret-scan-card clean">
#         <div class="scan-title">🔑 Secret Scan</div>
#         <div class="scan-headline ok">✓ No secrets detected in diff</div>
#       </div>`;
#   }
# }

# async function runAgent() {
#   const repo    = document.getElementById('repo').value.trim();
#   const pr      = document.getElementById('pr-number').value;
#   const btn     = document.getElementById('run-btn');
#   const results = document.getElementById('results');
#   if (!repo || !pr) return;

#   btn.disabled = true;
#   document.getElementById('btn-icon').innerHTML = '<span class="spin"></span>';
#   results.style.display = 'none';
#   log.innerHTML = '<span class="t-muted">$ release-agent run --repo ' + repo + ' --pr ' + pr + '</span>';
#   setStep(-1);
#   await sleep(300);
#   addLine('<span class="t-blue">⟳  initializing agent...</span>');
#   await sleep(500);
#   setStep(0);
#   addLine('<span class="t-white">[ 1/5 ]</span> <span class="t-muted">reading PR from GitHub...</span>');

#   try {
#     const res  = await fetch('/run?repo=' + encodeURIComponent(repo) + '&pr=' + pr);
#     const data = await res.json();

#     if (data.error) {
#       addLine('<span class="t-warn">✗  error: ' + data.error + '</span>');
#       btn.disabled = false;
#       document.getElementById('btn-icon').textContent = '▶';
#       return;
#     }

#     await sleep(400); setStep(1);
#     addLine('<span class="t-green">✓</span>  <span class="t-white">PR read:</span> <span class="t-blue">' + data.pr_title + '</span>');

#     if (data.security) {
#       if (data.security.status === 'unauthorized')
#         addLine('<span class="t-warn">⚠  SECURITY: ' + data.security.message + '</span>');
#       else if (data.security.status === 'verified')
#         addLine('<span class="t-green">🔐 ' + data.security.message + '</span>');
#     }

#     if (data.secret_scan) {
#       if (data.secret_scan.found) {
#         addLine('<span class="t-gold">🔑 SECRET SCAN: ' + data.secret_scan.findings.length + ' potential secret(s) found!</span>');
#         data.secret_scan.findings.forEach(f => {
#           addLine('<span class="t-gold">   ↳ ' + f.file + ' (line ' + f.line + ') — ' + f.type + '</span>');
#         });
#       } else {
#         addLine('<span class="t-green">🔑 Secret scan: no secrets detected</span>');
#       }
#     }

#     await sleep(400);
#     addLine('<span class="t-white">[ 2/5 ]</span> <span class="t-muted">summarizing with Groq AI...</span>');
#     await sleep(500); setStep(2);
#     addLine('<span class="t-green">✓</span>  <span class="t-white">summary generated</span>');
#     await sleep(300);
#     addLine('<span class="t-white">[ 3/5 ]</span> <span class="t-muted">creating Jira ticket...</span>');
#     await sleep(400); setStep(3);
#     addLine('<span class="t-green">✓</span>  <span class="t-white">ticket →</span> <span class="t-blue">' + (data.jira_url || 'N/A') + '</span>');
#     await sleep(300);
#     addLine('<span class="t-white">[ 4/5 ]</span> <span class="t-muted">posting to Slack...</span>');
#     await sleep(400); setStep(4);
#     addLine('<span class="t-green">✓</span>  <span class="t-white">Slack posted to #releases</span>');
#     await sleep(300);
#     addLine('<span class="t-white">[ 5/5 ]</span> <span class="t-muted">scheduling go/no-go meeting...</span>');
#     await sleep(400);
#     addLine('<span class="t-green">✓</span>  <span class="t-white">meeting →</span> <span class="t-blue">' + (data.meeting || 'N/A') + '</span>');
#     await sleep(300);
#     addLine('');
#     addLine('<span class="t-green">══════════════════════════════════</span>');
#     addLine('<span class="t-green">  AGENT COMPLETE — all steps done  </span>');
#     addLine('<span class="t-green">══════════════════════════════════</span>');

#     document.getElementById('summary-text').textContent = data.summary || '—';
#     renderSecretScan(data.secret_scan);

#     const jiraLink = document.getElementById('jira-link');
#     jiraLink.href = data.jira_url || '#';
#     jiraLink.textContent = data.jira_url || '—';
#     document.getElementById('slack-val').innerHTML = data.slack_posted
#       ? '<span class="badge ok">✓ Posted</span>'
#       : '<span class="badge err">✗ Failed</span>';
#     document.getElementById('meeting-val').textContent = data.meeting || '—';
#     document.getElementById('pr-link').href = data.pr_url || '#';

#     const sec = document.getElementById('security-section');
#     if (data.security) {
#       const isOk   = data.security.status === 'verified';
#       const noList = data.security.status === 'no_whitelist';
#       sec.innerHTML = `<div class="security-card ${isOk || noList ? 'safe' : ''}">
#         <div class="card-label">🔐 Security Check</div>
#         <p style="font-size:14px;color:var(--text);margin-top:4px;">${data.security.message}</p>
#       </div>`;
#     }

#     results.style.display = 'block';
#     loadNotifications();
#   } catch(err) {
#     addLine('<span class="t-warn">✗  network error: ' + err + '</span>');
#   }

#   btn.disabled = false;
#   document.getElementById('btn-icon').textContent = '▶';
# }
# </script>
# </body>
# </html>
# """


# @app.route("/notifications")
# def get_notifications():
#     return jsonify({"notifications": load_notifications()})


# @app.route("/notifications/delete", methods=["POST"])
# def delete_notification():
#     data = request.get_json()
#     index = data.get("index")
#     notifications = load_notifications()
#     if index is not None and 0 <= index < len(notifications):
#         notifications.pop(index)
#         save_notifications(notifications)
#     return jsonify({"notifications": notifications})


# @app.route("/notifications/clear", methods=["POST"])
# def clear_notifications():
#     save_notifications([])
#     return jsonify({"notifications": []})


# @app.route("/whitelist")
# def get_whitelist():
#     return jsonify({"members": load_whitelist()})


# @app.route("/whitelist/add", methods=["POST"])
# def add_to_whitelist():
#     data = request.get_json()
#     username = data.get("username", "").strip()
#     if not username:
#         return jsonify({"error": "empty username"})
#     members = load_whitelist()
#     if username.lower() not in [m.lower() for m in members]:
#         members.append(username)
#         save_whitelist(members)
#     return jsonify({"members": members})


# @app.route("/whitelist/remove", methods=["POST"])
# def remove_from_whitelist():
#     data = request.get_json()
#     index = data.get("index")
#     members = load_whitelist()
#     if index is not None and 0 <= index < len(members):
#         members.pop(index)
#         save_whitelist(members)
#     return jsonify({"members": members})


# @app.route("/run")
# def run():
#     pr_number = request.args.get("pr", 1, type=int)
#     repo = request.args.get("repo", REPO)
#     try:
#         pr_data     = get_pr_info(repo, pr_number)
#         security    = check_contributor(pr_data["author"])
#         secret_scan = scan_for_secrets(repo, pr_number)
#         summary     = summarize_pr(pr_data)
#         ticket      = create_jira_ticket(
#             title=summary["jira_title"],
#             description=summary["summary"],
#             checklist=summary["checklist"],
#             risks=summary["risks"]
#         )
#         slack_message = f"""*New Release* — `{pr_data['title']}`
# *Author:* {pr_data['author']}
# *CI Status:* {pr_data['ci_status']}
# {summary['slack_message']}
# *Jira:* {ticket.get('url', 'N/A')}
# *PR:* {pr_data['pr_url']}""".strip()

#         if security["status"] == "unauthorized":
#             slack_message += f"\n⚠️ SECURITY ALERT: {security['message']}"
#         if secret_scan["found"]:
#             files_hit = ", ".join(set(f["file"] for f in secret_scan["findings"]))
#             slack_message += f"\n🔑 SECRET SCAN ALERT: Potential secrets detected in {files_hit}. Please rotate credentials immediately."

#         slack_result = post_slack_message(slack_message)
#         meeting = create_calendar_event(
#             meeting_title=summary["meeting_title"],
#             pr_url=pr_data["pr_url"],
#             risks=summary["risks"]
#         )
#         add_notification(
#             pr_title=pr_data["title"],
#             author=pr_data["author"],
#             jira_url=ticket.get("url", ""),
#             slack_posted=slack_result["success"],
#             meeting=meeting["time"],
#             security=security,
#             pr_url=pr_data["pr_url"],
#             secret_scan=secret_scan
#         )
#         return jsonify({
#             "pr_title":    pr_data["title"],
#             "summary":     summary["summary"],
#             "jira_url":    ticket.get("url", ""),
#             "slack_posted": slack_result["success"],
#             "meeting":     meeting["time"],
#             "pr_url":      pr_data["pr_url"],
#             "security":    security,
#             "secret_scan": secret_scan
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)})


# @app.route("/webhook", methods=["POST"])
# def webhook():
#     data = request.get_json()
#     action = data.get("action")
#     pr = data.get("pull_request", {})
#     is_merged = pr.get("merged", False)

#     if action in ["opened", "reopened"]:
#         pr_number = pr["number"]
#         repo = data["repository"]["full_name"]
#         try:
#             pr_data  = get_pr_info(repo, pr_number)
#             security = check_contributor(pr_data["author"])
#             if security["status"] == "unauthorized":
#                 add_notification(
#                     pr_title=pr_data["title"],
#                     author=pr_data["author"],
#                     jira_url="",
#                     slack_posted=False,
#                     meeting="",
#                     security=security,
#                     pr_url=pr_data["pr_url"],
#                     secret_scan={"found": False, "findings": []}
#                 )
#             return jsonify({"status": "security checked on open", "pr": pr_number})
#         except Exception as e:
#             return jsonify({"status": "error", "message": str(e)})

#     if action == "closed" and is_merged:
#         pr_number = pr["number"]
#         repo = data["repository"]["full_name"]
#         try:
#             pr_data     = get_pr_info(repo, pr_number)
#             security    = check_contributor(pr_data["author"])
#             secret_scan = scan_for_secrets(repo, pr_number)
#             summary     = summarize_pr(pr_data)
#             ticket      = create_jira_ticket(
#                 title=summary["jira_title"],
#                 description=summary["summary"],
#                 checklist=summary["checklist"],
#                 risks=summary["risks"]
#             )
#             slack_message = f"""*PR Auto-processed*
# *PR:* `{pr_data['title']}`
# *Author:* {pr_data['author']}
# {summary['slack_message']}
# *Jira:* {ticket.get('url', 'N/A')}
# {security['message']}""".strip()

#             if secret_scan["found"]:
#                 files_hit = ", ".join(set(f["file"] for f in secret_scan["findings"]))
#                 slack_message += f"\n🔑 SECRET SCAN ALERT: Potential secrets detected in {files_hit}. Rotate credentials immediately."

#             post_slack_message(slack_message)
#             meeting = create_calendar_event(
#                 meeting_title=summary["meeting_title"],
#                 pr_url=pr_data["pr_url"],
#                 risks=summary["risks"]
#             )
#             add_notification(
#                 pr_title=pr_data["title"],
#                 author=pr_data["author"],
#                 jira_url=ticket.get("url", ""),
#                 slack_posted=True,
#                 meeting=meeting["time"],
#                 security=security,
#                 pr_url=pr_data["pr_url"],
#                 secret_scan=secret_scan
#             )
#             return jsonify({"status": "agent triggered", "pr": pr_number})
#         except Exception as e:
#             return jsonify({"status": "error", "message": str(e)})

#     return jsonify({"status": "ignored"})


# if __name__ == "__main__":
#     app.run(debug=True, port=5000)