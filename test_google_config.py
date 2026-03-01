#!/usr/bin/env python3
"""
Test Google API Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_config():
    """Test the Google API configuration."""
    print("Testing Google API Configuration...")
    print("=" * 40)

    # Test environment variables
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

    print(f"GOOGLE_CLIENT_ID: {'✓ Present' if client_id else '✗ Missing'}")
    if client_id:
        print(
            f"  Value: {client_id[:10]}..."
            if len(client_id) > 10
            else f"  Value: {client_id}"
        )

    print(f"GOOGLE_CLIENT_SECRET: {'✓ Present' if client_secret else '✗ Missing'}")
    if client_secret:
        print(f"  Length: {len(client_secret)} characters")

    print(f"GOOGLE_REDIRECT_URI: {'✓ Present' if redirect_uri else '✗ Missing'}")
    if redirect_uri:
        print(f"  Value: {redirect_uri}")

    # Check if redirect URI matches what we expect
    expected_redirects = ["http://localhost:8080/", "http://localhost:8080/callback"]

    redirect_match = any(
        expected in redirect_uri if redirect_uri else []
        for expected in expected_redirects
    )
    print(f"Redirect URI format: {'✓ Correct' if redirect_match else '⚠ Check format'}")

    print("\nConfiguration Status:")
    if client_id and client_secret and redirect_uri and redirect_match:
        print("✅ All Google API configuration values are set correctly!")
        print("\nTo complete setup:")
        print("1. Run the authentication script: python run_google_auth.py")
        print("2. Complete the OAuth flow in your browser (will use port 8080)")
        print("3. The system will create token.json and drive_token.json files")
        print("4. These files will store your authenticated access")
    else:
        print("❌ Missing or incorrect configuration values")
        print("Please check your .env file and Google Cloud Console settings")


if __name__ == "__main__":
    test_config()
