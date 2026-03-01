#!/usr/bin/env python3
"""
Fetch Google Drive documents using the Google Drive API and store them in a structured format.
"""

import os
import json
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Google Drive API scopes
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_google_drive_service():
    """
    Authenticate and return the Google Drive service.
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
            if not client_id or not client_secret:
                raise ValueError(
                    "Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in .env"
                )

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
            creds = flow.run_local_server(port=8000)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("drive", "v3", credentials=creds)
    return service


def fetch_documents(service, max_results=10):
    """
    Fetch recent documents from Google Drive.
    """
    # Define query to get recent Google Docs
    query = "mimeType='application/vnd.google-apps.document' and trashed=false"

    print(f"Getting the {max_results} most recently modified Google Docs")

    # Call the Drive API
    results = (
        service.files()
        .list(
            q=query,
            pageSize=max_results,
            fields="files(id, name, mimeType, modifiedTime, owners, createdTime, lastModifyingUser)",
            orderBy="modifiedTime desc",
        )
        .execute()
    )

    documents = results.get("files", [])

    if not documents:
        print("No Google Docs found.")
    else:
        print("Recent Google Docs:")
        for doc in documents:
            print(f"{doc['name']} - Modified: {doc['modifiedTime']}")

    return documents


def save_documents_to_json(documents, filename="drive_documents.json"):
    """
    Save documents to a JSON file.
    """
    with open(filename, "w") as f:
        json.dump(documents, f, indent=2)
    print(f"Documents saved to {filename}")


def format_documents_for_rag(documents):
    """
    Format documents for RAG system with consistent structure.
    """
    formatted_docs = []
    for doc in documents:
        formatted_doc = {
            "id": f"doc_{doc['id']}",
            "text": f"Document: {doc['name']} (last modified: {doc['modifiedTime']})",
            "metadata": {
                "type": "document",
                "name": doc["name"],
                "id": doc["id"],
                "modifiedTime": doc["modifiedTime"],
                "createdTime": doc.get("createdTime"),
                "owners": doc.get("owners", []),
                "lastModifyingUser": doc.get("lastModifyingUser", {}),
                "mimeType": doc["mimeType"],
            },
        }
        formatted_docs.append(formatted_doc)

    return formatted_docs


def main():
    """
    Main function to fetch and save drive documents.
    """
    try:
        service = get_google_drive_service()
        documents = fetch_documents(service)
        save_documents_to_json(documents)

        # Format for RAG system
        rag_formatted = format_documents_for_rag(documents)
        with open("drive_documents_rag.json", "w") as f:
            json.dump(rag_formatted, f, indent=2)
        print(f"Formatted {len(rag_formatted)} documents for RAG system")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
