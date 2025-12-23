# Test Fixtures

Place sample PDF documents here for testing the Document Intelligence System.

## Usage

```bash
cd /root/flourisha/00_AI_Brain

# Test with a PDF in this directory (auto-finds first .pdf)
python tests/test_document_intelligence.py

# Test with a specific PDF
python tests/test_document_intelligence.py tests/fixtures/sample-invoice.pdf

# Extraction only (faster, no matching)
python tests/test_document_intelligence.py --extract-only tests/fixtures/sample.pdf

# Save results to JSON
python tests/test_document_intelligence.py -o results.json tests/fixtures/sample.pdf
```

## Sample Documents to Test

Good test documents include:
- Invoices (company, amounts, dates)
- Contracts (parties, terms, signatures)
- Lease agreements (property, tenant, landlord)
- Correspondence (sender, recipient, subject)
- Tax documents (financial details)
