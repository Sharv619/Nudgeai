# Google API Setup Guide

## Prerequisites

1. **Google Cloud Project**: You need a Google Cloud project with the following APIs enabled:
   - Google Calendar API
   - Google Drive API
   - Google Fit API (optional for future use)

2. **OAuth 2.0 Credentials**: Create OAuth 2.0 credentials for desktop application

## Step-by-Step Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the required APIs:
   - Navigate to "APIs & Services" > "Library"
   - Search for and enable:
     - "Google Calendar API"
     - "Google Drive API"

### 2. Create Desktop Application Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. For "Application type", select "Desktop application"
4. For "Name", enter "NudgeAI" or your preferred name
5. **Important**: Add the redirect URI to "Authorized redirect URIs":
   - `http://localhost:8080/`
   - `http://localhost:8080/callback`
   - `urn:ietf:wg:oauth:2.0:oob` (for command-line tools)

### 3. Download Credentials
1. Download the JSON file for your OAuth 2.0 credentials
2. Rename it to `credentials.json`
3. Place it in your project root directory

### 4. Update .env File
Make sure your `.env` file contains:
```
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/
```

### 5. Install Required Libraries
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Running the Applications

### For Calendar Sync:
```bash
cd data_ingestion/calendar/
python fetch_calendar_events.py
```

### For Drive Sync:
```bash
cd data_ingestion/drive/
python fetch_drive_documents.py
```

## Troubleshooting Common Issues

### Redirect URI Mismatch Error
**Problem**: `Error 400: redirect_uri_mismatch`
**Cause**: The redirect URI used in the application doesn't match the ones registered in Google Cloud Console
**Solution**: 
1. Ensure the port in your code matches the registered URIs
2. In this project, we use port 8000, so make sure you have registered:
   - `http://localhost:8000/`
   - `http://localhost:8000/callback`

### Token Expiration
- The application stores user credentials in `token.json`
- If you encounter authentication errors, delete `token.json` and re-run the application

### Scope Permissions
- The application requests minimal scopes needed for functionality
- If you need additional data, modify the SCOPES in the respective files

## Security Considerations

1. **Never commit** your `credentials.json` or `.env` files to version control
2. The `token.json` file contains user access tokens - keep it secure
3. Always use environment variables for sensitive information

## OAuth 2.0 Flow Explanation

The application uses the OAuth 2.0 flow for installed applications:
1. When no credentials exist, it opens a browser for user authorization
2. User grants permission to access their data
3. Application receives authorization code
4. Authorization code is exchanged for access and refresh tokens
5. Tokens are stored in `token.json` for subsequent use

This flow ensures your application can access Google services on behalf of the user without storing passwords.