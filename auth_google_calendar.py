#!/usr/bin/env python3
"""
Simple Google Calendar authentication
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def authenticate_calendar():
    """Authenticate Google Calendar API."""
    print("Setting up Google Calendar authentication...")
    
    scopes = ["https://www.googleapis.com/auth/calendar.readonly"]
    token_filename = "token.json"
    
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
                print("ERROR: GOOGLE_CLIENT_ID and/or GOOGLE_CLIENT_SECRET not found in .env file")
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
    
    print("Google Calendar authentication successful!")
    return True

if __name__ == "__main__":
    authenticate_calendar()