#!/usr/bin/env python3
"""
Google API Authentication Setup Script for NudgeAI
This script helps users set up their Google API authentication properly.
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


def setup_calendar_auth():
    """Set up Google Calendar authentication."""
    print("Setting up Google Calendar authentication...")

    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    creds = None

    # Check if token.json exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use the credentials from environment
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

            if not client_id or not client_secret:
                print(
                    "ERROR: GOOGLE_CLIENT_ID and/or GOOGLE_CLIENT_SECRET not found in .env file"
                )
                print("Please add them to your .env file:")
                print("GOOGLE_CLIENT_ID=your_client_id_here")
                print("GOOGLE_CLIENT_SECRET=your_client_secret_here")
                return False

            # Create flow using environment credentials
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [
                            "http://localhost:8000/",
                            "http://localhost:8000/callback",
                            "urn:ietf:wg:oauth:2.0:oob",
                        ],
                    }
                },
                SCOPES,
            )

            # Use port 8000 to match the redirect URI in .env
            creds = flow.run_local_server(port=8000, open_browser=True)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    print("Google Calendar authentication successful!")
    return True


def setup_drive_auth():
    """Set up Google Drive authentication."""
    print("Setting up Google Drive authentication...")

    SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
    creds = None

    # Check if token.json exists
    if os.path.exists("drive_token.json"):
        creds = Credentials.from_authorized_user_file("drive_token.json", SCOPES)
    elif os.path.exists("token.json"):
        # Reuse the same token if it has the right scopes
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        except:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use the credentials from environment
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

            if not client_id or not client_secret:
                print(
                    "ERROR: GOOGLE_CLIENT_ID and/or GOOGLE_CLIENT_SECRET not found in .env file"
                )
                return False

            # Create flow using environment credentials
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [
                            "http://localhost:8000/",
                            "http://localhost:8000/callback",
                            "urn:ietf:wg:oauth:2.0:oob",
                        ],
                    }
                },
                SCOPES,
            )

            # Use port 8000 to match the redirect URI in .env
            creds = flow.run_local_server(port=8000, open_browser=True)

        # Save the credentials for the next run
        with open("drive_token.json", "w") as token:
            token.write(creds.to_json())

    print("Google Drive authentication successful!")
    return True


def main():
    """Main function to set up Google API authentication."""
    print("NudgeAI - Google API Authentication Setup")
    print("=" * 50)

    print("\nThis script will help you set up authentication for Google APIs.")
    print("Make sure you have:")
    print("1. A Google Cloud Project with Calendar and Drive APIs enabled")
    print("2. OAuth 2.0 credentials with redirect URI: http://localhost:8000/")
    print("3. GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file")
    print()

    # Check if .env has the required credentials
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("❌ Error: Missing Google credentials in .env file!")
        print("Please add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to your .env file")
        return

    print(f"✅ Found Google Client ID in .env: {client_id[:10]}...")

    # Ask user which services to set up
    print("\nWhich services would you like to set up?")
    print("1. Calendar only")
    print("2. Drive only")
    print("3. Both Calendar and Drive")

    choice = input("\nEnter your choice (1/2/3) [default 3]: ").strip()
    if not choice:
        choice = "3"

    success = True

    if choice in ["1", "3"]:
        success &= setup_calendar_auth()

    if choice in ["2", "3"]:
        success &= setup_drive_auth()

    if success:
        print("\n🎉 Authentication setup completed successfully!")
        print("You can now use the Google API integration features in NudgeAI.")
        print("\nTokens have been saved to:")
        if choice in ["1", "3"] and os.path.exists("token.json"):
            print("- token.json (for calendar access)")
        if choice in ["2", "3"] and os.path.exists("drive_token.json"):
            print("- drive_token.json (for drive access)")
    else:
        print("\n❌ Authentication setup failed!")
        print("Please check your Google Cloud Console settings and .env file.")


if __name__ == "__main__":
    main()
