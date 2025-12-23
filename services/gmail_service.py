"""
Gmail API Service
Handles Gmail authentication, message retrieval, and attachment processing
"""

import os
import pickle
import base64
import logging
from typing import List, Dict, Optional, Tuple
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import mimetypes

logger = logging.getLogger(__name__)

# Gmail API scopes
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

SUPPORTED_ATTACHMENT_TYPES = {
    'application/pdf': '.pdf',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/vnd.ms-excel': '.xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
    'text/plain': '.txt',
    'text/csv': '.csv',
    'text/markdown': '.md',
}

MAX_ATTACHMENT_SIZE = 50 * 1024 * 1024  # 50MB max


class GmailService:
    """Gmail API service for authentication and message retrieval"""

    def __init__(self, credentials_path: str = None, token_path: str = None):
        """
        Initialize Gmail service

        Args:
            credentials_path: Path to credentials.json from Google Cloud Console
            token_path: Path to store/retrieve oauth token
        """
        self.credentials_path = credentials_path or os.getenv('GMAIL_CREDENTIALS_PATH', '/root/.config/gmail/credentials.json')
        self.token_path = token_path or os.getenv('GMAIL_TOKEN_PATH', '/root/.config/gmail/token.pickle')
        self.service = None
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure config directory exists"""
        config_dir = os.path.dirname(self.token_path)
        os.makedirs(config_dir, exist_ok=True)

    async def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth 2.0

        Returns:
            True if authenticated successfully, False otherwise
        """
        try:
            creds = None

            # Load existing token if available
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token_file:
                    creds = pickle.load(token_file)

            # Refresh token if expired
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    logger.warning("Token refresh failed, re-authenticating")
                    creds = None

            # Get new credentials if needed
            if not creds or not creds.valid:
                if not os.path.exists(self.credentials_path):
                    logger.error(f"Credentials file not found: {self.credentials_path}")
                    logger.error("Download credentials.json from Google Cloud Console and save to: " + self.credentials_path)
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token for next run
            with open(self.token_path, 'wb') as token_file:
                pickle.dump(creds, token_file)

            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail authentication successful")
            return True

        except Exception as e:
            logger.error(f"Gmail authentication failed: {str(e)}")
            return False

    async def list_messages(
        self,
        label: str = "INBOX",
        query: str = "",
        max_results: int = 10
    ) -> List[Dict]:
        """
        List messages from Gmail

        Args:
            label: Gmail label (e.g., "INBOX", "AI Brain/Inbox")
            query: Gmail search query (e.g., "has:attachment")
            max_results: Maximum number of messages to return

        Returns:
            List of message metadata
        """
        if not self.service:
            logger.error("Gmail service not authenticated")
            return []

        try:
            # Build query
            full_query = f"label:{label}"
            if query:
                full_query += f" {query}"

            results = self.service.users().messages().list(
                userId='me',
                q=full_query,
                maxResults=max_results,
                fields='messages(id,threadId)'
            ).execute()

            return results.get('messages', [])

        except HttpError as error:
            logger.error(f"Gmail list error: {error}")
            return []

    async def get_message(self, message_id: str) -> Optional[Dict]:
        """
        Get full message details

        Args:
            message_id: Gmail message ID

        Returns:
            Full message data or None
        """
        if not self.service:
            logger.error("Gmail service not authenticated")
            return None

        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            return message

        except HttpError as error:
            logger.error(f"Gmail get message error: {error}")
            return None

    async def get_attachments(self, message_id: str) -> List[Dict]:
        """
        Get all attachments from a message

        Args:
            message_id: Gmail message ID

        Returns:
            List of attachments with metadata
        """
        attachments = []
        message = await self.get_message(message_id)

        if not message:
            return attachments

        try:
            payload = message.get('payload', {})
            parts = payload.get('parts', [])

            for part in parts:
                if part.get('filename'):
                    attachment_data = {
                        'message_id': message_id,
                        'attachment_id': part.get('body', {}).get('attachmentId'),
                        'filename': part.get('filename'),
                        'mime_type': part.get('mimeType'),
                        'size': int(part.get('body', {}).get('size', 0))
                    }

                    # Check size limit
                    if attachment_data['size'] > MAX_ATTACHMENT_SIZE:
                        logger.warning(f"Attachment too large: {attachment_data['filename']} ({attachment_data['size']} bytes)")
                        continue

                    # Check supported type
                    if attachment_data['mime_type'] not in SUPPORTED_ATTACHMENT_TYPES:
                        logger.debug(f"Unsupported attachment type: {attachment_data['mime_type']}")
                        continue

                    attachments.append(attachment_data)

        except Exception as e:
            logger.error(f"Error processing attachments: {str(e)}")

        return attachments

    async def download_attachment(
        self,
        message_id: str,
        attachment_id: str,
        filename: str
    ) -> Optional[bytes]:
        """
        Download attachment data

        Args:
            message_id: Gmail message ID
            attachment_id: Attachment ID
            filename: Original filename (for extension detection)

        Returns:
            Attachment bytes or None
        """
        if not self.service:
            logger.error("Gmail service not authenticated")
            return None

        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()

            data = attachment.get('data', '')
            if data:
                return base64.urlsafe_b64decode(data)

            return None

        except HttpError as error:
            logger.error(f"Gmail download error: {error}")
            return None

    async def mark_as_processed(
        self,
        message_id: str,
        processed_label: str = "AI Brain/Processed"
    ) -> bool:
        """
        Mark message as processed by adding a label

        Args:
            message_id: Gmail message ID
            processed_label: Label to add

        Returns:
            True if successful
        """
        if not self.service:
            logger.error("Gmail service not authenticated")
            return False

        try:
            # Try to get or create the label
            labels_result = self.service.users().labels().list(userId='me').execute()
            labels = labels_result.get('labels', [])

            label_id = None
            for label in labels:
                if label['name'] == processed_label:
                    label_id = label['id']
                    break

            # Create label if it doesn't exist
            if not label_id:
                label_body = {
                    'name': processed_label,
                    'labelListVisibility': 'labelShow',
                    'messageLis Visibility': 'show'
                }
                created_label = self.service.users().labels().create(
                    userId='me',
                    body=label_body
                ).execute()
                label_id = created_label['id']

            # Add label to message
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()

            logger.info(f"Marked message {message_id} as processed")
            return True

        except HttpError as error:
            logger.error(f"Gmail mark processed error: {error}")
            return False

    async def get_message_subject(self, message_id: str) -> Optional[str]:
        """
        Get message subject

        Args:
            message_id: Gmail message ID

        Returns:
            Subject line or None
        """
        message = await self.get_message(message_id)
        if not message:
            return None

        try:
            headers = message.get('payload', {}).get('headers', [])
            for header in headers:
                if header.get('name') == 'Subject':
                    return header.get('value')
        except Exception as e:
            logger.error(f"Error getting subject: {str(e)}")

        return None

    async def get_message_sender(self, message_id: str) -> Optional[str]:
        """
        Get message sender email

        Args:
            message_id: Gmail message ID

        Returns:
            Sender email or None
        """
        message = await self.get_message(message_id)
        if not message:
            return None

        try:
            headers = message.get('payload', {}).get('headers', [])
            for header in headers:
                if header.get('name') == 'From':
                    return header.get('value')
        except Exception as e:
            logger.error(f"Error getting sender: {str(e)}")

        return None

    async def get_message_body(self, message_id: str) -> Optional[str]:
        """
        Extract plain text body from email message.

        Handles multipart emails, preferring plain text over HTML.
        If only HTML is available, strips HTML tags.

        Args:
            message_id: Gmail message ID

        Returns:
            Plain text body or None
        """
        message = await self.get_message(message_id)
        if not message:
            return None

        try:
            payload = message.get('payload', {})
            return self._extract_body_from_payload(payload)
        except Exception as e:
            logger.error(f"Error extracting message body: {str(e)}")
            return None

    def _extract_body_from_payload(self, payload: Dict) -> Optional[str]:
        """
        Recursively extract body text from email payload.

        Handles nested multipart structures.
        """
        mime_type = payload.get('mimeType', '')

        # Direct body content
        body = payload.get('body', {})
        data = body.get('data')

        if data and mime_type == 'text/plain':
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')

        # Multipart - recurse into parts
        parts = payload.get('parts', [])
        if parts:
            # First pass: look for text/plain
            for part in parts:
                part_mime = part.get('mimeType', '')
                if part_mime == 'text/plain':
                    part_body = part.get('body', {})
                    part_data = part_body.get('data')
                    if part_data:
                        return base64.urlsafe_b64decode(part_data).decode('utf-8', errors='replace')
                # Recurse into nested multipart
                elif part_mime.startswith('multipart/'):
                    result = self._extract_body_from_payload(part)
                    if result:
                        return result

            # Second pass: fall back to HTML if no plain text
            for part in parts:
                part_mime = part.get('mimeType', '')
                if part_mime == 'text/html':
                    part_body = part.get('body', {})
                    part_data = part_body.get('data')
                    if part_data:
                        html_content = base64.urlsafe_b64decode(part_data).decode('utf-8', errors='replace')
                        return self._html_to_text(html_content)

        # Single-part HTML message
        if data and mime_type == 'text/html':
            html_content = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
            return self._html_to_text(html_content)

        return None

    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML to plain text.

        Simple implementation that strips tags and decodes entities.
        """
        import re
        from html import unescape

        # Remove script and style elements
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Convert br and p tags to newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)

        # Remove all other HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Decode HTML entities
        text = unescape(text)

        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
        text = text.strip()

        return text

    async def get_message_date(self, message_id: str) -> Optional[str]:
        """
        Get message date.

        Args:
            message_id: Gmail message ID

        Returns:
            Date string or None
        """
        message = await self.get_message(message_id)
        if not message:
            return None

        try:
            headers = message.get('payload', {}).get('headers', [])
            for header in headers:
                if header.get('name') == 'Date':
                    return header.get('value')
        except Exception as e:
            logger.error(f"Error getting date: {str(e)}")

        return None

    async def get_message_recipients(self, message_id: str) -> Optional[str]:
        """
        Get message recipients (To field).

        Args:
            message_id: Gmail message ID

        Returns:
            Recipients string or None
        """
        message = await self.get_message(message_id)
        if not message:
            return None

        try:
            headers = message.get('payload', {}).get('headers', [])
            for header in headers:
                if header.get('name') == 'To':
                    return header.get('value')
        except Exception as e:
            logger.error(f"Error getting recipients: {str(e)}")

        return None

    def get_supported_extensions(self) -> Dict[str, str]:
        """Get supported file types and their extensions"""
        return SUPPORTED_ATTACHMENT_TYPES.copy()


# Global instance
_gmail_service = None


async def get_gmail_service() -> GmailService:
    """Get or create Gmail service instance"""
    global _gmail_service
    if _gmail_service is None:
        _gmail_service = GmailService()
        await _gmail_service.authenticate()
    return _gmail_service


async def reset_gmail_service():
    """Reset Gmail service (useful for re-authentication)"""
    global _gmail_service
    _gmail_service = None
