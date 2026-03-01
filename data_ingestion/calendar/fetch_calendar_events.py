#!/usr/bin/env python3
"""
Fetch calendar events using the Google Calendar API and store them in a structured format.
"""

import os
import json
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Google Calendar API scopes
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_google_calendar_service():
    """
    Authenticate and return the Google Calendar service.
    """
    creds = None

    # Check if token.json exists (stores user's access and refresh tokens)
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                },
                SCOPES,
            )
            creds = flow.run_local_server(port=8080)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service


def fetch_events(service, max_results=10):
    """
    Fetch events from the primary calendar.
    """
    # Call the Calendar API
    now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming {} events".format(max_results))
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
    else:
        print("Upcoming events:")
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    return events


def save_events_to_json(events, filename="calendar_events.json"):
    """
    Save events to a JSON file.
    """
    with open(filename, "w") as f:
        json.dump(events, f, indent=2)
    print(f"Events saved to {filename}")


def main():
    """
    Main function to fetch and save calendar events.
    """
    try:
        service = get_google_calendar_service()
        events = fetch_events(service)
        save_events_to_json(events)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
