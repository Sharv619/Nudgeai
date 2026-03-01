import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class GoogleAuth:
    """Handle Google API authentication using credentials from .env"""

    @staticmethod
    def get_credentials_from_env(scopes: List[str]):
        """
        Get credentials from environment variables.
        This method assumes credentials are stored in the environment
        or in the .env file for local development.
        """
        # For hackathon, we'll use the credentials from .env
        # In production, this would use OAuth2 flow
        google_token = os.getenv("GOOGLE_TOKEN")
        if not google_token:
            raise ValueError("GOOGLE_TOKEN not found in environment")

        return google_token, scopes

    @staticmethod
    def get_service_account_info():
        """Get service account information if available"""
        service_account_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if service_account_file and os.path.exists(service_account_file):
            return service_account_file
        return None
