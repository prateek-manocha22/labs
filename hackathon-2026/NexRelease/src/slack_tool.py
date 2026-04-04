import requests
import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
DEFAULT_CHANNEL = "releases"

def post_slack_message(message, channel=DEFAULT_CHANNEL):
    url = "https://slack.com/api/chat.postMessage"
    
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "channel": channel,
        "text": message,
        "mrkdwn": True
    }
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    
    if data.get("ok"):
        print(f"Slack message posted to {channel}")
        return {"success": True}
    else:
        print(f"Slack error: {data.get('error')}")
        return {"success": False, "error": data.get("error")}


# Test it
if __name__ == "__main__":
    result = post_slack_message(
        message="*Test message* from release agent. If you see this, Slack is working ✅"
    )
    print(result)
