import requests
import base64
import os
import json
from dotenv import load_dotenv
load_dotenv()

JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

PROCESSED_PRS_FILE = "processed_prs.json"


def get_auth():
    credentials = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
    return base64.b64encode(credentials.encode("utf-8")).decode("utf-8")


def get_headers():
    return {
        "Authorization": f"Basic {get_auth()}",
        "Content-Type": "application/json"
    }


def load_processed():
    if os.path.exists(PROCESSED_PRS_FILE):
        with open(PROCESSED_PRS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_processed(title, key, url, pr_id=None):
    data = load_processed()
    if pr_id:
        data[f"pr_{pr_id}"] = {"key": key, "url": url}
    data[title.lower()] = {"key": key, "url": url}
    with open(PROCESSED_PRS_FILE, "w") as f:
        json.dump(data, f)


def ticket_exists(pr_title, pr_id=None):
    data = load_processed()
    # Check by PR number first — most reliable
    if pr_id and f"pr_{pr_id}" in data:
        match = data[f"pr_{pr_id}"]
        print(f"  Ticket already exists: {match['key']} — skipping creation")
        return {"exists": True, "key": match["key"], "url": match["url"]}
    # Fallback: check by title
    match = data.get(pr_title.lower())
    if match:
        print(f"  Ticket already exists: {match['key']} — skipping creation")
        return {"exists": True, "key": match["key"], "url": match["url"]}
    return {"exists": False}


def create_jira_ticket(title, description, checklist="", risks="", pr_id=None):
    # Check for duplicate first
    existing = ticket_exists(title, pr_id=pr_id)
    if existing["exists"]:
        return {"success": True, "key": existing["key"], "url": existing["url"]}

    # Build full description
    full_description = description
    if checklist:
        full_description += f"\n\nChecklist:\n{checklist}"
    if risks:
        full_description += f"\n\nRisks:\n{risks}"

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": title,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": full_description}]
                }]
            },
            "issuetype": {"name": "Task"},
            "priority": {"name": "High"}
        }
    }

    response = requests.post(
        f"https://{JIRA_DOMAIN}/rest/api/3/issue",
        headers=get_headers(),
        json=payload
    )
    data = response.json()

    if response.status_code == 201:
        ticket_key = data["key"]
        ticket_url = f"https://{JIRA_DOMAIN}/browse/{ticket_key}"
        save_processed(title, ticket_key, ticket_url, pr_id=pr_id)
        print(f"  Jira ticket created: {ticket_key}")
        return {"success": True, "key": ticket_key, "url": ticket_url}
    else:
        print(f"  Jira error: {data}")
        return {"success": False, "error": str(data)}


def add_comment(ticket_key, comment_text):
    payload = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": comment_text}]
            }]
        }
    }
    response = requests.post(
        f"https://{JIRA_DOMAIN}/rest/api/3/issue/{ticket_key}/comment",
        headers=get_headers(),
        json=payload
    )
    if response.status_code == 201:
        print(f"  Comment added to {ticket_key}")
    else:
        print(f"  Comment error: {response.json()}")


def update_ticket_status(ticket_key, target_status="In Progress"):
    r = requests.get(
        f"https://{JIRA_DOMAIN}/rest/api/3/issue/{ticket_key}/transitions",
        headers=get_headers()
    )
    transitions = r.json().get("transitions", [])
    match = next(
        (t for t in transitions if target_status.lower() in t["name"].lower()),
        None
    )
    if match:
        requests.post(
            f"https://{JIRA_DOMAIN}/rest/api/3/issue/{ticket_key}/transitions",
            headers=get_headers(),
            json={"transition": {"id": match["id"]}}
        )
        print(f"  {ticket_key} moved to '{target_status}'")
    else:
        print(f"  Transition '{target_status}' not found")
        print(f"  Available: {[t['name'] for t in transitions]}")


# Test
if __name__ == "__main__":
    result = create_jira_ticket(
        title="Integrate Stripe Payment Gateway",
        description="This PR integrates Stripe as the payment gateway.",
        checklist="- Verify Stripe integration\n- Test refund flow",
        risks="- Refund route has no auth guard",
        pr_id=1
    )
    print(result)

