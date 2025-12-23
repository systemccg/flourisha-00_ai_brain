"""
YouTube Service
Integration with YouTube Data API v3
"""
import os
from typing import Optional, Dict, Any, List
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

load_dotenv('/root/.claude/.env')


class YouTubeService:
    """YouTube Data API integration"""

    def __init__(self):
        """Initialize YouTube service"""
        # Note: YouTube credentials should be per-user OAuth tokens
        # For now, we'll use the credentials from .env for testing
        self.credentials_path = "/root/flourisha/00_AI_Brain/credentials/youtube_oauth.json"

    def _get_youtube_client(self, access_token: Optional[str] = None):
        """
        Get YouTube API client

        In production, this should use user's OAuth access token.
        For now, using API key for read-only operations.
        """
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")

        return build('youtube', 'v3', developerKey=api_key)

    async def get_playlist_items(
        self,
        playlist_id: str,
        max_results: int = 50,
        access_token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get videos from a playlist

        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum number of videos to retrieve
            access_token: User's OAuth access token (optional)

        Returns:
            List of video items with metadata
        """
        youtube = self._get_youtube_client(access_token)

        videos = []
        next_page_token = None

        while len(videos) < max_results:
            request = youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            )

            response = request.execute()

            for item in response.get('items', []):
                video_data = {
                    'video_id': item['contentDetails']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'channel_id': item['snippet']['channelId'],
                    'channel_title': item['snippet']['channelTitle'],
                    'thumbnails': item['snippet']['thumbnails']
                }
                videos.append(video_data)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return videos

    async def get_video_metadata(
        self,
        video_id: str,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get video metadata

        Args:
            video_id: YouTube video ID
            access_token: User's OAuth access token (optional)

        Returns:
            Video metadata
        """
        youtube = self._get_youtube_client(access_token)

        request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        )

        response = request.execute()

        if not response.get('items'):
            raise ValueError(f"Video not found: {video_id}")

        item = response['items'][0]

        return {
            'video_id': video_id,
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'published_at': item['snippet']['publishedAt'],
            'channel_id': item['snippet']['channelId'],
            'channel_title': item['snippet']['channelTitle'],
            'duration': item['contentDetails']['duration'],
            'view_count': item['statistics'].get('viewCount'),
            'like_count': item['statistics'].get('likeCount'),
            'comment_count': item['statistics'].get('commentCount'),
            'thumbnails': item['snippet']['thumbnails'],
            'tags': item['snippet'].get('tags', [])
        }

    async def get_video_transcript(
        self,
        video_id: str,
        languages: List[str] = ['en', 'en-US']
    ) -> Optional[str]:
        """
        Get video transcript using youtube-transcript-api

        Args:
            video_id: YouTube video ID
            languages: Preferred languages (in order)

        Returns:
            Full transcript as string, or None if not available
        """
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=languages
            )

            # Combine all transcript segments
            full_transcript = ' '.join([item['text'] for item in transcript_list])
            return full_transcript

        except Exception as e:
            print(f"Could not retrieve transcript for {video_id}: {e}")
            return None

    async def get_channel_videos(
        self,
        channel_id: str,
        max_results: int = 50,
        access_token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent videos from a channel

        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to retrieve
            access_token: User's OAuth access token (optional)

        Returns:
            List of video items
        """
        youtube = self._get_youtube_client(access_token)

        videos = []
        next_page_token = None

        while len(videos) < max_results:
            request = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=min(50, max_results - len(videos)),
                order='date',
                type='video',
                pageToken=next_page_token
            )

            response = request.execute()

            for item in response.get('items', []):
                video_data = {
                    'video_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'channel_id': item['snippet']['channelId'],
                    'channel_title': item['snippet']['channelTitle'],
                    'thumbnails': item['snippet']['thumbnails']
                }
                videos.append(video_data)

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return videos

    async def get_playlist_metadata(
        self,
        playlist_id: str,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get playlist metadata"""
        youtube = self._get_youtube_client(access_token)

        request = youtube.playlists().list(
            part='snippet,contentDetails',
            id=playlist_id
        )

        response = request.execute()

        if not response.get('items'):
            raise ValueError(f"Playlist not found: {playlist_id}")

        item = response['items'][0]

        return {
            'playlist_id': playlist_id,
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'channel_id': item['snippet']['channelId'],
            'channel_title': item['snippet']['channelTitle'],
            'item_count': item['contentDetails']['itemCount'],
            'thumbnails': item['snippet']['thumbnails']
        }


# Singleton instance
youtube_service = YouTubeService()
