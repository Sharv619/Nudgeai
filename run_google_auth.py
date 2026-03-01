#!/usr/bin/env python3
"""
Quick Google API Authentication Setup for NudgeAI
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


def authenticate_service(service_name, scopes, token_filename):
    """Authenticate a Google service."""
    print(f"Setting up {service_name} authentication...")

    creds = None

    # Check if token file exists
    if os.path.exists(token_filename):
        creds = Credentials.from_authorized_user_file(token_filename, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use the credentials from environment
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

            if not client_id or not client_secret:
                print(
                    f"ERROR: GOOGLE_CLIENT_ID and/or GOOGLE_CLIENT_SECRET not found in .env file"
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
                            "http://localhost:8080/",
                            "http://localhost:8080/callback",
                            "urn:ietf:wg:oauth:2.0:oob",
                        ],
                    }
                },
                scopes,
            )

            # Use port 8080 to match the redirect URI in .env
            creds = flow.run_local_server(port=8080)

        # Save the credentials for the next run
        with open(token_filename, "w") as token:
            token.write(creds.to_json())

    print(f"{service_name} authentication successful!")
    return True


def main():
    """Main function to authenticate Google services."""
    print("NudgeAI - Quick Google API Authentication")
    print("=" * 45)

    # Calendar API setup
    calendar_scopes = ["https://www.googleapis.com/auth/calendar.readonly"]
    calendar_success = authenticate_service(
        "Google Calendar", calendar_scopes, "token.json"
    )

    # Drive API setup
    drive_scopes = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
    drive_success = authenticate_service(
        "Google Drive", drive_scopes, "drive_token.json"
    )

    if calendar_success and drive_success:
        print("\n🎉 Authentication completed successfully!")
        print("Token files created:")
        print("- token.json (for calendar access)")
        print("- drive_token.json (for drive access)")
        print("\nYou can now use Google API features in NudgeAI!")
    else:
        print("\n❌ Authentication failed!")
        print("Please check your Google Cloud Console settings.")


if __name__ == "__main__":
    main()
