#!/usr/bin/env python3
"""
Test Document Intelligence System

Usage:
    # Test with a specific PDF
    python tests/test_document_intelligence.py path/to/document.pdf

    # Test with default fixture
    python tests/test_document_intelligence.py

    # Skip entity matching (faster, just extraction)
    python tests/test_document_intelligence.py --extract-only path/to/document.pdf

Place sample PDFs in: tests/fixtures/
"""

import os
import sys
import asyncio
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
def load_env():
    """Load environment from ~/.claude/.env"""
    env_file = Path.home() / ".claude" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value.strip('"').strip("'")
        print(f"Loaded environment from {env_file}")

load_env()

# Verify API key
if not os.environ.get("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY not set")
    print("Set it in ~/.claude/.env or export it directly")
    sys.exit(1)


# =============================================================================
# Test Functions
# =============================================================================

async def test_extraction(pdf_path: Path) -> dict:
    """Test document extraction only"""
    from agents.document_processor import process_document
    from agents.models import DocumentContext

    print(f"\n{'='*60}")
    print(f"DOCUMENT EXTRACTION TEST")
    print(f"{'='*60}")
    print(f"File: {pdf_path}")
    print(f"Size: {pdf_path.stat().st_size:,} bytes")

    # Read PDF
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Create context
    context = DocumentContext(
        source="test",
        source_detail="Test script",
        original_filename=pdf_path.name,
        tenant_id="test",
    )

    # Process
    print(f"\nProcessing with Claude...")
    start = datetime.now()

    extraction = await process_document(
        document_content=pdf_bytes,
        context=context,
    )

    elapsed = (datetime.now() - start).total_seconds()
    print(f"Completed in {elapsed:.1f}s")

    # Display results
    print(f"\n{'='*60}")
    print(f"EXTRACTION RESULTS")
    print(f"{'='*60}")

    print(f"\nDocument Name: {extraction.document_name}")
    print(f"Category: {extraction.category.value}")
    if extraction.subcategory:
        print(f"Subcategory: {extraction.subcategory}")
    print(f"Confidence: {extraction.extraction_confidence:.0%}")
    print(f"Needs Review: {extraction.needs_human_review}")

    print(f"\nSummary:\n{extraction.summary}")

    if extraction.document_date:
        print(f"\nDocument Date: {extraction.document_date}")
    if extraction.effective_date:
        print(f"Effective Date: {extraction.effective_date}")

    # Companies
    if extraction.companies:
        print(f"\n--- Companies ({len(extraction.companies)}) ---")
        for c in extraction.companies:
            print(f"  - {c.name}")
            if c.company_type:
                print(f"    Type: {c.company_type}")
            if c.phone:
                print(f"    Phone: {c.phone}")
            if c.email:
                print(f"    Email: {c.email}")
            if c.role_in_document:
                print(f"    Role: {c.role_in_document}")

    # Contacts
    if extraction.contacts:
        print(f"\n--- Contacts ({len(extraction.contacts)}) ---")
        for c in extraction.contacts:
            print(f"  - {c.full_name}")
            if c.title:
                print(f"    Title: {c.title}")
            if c.company:
                print(f"    Company: {c.company}")
            if c.email:
                print(f"    Email: {c.email}")
            if c.phone:
                print(f"    Phone: {c.phone}")

    # Properties
    if extraction.properties:
        print(f"\n--- Properties ({len(extraction.properties)}) ---")
        for p in extraction.properties:
            addr = p.address
            if p.city:
                addr += f", {p.city}"
            if p.state:
                addr += f", {p.state}"
            if p.zip_code:
                addr += f" {p.zip_code}"
            print(f"  - {addr}")
            if p.property_type:
                print(f"    Type: {p.property_type}")

    # Agreement
    if extraction.agreement:
        print(f"\n--- Agreement ---")
        print(f"  Type: {extraction.agreement.agreement_type}")
        if extraction.agreement.title:
            print(f"  Title: {extraction.agreement.title}")
        if extraction.agreement.parties:
            print(f"  Parties: {', '.join(extraction.agreement.parties)}")
        if extraction.agreement.effective_date:
            print(f"  Effective: {extraction.agreement.effective_date}")
        if extraction.agreement.expiration_date:
            print(f"  Expires: {extraction.agreement.expiration_date}")
        if extraction.agreement.value:
            print(f"  Value: ${extraction.agreement.value:,.2f}")

    # Financial
    if extraction.financial:
        print(f"\n--- Financial Details ---")
        if extraction.financial.total_amount:
            print(f"  Total: ${extraction.financial.total_amount:,.2f}")
        if extraction.financial.currency:
            print(f"  Currency: {extraction.financial.currency}")
        if extraction.financial.payment_due_date:
            print(f"  Due: {extraction.financial.payment_due_date}")
        if extraction.financial.account_numbers:
            print(f"  Accounts: {', '.join(extraction.financial.account_numbers)}")
        if extraction.financial.amounts:
            print(f"  Amounts: {', '.join(f'${a:,.2f}' for a in extraction.financial.amounts)}")

    # Primary entities
    print(f"\n--- Primary Entities ---")
    print(f"  Company: {extraction.primary_company or 'N/A'}")
    print(f"  Contact: {extraction.primary_contact or 'N/A'}")
    print(f"  Property: {extraction.primary_property or 'N/A'}")

    return extraction.model_dump()


