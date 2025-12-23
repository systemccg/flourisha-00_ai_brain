#!/usr/bin/env python3
"""
Quick test script for Gmail integration.
Tests:
1. Gmail service authentication
2. Email body extraction
3. KnowledgeIngestionService.ingest_text()
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.gmail_service import GmailService
from services.knowledge_ingestion_service import get_ingestion_service


async def test_gmail_auth():
    """Test Gmail authentication"""
    print("\n=== Testing Gmail Authentication ===")

    gmail = GmailService()
    success = await gmail.authenticate()

    if success:
        print("✓ Gmail authentication successful")
        return gmail
    else:
        print("✗ Gmail authentication failed")
        print("  Make sure:")
        print("  1. credentials.json exists at /root/.config/gmail/credentials.json")
        print("  2. Gmail API is enabled in Google Cloud Console")
        print("  3. Run this script with a browser available for OAuth flow")
        return None


async def test_list_messages(gmail: GmailService):
    """Test listing messages"""
    print("\n=== Testing Message Listing ===")

    # Try to list some messages from inbox
    messages = await gmail.list_messages(label="INBOX", max_results=3)

    if messages:
        print(f"✓ Found {len(messages)} messages in INBOX")
        return messages[0]['id'] if messages else None
    else:
        print("✗ No messages found or error occurred")
        return None


async def test_get_body(gmail: GmailService, message_id: str):
    """Test email body extraction"""
    print(f"\n=== Testing Body Extraction (message: {message_id}) ===")

    subject = await gmail.get_message_subject(message_id)
    sender = await gmail.get_message_sender(message_id)
    body = await gmail.get_message_body(message_id)

    print(f"Subject: {subject}")
    print(f"From: {sender}")
    print(f"Body length: {len(body) if body else 0} chars")

    if body:
        print(f"Body preview: {body[:200]}...")
        print("✓ Body extraction successful")
        return body
    else:
        print("✗ Failed to extract body")
        return None


async def test_ingest_text():
    """Test text ingestion (mock data)"""
    print("\n=== Testing KnowledgeIngestionService.ingest_text() ===")

    service = get_ingestion_service(tenant_id="gmail-test")

    test_text = """
    This is a test email from the Gmail integration.

    We are testing the ingestion pipeline to ensure:
    1. Text is stored in the raw document store
    2. Text is chunked and embedded in the vector store
    3. Entities are extracted and stored in the graph store

    Best regards,
    Test Bot
    """

    result = await service.ingest_text(
        text=test_text,
        source="gmail-test",
        source_id="test-message-001",
        title="Test Email: Gmail Integration",
        document_type="email",
        metadata={
            "sender": "test@example.com",
            "recipients": "user@example.com",
            "date": "2025-12-13"
        }
    )

    print(f"Status: {result['status']}")
    print(f"Document ID: {result.get('document_id')}")
    print(f"Chunks created: {result.get('chunks_created', 0)}")
    print(f"Stores: {list(result.get('stores', {}).keys())}")

    if result['status'] == 'success':
        print("✓ Text ingestion successful")
    else:
        print(f"✗ Text ingestion failed: {result.get('errors', [])}")

    return result


async def main():
    print("=" * 60)
    print("Gmail Integration Test Suite")
    print("=" * 60)

    # Test 1: Gmail auth
    gmail = await test_gmail_auth()

    if gmail:
        # Test 2: List messages
        message_id = await test_list_messages(gmail)

        if message_id:
            # Test 3: Get body
            await test_get_body(gmail, message_id)

    # Test 4: Text ingestion (independent of Gmail)
    await test_ingest_text()

    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
