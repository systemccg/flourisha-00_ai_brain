#!/usr/bin/env python3
"""
YouTube Multi-Channel Manager
Manages multiple YouTube channel tokens for brand account support.

Usage:
    # List saved channels
    python youtube_channel_manager.py list

    # Authenticate a new channel (opens browser)
    python youtube_channel_manager.py auth

    # Show playlists for a channel
    python youtube_channel_manager.py playlists <channel_name>

    # Set default channel
    python youtube_channel_manager.py default <channel_name>
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Third-party imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)


class YouTubeChannelManager:
    """Manages multiple YouTube channel authentications."""

    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

    def __init__(self, credentials_dir: Optional[Path] = None):
        """Initialize the channel manager."""
        # Use environment variable if provided, otherwise use default
        env_creds_path = os.getenv('YOUTUBE_OAUTH_CREDENTIALS_PATH')
        env_tokens_dir = os.getenv('YOUTUBE_TOKENS_DIR')

        self.credentials_dir = (
            Path(env_creds_path).parent if env_creds_path
            else credentials_dir or Path('/root/flourisha/00_AI_Brain/credentials')
        )
        self.oauth_file = Path(env_creds_path) if env_creds_path else self.credentials_dir / 'youtube_oauth.json'
        self.channels_file = self.credentials_dir / 'youtube_channels.json'
        self.tokens_dir = Path(env_tokens_dir) if env_tokens_dir else self.credentials_dir / 'youtube_tokens'

        # Ensure directories exist
        self.tokens_dir.mkdir(parents=True, exist_ok=True)

        # Load channel registry
        self.channels = self._load_channels()

    def _load_channels(self) -> Dict[str, Any]:
        """Load the channel registry."""
        if self.channels_file.exists():
            with open(self.channels_file, 'r') as f:
                return json.load(f)
        return {
            "default": None,
            "channels": {}
        }

    def _save_channels(self):
        """Save the channel registry."""
        with open(self.channels_file, 'w') as f:
            json.dump(self.channels, f, indent=2)

    def _get_token_path(self, channel_name: str) -> Path:
        """Get the token file path for a channel."""
        safe_name = "".join(c if c.isalnum() or c in '-_' else '_' for c in channel_name.lower())
        return self.tokens_dir / f"token_{safe_name}.json"

    def authenticate_channel(self, force_new: bool = True) -> Dict[str, Any]:
        """
        Authenticate a YouTube channel.

        Args:
            force_new: Force re-authentication even if token exists

        Returns:
            Channel info dict with name, id, and token path
        """
        if not self.oauth_file.exists():
            print(f"Error: OAuth credentials not found at {self.oauth_file}")
            print("\nSetup Instructions:")
            print("1. Go to https://console.cloud.google.com/")
            print("2. Enable YouTube Data API v3")
            print("3. Create OAuth 2.0 credentials (Desktop app)")
            print("4. Download and save as youtube_oauth.json")
            sys.exit(1)

        # Use OAuth Playground for headless server authentication
        # Load client config
        with open(self.oauth_file, 'r') as f:
            client_config = json.load(f)

        client_id = client_config['installed']['client_id']
        client_secret = client_config['installed']['client_secret']
        redirect_uri = "https://developers.google.com/oauthplayground"

        # Build auth URL with prompt=consent to force channel selection
        auth_url = (
            "https://accounts.google.com/o/oauth2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            "response_type=code&"
            "scope=https://www.googleapis.com/auth/youtube.readonly&"
            "access_type=offline&"
            "prompt=consent"
        )

        print("\n🔐 YouTube Authentication via OAuth Playground")
        print("=" * 60)
        print("\n1. Open this URL in your browser:\n")
        print(f"   {auth_url}\n")
        print("2. Sign in and SELECT THE CHANNEL you want to use")
        print("3. You'll be redirected to OAuth Playground")
        print("4. Click 'Exchange authorization code for tokens'")
        print("5. Copy the 'Refresh token' value and paste it below\n")

        refresh_token = input("Enter the refresh token: ").strip()

        # Exchange refresh token for access token
        import urllib.request
        import urllib.parse

        token_url = "https://oauth2.googleapis.com/token"
        data = urllib.parse.urlencode({
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }).encode()

        req = urllib.request.Request(token_url, data=data, method='POST')
        with urllib.request.urlopen(req) as response:
            token_data = json.loads(response.read().decode())

        # Create credentials object
        creds = Credentials(
            token=token_data['access_token'],
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=self.SCOPES
        )

        # Build YouTube client to get channel info
        youtube = build('youtube', 'v3', credentials=creds)

        # Get the authenticated channel
        request = youtube.channels().list(
            part='snippet,statistics',
            mine=True
        )
        response = request.execute()

        if not response.get('items'):
            print("Error: No channel found for authenticated user")
            sys.exit(1)

        channel = response['items'][0]
        channel_id = channel['id']
        channel_name = channel['snippet']['title']

        # Save token
        token_path = self._get_token_path(channel_name)
        with open(token_path, 'w') as f:
            f.write(creds.to_json())

        # Update registry
        channel_info = {
            "id": channel_id,
            "name": channel_name,
            "token_file": str(token_path),
            "authenticated_at": datetime.now().isoformat(),
            "subscribers": channel['statistics'].get('subscriberCount', 'hidden'),
            "description": channel['snippet'].get('description', '')[:200]
        }

        self.channels["channels"][channel_name] = channel_info

        # Set as default if first channel
        if self.channels["default"] is None:
            self.channels["default"] = channel_name

        self._save_channels()

        print(f"\n✅ Authenticated: {channel_name}")
        print(f"   Channel ID: {channel_id}")
        print(f"   Token saved to: {token_path}")

        return channel_info

    def list_channels(self) -> List[Dict[str, Any]]:
        """List all authenticated channels."""
        channels = []
        for name, info in self.channels.get("channels", {}).items():
            # Check if token is still valid
            token_path = Path(info['token_file'])
            token_valid = token_path.exists()

            channels.append({
                "name": name,
                "id": info['id'],
                "is_default": name == self.channels.get("default"),
                "token_valid": token_valid,
                "authenticated_at": info.get('authenticated_at', 'unknown')
            })
        return channels

    def set_default(self, channel_name: str) -> bool:
        """Set the default channel."""
        if channel_name not in self.channels.get("channels", {}):
            print(f"Error: Channel '{channel_name}' not found")
            return False

        self.channels["default"] = channel_name
        self._save_channels()
        print(f"✅ Default channel set to: {channel_name}")
        return True

    def get_client(self, channel_name: Optional[str] = None):
        """
        Get an authenticated YouTube client for a channel.

        Args:
            channel_name: Channel name (uses default if not specified)

        Returns:
            Authenticated YouTube API client
        """
        if channel_name is None:
            channel_name = self.channels.get("default")

        if channel_name is None:
            raise ValueError("No channel specified and no default set. Run 'auth' first.")

        if channel_name not in self.channels.get("channels", {}):
            raise ValueError(f"Channel '{channel_name}' not found. Run 'auth' to add it.")

        channel_info = self.channels["channels"][channel_name]
        token_path = Path(channel_info['token_file'])

        if not token_path.exists():
            raise ValueError(f"Token file not found for '{channel_name}'. Run 'auth' again.")

        creds = Credentials.from_authorized_user_file(str(token_path), self.SCOPES)

        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'w') as f:
                f.write(creds.to_json())

        return build('youtube', 'v3', credentials=creds)

    def get_playlists(self, channel_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all playlists for a channel.

        Args:
            channel_name: Channel name (uses default if not specified)

        Returns:
            List of playlist dicts
        """
        youtube = self.get_client(channel_name)

        playlists = []
        request = youtube.playlists().list(
            part='snippet,contentDetails',
            mine=True,
            maxResults=50
        )

        while request:
            response = request.execute()
            for pl in response.get('items', []):
                playlists.append({
                    'id': pl['id'],
                    'title': pl['snippet']['title'],
                    'description': pl['snippet'].get('description', '')[:200],
                    'video_count': pl['contentDetails']['itemCount'],
                    'published_at': pl['snippet']['publishedAt']
                })
            request = youtube.playlists().list_next(request, response)

        return playlists

    def get_playlist_videos(
        self,
        playlist_id: str,
        channel_name: Optional[str] = None,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get videos from a playlist.

        Args:
            playlist_id: YouTube playlist ID
            channel_name: Channel name (uses default if not specified)
            max_results: Maximum videos to return

        Returns:
            List of video dicts
        """
        youtube = self.get_client(channel_name)

        videos = []
        request = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=playlist_id,
            maxResults=min(50, max_results)
        )

        while request and len(videos) < max_results:
            response = request.execute()
            for item in response.get('items', []):
                videos.append({
                    'video_id': item['contentDetails']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet'].get('description', '')[:500],
                    'channel_title': item['snippet'].get('channelTitle', ''),
                    'published_at': item['snippet']['publishedAt'],
                    'position': item['snippet']['position']
                })
            request = youtube.playlistItems().list_next(request, response)

        return videos[:max_results]


def main():
    """CLI interface for YouTube Channel Manager."""
    parser = argparse.ArgumentParser(
        description='YouTube Multi-Channel Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                    # List all authenticated channels
  %(prog)s auth                    # Authenticate a new channel
  %(prog)s playlists               # Show playlists for default channel
  %(prog)s playlists "LeadingAI"   # Show playlists for specific channel
  %(prog)s default "LeadingAI"     # Set default channel
  %(prog)s videos PLxxx            # List videos in a playlist
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    subparsers.add_parser('list', help='List authenticated channels')

    # Auth command
    subparsers.add_parser('auth', help='Authenticate a new channel')

    # Playlists command
    pl_parser = subparsers.add_parser('playlists', help='List playlists')
    pl_parser.add_argument('channel', nargs='?', help='Channel name (optional)')

    # Default command
    def_parser = subparsers.add_parser('default', help='Set default channel')
    def_parser.add_argument('channel', help='Channel name')

    # Videos command
    vid_parser = subparsers.add_parser('videos', help='List videos in a playlist')
    vid_parser.add_argument('playlist_id', help='Playlist ID')
    vid_parser.add_argument('--channel', '-c', help='Channel name (optional)')
    vid_parser.add_argument('--max', '-m', type=int, default=20, help='Max videos')

    args = parser.parse_args()

    manager = YouTubeChannelManager()

    if args.command == 'list':
        channels = manager.list_channels()
        if not channels:
            print("No channels authenticated yet. Run 'auth' to add one.")
            return

        print(f"\n{'Channel':<30} {'ID':<26} {'Default':<8} {'Status'}")
        print("-" * 80)
        for ch in channels:
            default = "✓" if ch['is_default'] else ""
            status = "✓ Valid" if ch['token_valid'] else "✗ Invalid"
            print(f"{ch['name']:<30} {ch['id']:<26} {default:<8} {status}")
        print()

    elif args.command == 'auth':
        manager.authenticate_channel()

    elif args.command == 'playlists':
        try:
            channel = args.channel if hasattr(args, 'channel') else None
            playlists = manager.get_playlists(channel)

            channel_name = channel or manager.channels.get('default', 'Unknown')
            print(f"\n📺 Playlists for: {channel_name}")
            print(f"\n{'#':<4} {'Playlist Name':<50} {'Videos':<8} {'ID'}")
            print("-" * 95)

            for i, pl in enumerate(playlists, 1):
                title = pl['title'][:48]
                print(f"{i:<4} {title:<50} {pl['video_count']:<8} {pl['id']}")

            print(f"\nTotal: {len(playlists)} playlists")
        except ValueError as e:
            print(f"Error: {e}")

    elif args.command == 'default':
        manager.set_default(args.channel)

    elif args.command == 'videos':
        try:
            videos = manager.get_playlist_videos(
                args.playlist_id,
                channel_name=args.channel,
                max_results=args.max
            )

            print(f"\n📹 Videos in playlist (showing {len(videos)}):\n")
            for i, v in enumerate(videos, 1):
                title = v['title'][:60]
                print(f"{i:>3}. {title}")
                print(f"     ID: {v['video_id']} | Channel: {v['channel_title'][:30]}")
        except ValueError as e:
            print(f"Error: {e}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
