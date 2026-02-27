import os
import json
import base64
import datetime

# Google API Libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes required for Gmail and Calendar
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
]

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "config", "credentials.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "config", "token.json")


def _get_credentials():
    """Handles OAuth2 authentication and returns credentials."""
    creds = None
    token_path = os.path.abspath(TOKEN_FILE)
    creds_path = os.path.abspath(CREDENTIALS_FILE)

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(
                    f"credentials.json not found at {creds_path}. "
                    "Please download it from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


class GmailManager:
    def __init__(self):
        try:
            creds = _get_credentials()
            self.gmail_service = build("gmail", "v1", credentials=creds)
            self.calendar_service = build("calendar", "v3", credentials=creds)
            print("[Gmail] Services connected successfully.")
        except FileNotFoundError as e:
            print(f"[Gmail] Setup Needed: {e}")
            self.gmail_service = None
            self.calendar_service = None
        except Exception as e:
            print(f"[Gmail] Init Error: {e}")
            self.gmail_service = None
            self.calendar_service = None

    def _is_ready(self):
        return self.gmail_service is not None and self.calendar_service is not None

    # ─────────────────────────────────────────
    # GMAIL
    # ─────────────────────────────────────────

    def read_unread_emails(self, max_results=5):
        """
        Fetches unread emails from Gmail inbox.
        Returns a list of dicts: {subject, sender, snippet}
        """
        if not self._is_ready():
            return "Gmail is not connected. Please ensure credentials.json is in place."

        try:
            result = self.gmail_service.users().messages().list(
                userId="me",
                labelIds=["INBOX", "UNREAD"],
                maxResults=max_results
            ).execute()

            messages = result.get("messages", [])
            if not messages:
                return "Your inbox is empty — no unread messages."

            emails = []
            for msg in messages:
                detail = self.gmail_service.users().messages().get(
                    userId="me", id=msg["id"], format="metadata",
                    metadataHeaders=["Subject", "From"]
                ).execute()

                headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
                emails.append({
                    "subject": headers.get("Subject", "(No Subject)"),
                    "sender": headers.get("From", "Unknown"),
                    "snippet": detail.get("snippet", "")
                })

            return emails

        except HttpError as e:
            return f"Gmail error: {e}"

    def search_emails(self, query, max_results=5):
        """
        Searches Gmail with a query string.
        Returns a list of matching email summaries.
        """
        if not self._is_ready():
            return "Gmail is not connected."

        try:
            result = self.gmail_service.users().messages().list(
                userId="me", q=query, maxResults=max_results
            ).execute()

            messages = result.get("messages", [])
            if not messages:
                return f'No emails found matching "{query}".'

            emails = []
            for msg in messages:
                detail = self.gmail_service.users().messages().get(
                    userId="me", id=msg["id"], format="metadata",
                    metadataHeaders=["Subject", "From"]
                ).execute()
                headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
                emails.append({
                    "subject": headers.get("Subject", "(No Subject)"),
                    "sender": headers.get("From", "Unknown"),
                    "snippet": detail.get("snippet", "")
                })

            return emails

        except HttpError as e:
            return f"Gmail search error: {e}"

    # ─────────────────────────────────────────
    # GOOGLE CALENDAR
    # ─────────────────────────────────────────

    def get_upcoming_events(self, max_results=5):
        """
        Fetches upcoming calendar events.
        Returns a list of dicts: {title, start, end}
        """
        if not self._is_ready():
            return "Google Calendar is not connected."

        try:
            now = datetime.datetime.utcnow().isoformat() + "Z"
            events_result = self.calendar_service.events().list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            events = events_result.get("items", [])
            if not events:
                return "No upcoming events found."

            parsed = []
            for e in events:
                start = e["start"].get("dateTime", e["start"].get("date"))
                end = e["end"].get("dateTime", e["end"].get("date"))
                parsed.append({
                    "title": e.get("summary", "Untitled Event"),
                    "start": start,
                    "end": end,
                    "location": e.get("location", ""),
                })
            return parsed

        except HttpError as e:
            return f"Calendar error: {e}"

    def create_calendar_event(self, title, start_datetime_str, duration_mins=60, description=""):
        """
        Creates a Google Calendar event.
        start_datetime_str: ISO format string like '2026-02-24T15:00:00'
        """
        if not self._is_ready():
            return "Google Calendar is not connected."

        try:
            start_dt = datetime.datetime.fromisoformat(start_datetime_str)
            end_dt = start_dt + datetime.timedelta(minutes=duration_mins)

            event = {
                "summary": title,
                "description": description or f"Created by J.A.R.V.I.S.",
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": "Asia/Kolkata",
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "Asia/Kolkata",
                },
            }

            created = self.calendar_service.events().insert(
                calendarId="primary", body=event
            ).execute()

            return f"Event created: '{title}' on {start_dt.strftime('%B %d at %I:%M %p')}. Link: {created.get('htmlLink')}"

        except HttpError as e:
            return f"Calendar create error: {e}"
        except ValueError as e:
            return f"Invalid date format provided: {e}"
