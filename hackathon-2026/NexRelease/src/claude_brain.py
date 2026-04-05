from openai import OpenAI
import json
import os


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

WHITELIST_FILE = "whitelist.json"

def load_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        return []
    with open(WHITELIST_FILE, "r") as f:
        return json.load(f)

def save_whitelist(members):
    with open(WHITELIST_FILE, "w") as f:
        json.dump(members, f)

def check_contributor(author: str) -> dict:
    whitelist = load_whitelist()
    if not whitelist:
        return {"status": "no_whitelist", "message": "⚪ No whitelist configured."}
    if author.lower() in [m.lower() for m in whitelist]:
        return {"status": "verified", "message": f"✅ Contributor verified: {author}"}
    return {"status": "unauthorized", "message": f"⚠️ Unauthorized contributor detected: {author}. Please review immediately."}

def summarize_pr(pr_data):
    prompt = f"""
You are a release coordinator assistant. A developer just merged a pull request.
Here is the pull request information:
TITLE: {pr_data['title']}
DESCRIPTION:
{pr_data['body']}
CI STATUS: {pr_data['ci_status']}
Your job is to produce a structured release summary.
Respond in this exact format and nothing else:
SUMMARY:
(2-3 sentences explaining what this PR does in plain English)
JIRA_TITLE:
(one line, suitable as a Jira ticket title)
CHECKLIST:
* (acceptance criteria item 1)
* (acceptance criteria item 2)
* (acceptance criteria item 3)
* (acceptance criteria item 4)
RISKS:
* (risk or open item 1)
* (risk or open item 2)
SLACK_MESSAGE:
(2-3 sentences for the #releases Slack channel,
mention the PR title, tag @channel if CI failed)
MEETING_TITLE:
(title for the go/no-go calendar meeting)
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content
    return parse_response(raw)

def parse_response(raw_text):
    sections = {}
    current_key = None
    current_lines = []
    for line in raw_text.strip().split("\n"):
        line = line.strip()
        if line.endswith(":") and line.replace("_", "").replace(" ", "").isupper():
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