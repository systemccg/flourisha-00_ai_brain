---
name: Real Estate Core
description: |
  Foundation skill for real estate investment management with Odoo ERP integration,
  Google Shared Drives PARA organization, and local service orchestration.

  USE PROACTIVELY when user mentions properties, portfolio, tenants, or real estate operations.

triggers:
  - property
  - properties
  - portfolio
  - real estate
  - tenant
  - lease
  - LLC
  - company
  - Odoo
  - PARA
  - Google Drive
---

# Real Estate Core - Skill Definition

**Version**: 1.0.0
**Domain**: Real Estate Investment Management
**Purpose**: Core integration layer for Odoo ERP, Google Drives (PARA), and local AI services

---

## Progressive Disclosure

### Tier 1: Metadata (Always Loaded) ~150 tokens

Foundation skill for real estate investment operations:

**External Integrations**:
- Odoo ERP (external instance) - Property data, financials, tenants
- Google Shared Drives - PARA structure (Projects, Areas, Resources, Archives)

**Local Services**:
- n8n: Workflow automation engine
- Supabase: Fast queries & real-time subscriptions
- Neo4j: Property relationships & market analysis
- Open WebUI: AI chat interface

**Capabilities**:
- Property lookup and portfolio summaries
- Odoo data synchronization
- PARA file organization
- Financial reporting
- Multi-LLC management

**Natural Language Triggers**: property, portfolio, tenant, lease, Odoo, real estate, LLC

---

### Tier 2: Instructions (On-Demand) ~2000 tokens

#### Odoo Integration Architecture

**Connection Method**: XML-RPC 2.0
**Base URL**: From `$ODOO_URL` environment variable
**Authentication**: Username/password from environment

**Core Models**:
```
real.estate.property     - Property master data
real.estate.tenant       - Tenant management
real.estate.lease        - Lease tracking
property.financial.metrics - Monthly performance
account.analytic.account - Property-level accounting
res.company              - LLC entities
```

**Common Operations**:
- `search_read`: Query properties with filters
- `create`: Add new properties/tenants
- `write`: Update existing records
- `read`: Get detailed property information

#### Google Drive PARA Structure

**4 Shared Drives**:

1. **PROJECTS Drive** - Active work with deadlines
   - ACTIVE-DEALS/
   - RENOVATIONS/
   - DEVELOPMENT-PROJECTS/
   - DISPOSITION-SALES/

2. **AREAS Drive** - Ongoing responsibilities
   - PROPERTY-PORTFOLIO/ (property folders by address)
   - BUSINESS-OPERATIONS/
   - INVESTMENT-STRATEGY/
   - AI-ENHANCED-OPERATIONS/

3. **RESOURCES Drive** - Reference materials
   - REAL-ESTATE-KNOWLEDGE/
   - ANALYSIS-TOOLS/
   - INDUSTRY-CONNECTIONS/
   - AI-GENERATED-INSIGHTS/

4. **ARCHIVES Drive** - Historical records
   - COMPLETED-PROJECTS/
   - INACTIVE-AREAS/
   - OLD-RESOURCES/
   - HISTORICAL/

**File Organization**:
- Each property gets subfolder in AREAS/PROPERTY-PORTFOLIO/
- Subfolders: Leases, Maintenance, Financial, Photos, Legal
- AI automatically routes documents to appropriate PARA category

#### Local Services Integration

**n8n Workflows** (https://n8n.leadingai.info):
- `/webhook/rent-collected` - Process rent payments
- `/webhook/maintenance-request` - Create maintenance tickets
- `/webhook/generate-report` - Monthly financial reports

**Supabase** (https://db.leadingai.info):
- Cached property data for fast queries
- Real-time subscriptions for dashboard updates
- Supplemental data (notes, tags, custom fields)

**Neo4j** (neo4j://localhost:7687):
- Property relationship graphs
- Market comparison networks
- Investor/partner connections
- Neighborhood trend analysis

**Open WebUI** (https://webui.leadingai.info):
- Natural language property queries
- AI-powered investment analysis
- Chat interface for property management

---

### Tier 3: Resources (As-Needed) ~1000+ tokens

**Documentation Links**:
- Odoo XML-RPC API: `/root/.claude/skills/real-estate-core/docs/odoo-api.md`
- Google Drive API: `/root/.claude/skills/real-estate-core/docs/google-drive-api.md`
- n8n Webhooks: `/root/.claude/skills/real-estate-core/docs/n8n-integration.md`
- Data Schemas: `/root/.claude/skills/real-estate-core/docs/schemas.md`

**Example Queries**:
```typescript
// Get all properties for a company
await odoo.searchRead('real.estate.property', [
  ['company_id', '=', companyId],
  ['active', '=', true]
], ['name', 'address', 'property_type']);

// Get property financials
await odoo.searchRead('property.financial.metrics', [
  ['property_id', '=', propertyId],
  ['period_date', '>=', '2025-01-01']
], ['rental_income', 'total_expenses', 'net_cash_flow']);
```

---

## Dependencies

**Required**:
- Odoo API credentials (`$ODOO_URL`, `$ODOO_USERNAME`, `$ODOO_PASSWORD`)
- Google Drive API (`$GOOGLE_DRIVE_*_ID`, `$GOOGLE_CLIENT_ID`, `$GOOGLE_CLIENT_SECRET`)

**Optional**:
- n8n webhooks (for automation)
- Supabase connection (for caching)
- Neo4j database (for graph analysis)

---

## Workflows

Located in `./workflows/`:
- `property-lookup.md` - Find property by address or ID
- `odoo-sync.md` - Synchronize Odoo data to local cache
- `portfolio-summary.md` - Generate portfolio performance reports
- `file-organization.md` - Organize files in PARA structure

---

## Quick Commands

```bash
# Property lookup
"Find property at 123 Main Street"
"Show me all properties in Springfield LLC"

# Portfolio operations
"Generate portfolio summary for November 2025"
"What's the total monthly cash flow across all properties?"

# Odoo sync
"Sync Odoo properties to local database"
"Update property financials from Odoo"

# File organization
"Upload this lease to property folder"
"Find all maintenance invoices for 456 Oak Ave"
```

---

## Error Handling

**Odoo Connection Failed**:
- Falls back to cached data in Supabase
- Shows last sync timestamp
- Suggests retry or manual connection check

**Google Drive API Rate Limit**:
- Queues operations for retry
- Uses exponential backoff
- Notifies user of delay

**Missing Environment Variables**:
- Lists required variables
- Provides setup instructions
- Offers manual configuration option

---

## Integration Flow Example

```
User: "Show me the financials for 123 Main Street"
  ↓
1. Parse address from query
2. Query Odoo API for property record
3. Fetch financial metrics from Odoo
4. Check Neo4j for market comparisons
5. Generate summary with AI insights
6. Return formatted report
```

---

## Security Notes

- **Never commit `.env` files** - Contains API credentials
- **Odoo credentials** are stored in environment only
- **Google OAuth tokens** use refresh tokens, not passwords
- **All API calls** use HTTPS/TLS encryption
- **Property data** may contain PII - handle according to privacy policy

---

**Last Updated**: 2025-11-14
**Maintainer**: Real Estate Operations Team
**Status**: Active Development