# =============================================================================================================================
# import requests
# import base64
# import os
# import json

# PROCESSED_PRS_FILE = "processed_prs.json"


# def get_auth(email, api_token):
#     credentials = f"{email}:{api_token}"
#     return base64.b64encode(credentials.encode("utf-8")).decode("utf-8")


# def get_headers(email, api_token):
#     return {
#         "Authorization": f"Basic {get_auth(email, api_token)}",
#         "Content-Type": "application/json"
#     }


# def load_processed():
#     if os.path.exists(PROCESSED_PRS_FILE):
#         with open(PROCESSED_PRS_FILE, "r") as f:
#             return json.load(f)
#     return {}


# def save_processed(title, key, url, pr_id=None):
#     data = load_processed()
#     if pr_id:
#         data[f"pr_{pr_id}"] = {"key": key, "url": url}
#     data[title.lower()] = {"key": key, "url": url}
#     with open(PROCESSED_PRS_FILE, "w") as f:
#         json.dump(data, f)


# def ticket_exists(pr_title, pr_id=None):
#     data = load_processed()
#     if pr_id and f"pr_{pr_id}" in data:
#         match = data[f"pr_{pr_id}"]
#         print(f"  Ticket already exists: {match['key']} — skipping creation")
#         return {"exists": True, "key": match["key"], "url": match["url"]}
#     match = data.get(pr_title.lower())
#     if match:
#         print(f"  Ticket already exists: {match['key']} — skipping creation")
#         return {"exists": True, "key": match["key"], "url": match["url"]}
#     return {"exists": False}


# def create_jira_ticket(title, description, checklist="", risks="", pr_id=None,
#                        jira_domain=None, jira_email=None, jira_api_token=None,
#                        jira_project_key="KAN"):
#     # Use passed credentials — no hardcoded fallback
#     if not jira_domain or not jira_email or not jira_api_token:
#         return {"success": False, "error": "Jira credentials not provided"}

#     existing = ticket_exists(title, pr_id=pr_id)
#     if existing["exists"]:
#         return {"success": True, "key": existing["key"], "url": existing["url"]}

#     full_description = description
#     if checklist:
#         full_description += f"\n\nChecklist:\n{checklist}"
#     if risks:
#         full_description += f"\n\nRisks:\n{risks}"

#     payload = {
#         "fields": {
#             "project": {"key": jira_project_key},
#             "summary": title,
#             "description": {
#                 "type": "doc",
#                 "version": 1,
#                 "content": [{
#                     "type": "paragraph",
#                     "content": [{"type": "text", "text": full_description}]
#                 }]
#             },
#             "issuetype": {"name": "Task"},
#             "priority": {"name": "High"}
#         }
#     }

#     response = requests.post(
#         f"https://{jira_domain}/rest/api/3/issue",
#         headers=get_headers(jira_email, jira_api_token),
#         json=payload
#     )
#     data = response.json()

#     if response.status_code == 201:
#         ticket_key = data["key"]
#         ticket_url = f"https://{jira_domain}/browse/{ticket_key}"
#         save_processed(title, ticket_key, ticket_url, pr_id=pr_id)
#         print(f"  Jira ticket created: {ticket_key}")
#         return {"success": True, "key": ticket_key, "url": ticket_url}
#     else:
#         print(f"  Jira error: {data}")
#         return {"success": False, "error": str(data)}


# def add_comment(ticket_key, comment_text, jira_domain=None, jira_email=None, jira_api_token=None):
#     if not jira_domain or not jira_email or not jira_api_token:
#         return
#     payload = {
#         "body": {
#             "type": "doc",
#             "version": 1,
#             "content": [{
#                 "type": "paragraph",
#                 "content": [{"type": "text", "text": comment_text}]
#             }]
#         }
#     }
#     response = requests.post(
#         f"https://{jira_domain}/rest/api/3/issue/{ticket_key}/comment",
#         headers=get_headers(jira_email, jira_api_token),
#         json=payload
#     )
#     if response.status_code == 201:
#         print(f"  Comment added to {ticket_key}")
#     else:
#         print(f"  Comment error: {response.json()}")