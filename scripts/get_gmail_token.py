#!/usr/bin/env python3
"""
Gmail OAuth Token Generator

Generates an OAuth URL for Gmail API access.
Run this, paste the URL in your browser, authorize, and paste back the code.
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

# Gmail scopes needed
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

CREDENTIALS_PATH = '/root/.config/gmail/credentials.json'
TOKEN_PATH = '/root/.config/gmail/token.pickle'


def main():
    print("=" * 60)
    print("Gmail OAuth Token Generator")
    print("=" * 60)

    if not os.path.exists(CREDENTIALS_PATH):
        print(f"ERROR: Credentials file not found at {CREDENTIALS_PATH}")
        return

    # Check if token already exists
    if os.path.exists(TOKEN_PATH):
        print(f"Token already exists at {TOKEN_PATH}")
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return

    # Create the flow using console mode
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_PATH,
        SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'
    )

    # Generate authorization URL
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    print("\n" + "=" * 60)
    print("STEP 1: Open this URL in your browser:")
    print("=" * 60)
    print(f"\n{auth_url}\n")
    print("=" * 60)
    print("STEP 2: Authorize and paste the code below")
    print("=" * 60)

    code = input("\nEnter the authorization code: ").strip()

    if not code:
        print("No code entered. Cancelled.")
        return

    # Exchange code for token
    try:
        flow.fetch_token(code=code)
        creds = flow.credentials

        # Save the token
        with open(TOKEN_PATH, 'wb') as token_file:
            pickle.dump(creds, token_file)

        print("\n" + "=" * 60)
        print("SUCCESS! Token saved to:", TOKEN_PATH)
        print("=" * 60)
        print("\nYou can now run the Gmail monitor worker:")
        print("  python3 /root/flourisha/00_AI_Brain/scripts/gmail_monitor_worker.py")

    except Exception as e:
        print(f"\nERROR: Failed to get token: {e}")
        print("\nMake sure:")
        print("1. Gmail API is enabled in Google Cloud Console")
        print("2. The authorization code is correct")
        print("3. The OAuth consent screen is configured")


if __name__ == "__main__":
    main()
