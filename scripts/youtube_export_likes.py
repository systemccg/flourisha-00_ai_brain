#!/usr/bin/env python3
"""
YouTube Liked Videos Export Script
Exports all liked videos from your YouTube account to JSON and CSV formats.
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load environment variables
load_dotenv('/root/flourisha/00_AI_Brain/.env')

# YouTube API scopes
# Using force-ssl to access brand accounts and managed channels
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# Paths - use environment variables with fallbacks
AI_BRAIN = Path('/root/flourisha/00_AI_Brain')
YOUTUBE_OAUTH_PATH = os.getenv('YOUTUBE_OAUTH_CREDENTIALS_PATH', AI_BRAIN / 'credentials' / 'youtube_oauth.json')
YOUTUBE_TOKENS_DIR = os.getenv('YOUTUBE_TOKENS_DIR', AI_BRAIN / 'credentials' / 'youtube_tokens')
TOKEN_FILE = Path(YOUTUBE_TOKENS_DIR) / 'youtube_token.json'
OUTPUT_DIR = AI_BRAIN / 'outputs' / 'youtube_exports'
CREDENTIALS_FILE = Path(YOUTUBE_OAUTH_PATH)


def get_authenticated_service():
    """Authenticate and return YouTube API service."""
    creds = None

    # Load existing token if available
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # If no valid credentials, do the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing access token...")
            creds.refresh(Request())
        else:
            print("Starting OAuth flow...")
            print("\n" + "="*60)
            print("MANUAL AUTHORIZATION REQUIRED")
            print("="*60)
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES)

            # Generate the authorization URL
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            auth_url, _ = flow.authorization_url(prompt='consent')

            print(f"\n1. Open this URL in your browser:\n\n{auth_url}\n")
            print("2. Authorize the application")
            print("3. Copy the authorization code")
            print("="*60)

            code = input("\nEnter the authorization code: ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials

        # Save the credentials for next time
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)


def list_channels(youtube):
    """List all channels available to the authenticated user, including brand accounts."""
    all_channels = []

    # Get channels owned by authenticated user
    try:
        request = youtube.channels().list(
            part='snippet,contentDetails',
            mine=True,
            maxResults=50
        )
        response = request.execute()
        all_channels.extend(response.get('items', []))
    except Exception as e:
        print(f"Warning: Could not fetch owned channels: {e}")

    # Get channels managed by authenticated user (includes brand accounts)
    try:
        request = youtube.channels().list(
            part='snippet,contentDetails',
            managedByMe=True,
            maxResults=50
        )
        response = request.execute()
        managed_channels = response.get('items', [])

        # Add managed channels that aren't already in the list
        existing_ids = {ch['id'] for ch in all_channels}
        for channel in managed_channels:
            if channel['id'] not in existing_ids:
                all_channels.append(channel)
    except Exception as e:
        print(f"Warning: Could not fetch managed channels: {e}")

    return all_channels


def select_channel(youtube):
    """Let user select which channel to use."""
    channels = list_channels(youtube)

    if not channels:
        print("❌ No channels found for this account!")
        return None

    print("\n" + "="*60)
    print("AVAILABLE YOUTUBE CHANNELS")
    print("="*60)

    for idx, channel in enumerate(channels, 1):
        title = channel['snippet']['title']
        channel_id = channel['id']
        custom_url = channel['snippet'].get('customUrl', 'N/A')
        print(f"\n{idx}. {title}")
        print(f"   Channel ID: {channel_id}")
        print(f"   Custom URL: {custom_url}")

    print(f"\n{len(channels) + 1}. Enter custom Channel ID manually")
    print("="*60)

    # If only one channel, ask user if they want to use it or enter custom
    if len(channels) == 1:
        use_default = input(f"\nUse '{channels[0]['snippet']['title']}' or enter custom Channel ID? (y/custom): ").strip().lower()
        if use_default == 'y' or use_default == '':
            print(f"✅ Using: {channels[0]['snippet']['title']}")
            return channels[0]['id']
        else:
            custom_id = input("\nEnter Channel ID (e.g., UCtPFDR0Xz9g2gYQhDplLG7w): ").strip()
            if custom_id:
                print(f"✅ Using custom Channel ID: {custom_id}")
                return custom_id
            return channels[0]['id']

    # Let user select
    while True:
        try:
            choice = input(f"\nSelect channel (1-{len(channels) + 1}): ").strip()
            idx = int(choice) - 1

            if idx == len(channels):  # Custom ID option
                custom_id = input("\nEnter Channel ID: ").strip()
                if custom_id:
                    print(f"\n✅ Using custom Channel ID: {custom_id}")
                    return custom_id
                continue

            if 0 <= idx < len(channels):
                selected = channels[idx]
                print(f"\n✅ Selected: {selected['snippet']['title']}")
                return selected['id']
            else:
                print(f"Please enter a number between 1 and {len(channels) + 1}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nCancelled by user")
            return None


def get_liked_videos(youtube, channel_id=None):
    """Fetch all liked videos from YouTube."""
    liked_videos = []
    next_page_token = None

    print("\nFetching liked videos...")

    while True:
        # Request liked videos
        # Note: myRating='like' gets likes for the authenticated user
        # YouTube API doesn't directly support getting likes per-channel
        # but the user context is tied to the selected channel
        request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            myRating='like',
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        # Process each video
        for item in response.get('items', []):
            video_data = {
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'channel_id': item['snippet']['channelId'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'url': f"https://www.youtube.com/watch?v={item['id']}",
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'duration': item['contentDetails']['duration'],
                'view_count': item['statistics'].get('viewCount', 0),
                'like_count': item['statistics'].get('likeCount', 0),
                'comment_count': item['statistics'].get('commentCount', 0),
            }
            liked_videos.append(video_data)

        print(f"Fetched {len(liked_videos)} videos so far...")

        # Check if there are more pages
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return liked_videos


def export_to_json(videos, output_file):
    """Export videos to JSON format."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    print(f"✅ Exported to JSON: {output_file}")


def export_to_csv(videos, output_file):
    """Export videos to CSV format."""
    if not videos:
        print("No videos to export")
        return

    fieldnames = videos[0].keys()

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(videos)

    print(f"✅ Exported to CSV: {output_file}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("YouTube Liked Videos Export")
    print("=" * 60)

    # Authenticate
    youtube = get_authenticated_service()

    # Select channel
    channel_id = select_channel(youtube)
    if not channel_id:
        print("\n❌ No channel selected. Exiting.")
        return

    # Fetch liked videos
    liked_videos = get_liked_videos(youtube, channel_id)

    if not liked_videos:
        print("No liked videos found!")
        return

    print(f"\n✅ Total liked videos: {len(liked_videos)}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_filename = f"youtube_liked_videos_{timestamp}"

    # Export to both formats
    json_file = OUTPUT_DIR / f"{base_filename}.json"
    csv_file = OUTPUT_DIR / f"{base_filename}.csv"

    export_to_json(liked_videos, json_file)
    export_to_csv(liked_videos, csv_file)

    print("\n" + "=" * 60)
    print("Export Complete!")
    print("=" * 60)
    print(f"📁 Files saved to: {OUTPUT_DIR}")
    print(f"   - {json_file.name}")
    print(f"   - {csv_file.name}")


if __name__ == '__main__':
    main()
