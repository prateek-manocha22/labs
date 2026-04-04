import datetime
import random
import os
import json
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def detect_risk_level(risks: str) -> str:
    if not risks:
        return "medium"
    risks_lower = risks.lower()
    high_keywords = [
        "critical", "security", "auth", "payment", "refund",
        "crash", "vulnerability", "breach", "data loss", "urgent",
        "breaking", "production", "no auth", "no guard"
    ]
    low_keywords = [
        "minor", "ui", "cosmetic", "readme", "typo",
        "comment", "style", "formatting", "low risk"
    ]
    for word in high_keywords:
        if word in risks_lower:
            return "high"
    for word in low_keywords:
        if word in risks_lower:
            return "low"
    return "medium"


def get_next_weekday(base_date: datetime.datetime) -> datetime.datetime:
    result = base_date
    while result.weekday() >= 5:
        result += datetime.timedelta(days=1)
    return result


def get_calendar_service():
    """
    Returns an authenticated Google Calendar service.
    Uses saved token if available, otherwise returns None.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    if creds and creds.valid:
        return build("calendar", "v3", credentials=creds)

    return None


def save_token(creds):
    with open(TOKEN_FILE, "wb") as token:
        pickle.dump(creds, token)


def create_calendar_event(meeting_title: str, pr_url: str = "", risks: str = "") -> dict:
    now = datetime.datetime.now()
    risk = detect_risk_level(risks)

    if risk == "high":
        candidate = now + datetime.timedelta(hours=1)
        meeting_day = get_next_weekday(candidate)
    elif risk == "medium":
        candidate = now + datetime.timedelta(days=1)
        meeting_day = get_next_weekday(candidate)
    else:
        candidate = now + datetime.timedelta(days=2)
        meeting_day = get_next_weekday(candidate)

    hour = random.randint(10, 16)
    minute = random.choice([0, 15, 30, 45])

    meeting_datetime = meeting_day.replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )
    end_datetime = meeting_datetime + datetime.timedelta(hours=1)

    meeting_time = meeting_datetime.strftime("%Y-%m-%d %I:%M %p")
    day_label = meeting_datetime.strftime("%A, %B %d")

    risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    risk_urgency = {"high": "URGENT — Same Day", "medium": "Next Working Day", "low": "Scheduled"}

    # Generate Google Calendar pre-fill link as fallback
    from urllib.parse import urlencode
    start_str = meeting_datetime.strftime("%Y%m%dT%H%M%S")
    end_str = end_datetime.strftime("%Y%m%dT%H%M%S")
    cal_params = {
        "action": "TEMPLATE",
        "text": meeting_title,
        "dates": f"{start_str}/{end_str}",
        "details": f"Go/no-go meeting\nRisk: {risk.upper()} — {risk_urgency[risk]}\nPR: {pr_url}",
        "location": "Online"
    }
    cal_link = "https://calendar.google.com/calendar/render?" + urlencode(cal_params)

    # Try real Google Calendar API
    google_event_link = None
    service = get_calendar_service()

    if service:
        try:
            event = {
                "summary": meeting_title,
                "location": "Online",
                "description": f"Go/no-go release review\nRisk Level: {risk.upper()} — {risk_urgency[risk]}\nPR Reference: {pr_url}",
                "start": {
                    "dateTime": meeting_datetime.isoformat(),
                    "timeZone": "Asia/Kolkata"
                },
                "end": {
                    "dateTime": end_datetime.isoformat(),
                    "timeZone": "Asia/Kolkata"
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email",  "minutes": 60},
                        {"method": "popup",  "minutes": 30}
                    ]
                }
            }
            created = service.events().insert(
                calendarId="primary",
                body=event
            ).execute()
            google_event_link = created.get("htmlLink")
            print(f"  ✅ Google Calendar event created: {google_event_link}")
        except Exception as e:
            print(f"  ⚠ Google Calendar API error: {e}")
            print(f"  → Falling back to pre-fill link")

    print(f"📅 Meeting scheduled: {meeting_title}")
    print(f"   Risk Level: {risk_emoji[risk]} {risk.upper()} — {risk_urgency[risk]}")
    print(f"   Day: {day_label}")
    print(f"   Time: {meeting_time}")
    if pr_url:
        print(f"   PR Reference: {pr_url}")

    return {
        "success":            True,
        "title":              meeting_title,
        "time":               meeting_time,
        "day":                day_label,
        "risk":               risk,
        "urgency":            risk_urgency[risk],
        "pr_url":             pr_url,
        "cal_link":           google_event_link or cal_link,
        "google_integrated":  google_event_link is not None,
        "mock":               False
    }