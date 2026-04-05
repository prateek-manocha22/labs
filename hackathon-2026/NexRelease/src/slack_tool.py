import requests


def post_slack_message(message, slack_token=None, channel="releases"):
    if not slack_token:
        print("Slack error: no token provided")
        return {"success": False, "error": "no token"}

    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {slack_token}",
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