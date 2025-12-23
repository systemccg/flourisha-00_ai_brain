#!/usr/bin/env python3
"""
Gmail Monitor Worker
Polls Gmail for new messages with attachments and queues them for processing
Runs as a background service (systemd)
"""

import asyncio
import logging
import os
import sys
import tempfile
from datetime import datetime
from typing import Dict, List
import json

# Add parent directory (00_AI_Brain) to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gmail_service import get_gmail_service
from services.document_processor import get_document_processor
from services.supabase_client import supabase_service
from services.embeddings_service import get_embeddings_service
from services.chunking_service import chunk_text
from services.knowledge_graph_service import get_knowledge_graph
from services.file_storage_service import get_file_storage
from services.knowledge_ingestion_service import get_ingestion_service
from agents.content_processor import ContentProcessorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/flourisha/gmail_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
GMAIL_LABEL = os.getenv('GMAIL_MONITOR_LABEL', 'Flourisha/Unprocessed')
GMAIL_PROCESSED_LABEL = os.getenv('GMAIL_PROCESSED_LABEL', 'Flourisha/Processed')
POLL_INTERVAL = int(os.getenv('GMAIL_POLL_INTERVAL', '300'))  # 5 minutes
BATCH_SIZE = int(os.getenv('GMAIL_BATCH_SIZE', '10'))
TENANT_ID = os.getenv('FLOURISHA_TENANT_ID', 'default')
USER_ID = os.getenv('FLOURISHA_USER_ID', 'gmail-worker')