async def test_full_pipeline(pdf_path: Path) -> dict:
    """Test full pipeline including entity matching and resolution"""
    from ingestion.document_ingestion import process_uploaded_file

    print(f"\n{'='*60}")
    print(f"FULL PIPELINE TEST (with Entity Resolution)")
    print(f"{'='*60}")
    print(f"File: {pdf_path.name}")

    # Read PDF
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Process through full pipeline
    print(f"\nRunning full pipeline (resolve -> extract -> match -> store)...")
    print(f"Note: Storage will be skipped in test mode")

    start = datetime.now()

    # Import here to avoid circular imports
    from ingestion.document_ingestion import process_document_from_source

    result = await process_document_from_source(
        pdf_bytes=pdf_bytes,
        source="test",
        filename=pdf_path.name,
        source_detail="Test script - full pipeline",
        tenant_id="test",
        skip_storage=True,  # Don't actually store in test
    )

    elapsed = (datetime.now() - start).total_seconds()

    print(f"\n{'='*60}")
    print(f"PIPELINE RESULTS")
    print(f"{'='*60}")
    print(f"Success: {result.success}")
    print(f"Processing Time: {result.processing_time_ms}ms ({elapsed:.1f}s)")

    if result.error:
        print(f"Error: {result.error}")

    # Show filename parsing and entity resolution
    if result.filename_parsed:
        print(f"\n--- Filename Parsing ---")
        print(f"  Company: {result.filename_parsed.get('company', 'N/A')}")
        print(f"  Property: {result.filename_parsed.get('property', 'N/A')}")
        print(f"  Description: {result.filename_parsed.get('description', 'N/A')}")
        print(f"  Date: {result.filename_parsed.get('date', 'N/A')}")

    if result.resolved_property:
        print(f"\n--- Resolved Property (from alias) ---")
        print(f"  Shorthand: {result.resolved_property.get('shorthand')}")
        print(f"  Full Address: {result.resolved_property.get('name')}")
        print(f"  Owner: {result.resolved_property.get('owner')}")
        print(f"  Matched via: {result.resolved_property.get('matched_via')}")

    if result.resolved_organization:
        print(f"\n--- Resolved Organization (from alias) ---")
        print(f"  Name: {result.resolved_organization.get('name')}")
        print(f"  Matched via: {result.resolved_organization.get('matched_via')}")

    print(f"\n--- Entities Extracted from Document ---")
    print(f"  Companies: {result.companies_found}")
    print(f"  Contacts: {result.contacts_found}")
    print(f"  Properties: {result.properties_found}")

    if result.matching:
        print(f"\n--- Matching Results ---")
        print(f"  Auto-linkable: {result.entities_linked}")
        print(f"  New entities: {result.entities_created}")
        print(f"  Needs review: {result.matching.needs_review}")

    # Show validation results from feedback system
    if result.validation_results:
        print(f"\n--- Validation Results (Feedback Loop) ---")
        print(f"  All Passed: {result.validation_passed}")
        if result.needs_review_reason:
            print(f"  ⚠️  Review Needed: {result.needs_review_reason}")
        for v in result.validation_results:
            status = "✅" if v['passed'] else "❌"
            print(f"  {status} {v['rule']} ({v['severity']})")
            if v.get('suggestion'):
                print(f"      → {v['suggestion']}")

    if result.extraction:
        print(f"\n--- Document Extraction ---")
        print(f"  Name: {result.extraction.document_name}")
        print(f"  Category: {result.extraction.category.value}")
        print(f"  Confidence: {result.extraction.extraction_confidence:.0%}")
        print(f"  Summary: {result.extraction.summary[:200]}...")

    return {
        "success": result.success,
        "processing_time_ms": result.processing_time_ms,
        "companies_found": result.companies_found,
        "contacts_found": result.contacts_found,
        "properties_found": result.properties_found,
        "resolved_property": result.resolved_property,
        "resolved_organization": result.resolved_organization,
    }


# =============================================================================
# Main
# =============================================================================

def find_sample_pdf() -> Path:
    """Find a sample PDF in fixtures directory"""
    fixtures_dir = Path(__file__).parent / "fixtures"

    # Look for any PDF
    pdfs = list(fixtures_dir.glob("*.pdf"))
    if pdfs:
        return pdfs[0]

    # No PDF found
    print(f"\nNo PDF found in {fixtures_dir}")
    print(f"\nTo test, either:")
    print(f"  1. Place a PDF in: {fixtures_dir}/")
    print(f"  2. Pass a path: python {__file__} /path/to/document.pdf")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Test Document Intelligence System")
    parser.add_argument("pdf_path", nargs="?", help="Path to PDF file (optional)")
    parser.add_argument("--extract-only", "-e", action="store_true",
                        help="Only run extraction, skip matching/storage")
    parser.add_argument("--output", "-o", help="Save results to JSON file")

    args = parser.parse_args()

    # Get PDF path
    if args.pdf_path:
        pdf_path = Path(args.pdf_path)
        if not pdf_path.exists():
            print(f"ERROR: File not found: {pdf_path}")
            sys.exit(1)
    else:
        pdf_path = find_sample_pdf()

    # Run test
    if args.extract_only:
        result = asyncio.run(test_extraction(pdf_path))
    else:
        result = asyncio.run(test_full_pipeline(pdf_path))

    # Save output if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nResults saved to: {output_path}")

    print(f"\n{'='*60}")
    print("TEST COMPLETE")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