class GmailMonitorWorker:
    """Monitor Gmail for labeled emails and ingest them into the AI Brain"""

    def __init__(self):
        self.gmail_service = None
        self.doc_processor = None
        self.embeddings_service = None
        self.kg_service = None
        self.file_storage = None
        self.content_processor = None
        self.ingestion_service = None
        self.running = False

    async def initialize(self) -> bool:
        """Initialize services"""
        try:
            logger.info("Initializing Gmail monitor worker...")

            self.gmail_service = await get_gmail_service()
            self.doc_processor = await get_document_processor()
            self.embeddings_service = get_embeddings_service()  # sync
            self.kg_service = get_knowledge_graph()  # sync
            self.file_storage = get_file_storage()  # sync
            self.content_processor = ContentProcessorAgent()
            self.ingestion_service = get_ingestion_service(tenant_id=TENANT_ID)

            logger.info("Gmail monitor worker initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize worker: {str(e)}")
            return False

    async def process_attachment(
        self,
        message_id: str,
        attachment: Dict,
        subject: str,
        sender: str
    ) -> bool:
        """
        Process a single attachment

        Args:
            message_id: Gmail message ID
            attachment: Attachment metadata
            subject: Message subject
            sender: Sender email

        Returns:
            True if successful
        """
        temp_file = None

        try:
            logger.info(f"Processing attachment: {attachment['filename']}")

            # Download attachment
            attachment_data = await self.gmail_service.download_attachment(
                message_id,
                attachment['attachment_id'],
                attachment['filename']
            )

            if not attachment_data:
                logger.error(f"Failed to download attachment: {attachment['filename']}")
                return False

            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(attachment['filename'])[1]) as f:
                temp_file = f.name
                f.write(attachment_data)

            # Extract text
            text, metadata = await self.doc_processor.process_document(temp_file)
            logger.info(f"Extracted {metadata.get('word_count', 0)} words from {attachment['filename']}")

            # Calculate content hash
            import hashlib
            content_hash = hashlib.sha256(text.encode()).hexdigest()

            # Check if already processed
            existing = supabase_service.supabase.table('document_metadata').select('*').eq(
                'content_hash', content_hash
            ).eq('tenant_id', TENANT_ID).execute()

            if existing.data:
                logger.info(f"Document already processed: {content_hash}")
                return True

            # Create document record
            doc_data = {
                'id': f"gmail-{message_id}",
                'content_hash': content_hash,
                'version_number': 1,
                'is_current': True,
                'is_deleted': False,
                'tenant_id': TENANT_ID,
                'created_by': USER_ID,
                'source_type': 'email_attachment',
                'source_metadata': {
                    'subject': subject,
                    'sender': sender,
                    'attachment_filename': attachment['filename'],
                    'mime_type': attachment['mime_type']
                }
            }

            # Store in database
            doc_response = supabase_service.supabase.table('document_metadata').insert(doc_data).execute()
            if not doc_response.data:
                logger.error("Failed to create document record")
                return False

            logger.info(f"Created document record: {doc_data['id']}")

            # AI Processing (summary, insights, tags)
            ai_result = await self.content_processor.process_content(
                content=text,
                content_type='email_attachment',
                metadata={
                    'subject': subject,
                    'sender': sender,
                    'filename': attachment['filename']
                }
            )

            # Chunking
            chunks = chunk_text(text)
            logger.info(f"Created {len(chunks)} chunks from content")

            # Embeddings
            embeddings_result = await self.embeddings_service.generate_embeddings_batch(
                chunks  # chunk_text returns List[str] directly
            )

            if not embeddings_result:
                logger.error("Failed to generate embeddings")
                return False

            # Store chunks with embeddings
            chunk_data = []
            for i, (chunk_content, embedding) in enumerate(
                zip(chunks, embeddings_result)  # chunks is List[str] from chunk_text()
            ):
                chunk_data.append({
                    'file_id': doc_data['id'],
                    'file_title': attachment['filename'],
                    'chunk_index': i,
                    'content': chunk_content,
                    'embedding': embedding,
                    'metadata': {
                        'source': 'email',
                        'subject': subject,
                        'sender': sender
                    },
                    'tenant_id': TENANT_ID
                })

            chunks_response = supabase_service.supabase.table('documents_pg').insert(chunk_data).execute()
            if not chunks_response.data:
                logger.error("Failed to store chunks")
                return False

            logger.info(f"Stored {len(chunk_data)} chunks in documents_pg")

            # Add to knowledge graph
            try:
                kg_node = {
                    'name': f"[{TENANT_ID}] {attachment['filename']}",
                    'type': 'Document',
                    'properties': {
                        'source': 'email',
                        'subject': subject,
                        'sender': sender,
                        'summary': ai_result.get('summary', '')
                    }
                }
                await self.kg_service.add_episode(kg_node)
                logger.info("Added to knowledge graph")
            except Exception as e:
                logger.warning(f"Failed to add to knowledge graph: {str(e)}")

            # Save PARA file
            try:
                para_title = f"{datetime.now().strftime('%Y-%m-%d')}_{attachment['filename']}"
                await self.file_storage.save_content(
                    title=para_title,
                    content=text,
                    project_id=None,
                    content_type='email_attachment'
                )
                logger.info("Saved PARA file")
            except Exception as e:
                logger.warning(f"Failed to save PARA file: {str(e)}")

            logger.info(f"Successfully processed attachment: {attachment['filename']}")
            return True

        except Exception as e:
            logger.error(f"Error processing attachment: {str(e)}")
            return False

        finally:
            # Clean up temp file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {str(e)}")

    async def process_email_body(
        self,
        message_id: str,
        subject: str,
        sender: str,
        recipients: str,
        date: str
    ) -> bool:
        """
        Ingest email body into the RAG system using KnowledgeIngestionService.

        Args:
            message_id: Gmail message ID
            subject: Email subject
            sender: Sender email address
            recipients: Recipient email addresses
            date: Email date

        Returns:
            True if successful
        """
        try:
            # Get email body text
            body = await self.gmail_service.get_message_body(message_id)

            if not body or len(body.strip()) < 50:
                logger.debug(f"Message {message_id} has no substantial body content")
                return False

            logger.info(f"Processing email body: {subject} ({len(body)} chars)")

            # Check for duplicate based on content hash
            import hashlib
            content_hash = hashlib.sha256(body.encode()).hexdigest()

            # Prepare metadata
            email_metadata = {
                "sender": sender,
                "recipients": recipients,
                "date": date,
                "message_id": message_id,
                "content_hash": content_hash
            }

            # Ingest into all three stores using KnowledgeIngestionService
            result = await self.ingestion_service.ingest_text(
                text=body,
                source="gmail",
                source_id=message_id,
                title=f"Email: {subject}",
                document_type="email",
                metadata=email_metadata
            )

            if result["status"] == "success":
                logger.info(f"Email ingested successfully: {result['document_id']}")
                logger.info(f"  - Chunks created: {result.get('chunks_created', 0)}")
                logger.info(f"  - Stores: {list(result.get('stores', {}).keys())}")
                return True
            else:
                logger.warning(f"Email ingestion partial/failed: {result.get('errors', [])}")
                return result["status"] == "partial"

        except Exception as e:
            logger.error(f"Error processing email body: {str(e)}")
            return False

    async def check_messages(self) -> None:
        """Check for new labeled messages and process them (bodies + attachments)"""
        try:
            logger.info(f"Checking Gmail label: {GMAIL_LABEL}")

            # Get all messages with the label that haven't been processed
            # Removed has:attachment filter - now process all labeled emails
            messages = await self.gmail_service.list_messages(
                label=GMAIL_LABEL,
                query=f"-label:\"{GMAIL_PROCESSED_LABEL}\"",
                max_results=BATCH_SIZE
            )

            if not messages:
                logger.debug("No new messages to process")
                return

            logger.info(f"Found {len(messages)} new messages to process")

            # Process each message
            for message in messages:
                try:
                    message_id = message['id']
                    body_success = False
                    attachment_success_count = 0

                    # Get message details
                    subject = await self.gmail_service.get_message_subject(message_id)
                    sender = await self.gmail_service.get_message_sender(message_id)
                    recipients = await self.gmail_service.get_message_recipients(message_id)
                    date = await self.gmail_service.get_message_date(message_id)

                    logger.info(f"Processing message from {sender}: {subject}")

                    # Step 1: Process email body
                    body_success = await self.process_email_body(
                        message_id,
                        subject or "No subject",
                        sender or "Unknown",
                        recipients or "",
                        date or ""
                    )

                    # Step 2: Process attachments (if any)
                    attachments = await self.gmail_service.get_attachments(message_id)

                    if attachments:
                        logger.info(f"Message has {len(attachments)} attachments")
                        for attachment in attachments:
                            if await self.process_attachment(
                                message_id,
                                attachment,
                                subject or "No subject",
                                sender or "Unknown"
                            ):
                                attachment_success_count += 1

                    # Mark as processed if we processed body or any attachments
                    if body_success or attachment_success_count > 0:
                        await self.gmail_service.mark_as_processed(message_id, GMAIL_PROCESSED_LABEL)
                        logger.info(
                            f"Message {message_id} marked as processed "
                            f"(body: {'yes' if body_success else 'no'}, "
                            f"attachments: {attachment_success_count}/{len(attachments) if attachments else 0})"
                        )
                    else:
                        # Still mark as processed to avoid reprocessing
                        await self.gmail_service.mark_as_processed(message_id, GMAIL_PROCESSED_LABEL)
                        logger.info(f"Message {message_id} marked as processed (no content ingested)")

                except Exception as e:
                    logger.error(f"Error processing message {message_id}: {str(e)}")

        except Exception as e:
            logger.error(f"Error checking messages: {str(e)}")

    async def run(self) -> None:
        """Main worker loop"""
        logger.info("Starting Gmail monitor worker")
        self.running = True

        try:
            # Initialize
            if not await self.initialize():
                logger.error("Failed to initialize worker")
                return

            # Main loop
            while self.running:
                try:
                    await self.check_messages()
                except Exception as e:
                    logger.error(f"Error in main loop: {str(e)}")

                # Wait before next poll
                logger.debug(f"Waiting {POLL_INTERVAL} seconds before next poll...")
                await asyncio.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
            self.running = False
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            self.running = False
        finally:
            logger.info("Gmail monitor worker stopped")

    def stop(self) -> None:
        """Stop the worker"""
        logger.info("Stopping worker...")
        self.running = False


async def main():
    """Entry point"""
    worker = GmailMonitorWorker()

    # Handle shutdown
    import signal

    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        worker.stop()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Run worker
    await worker.run()


if __name__ == "__main__":
    # Ensure log directory exists
    log_dir = '/var/log/flourisha'
    os.makedirs(log_dir, exist_ok=True)

    asyncio.run(main())
