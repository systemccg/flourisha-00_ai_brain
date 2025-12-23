# Daniel Miessler's PAI Implementation Plan
## leadingai004 Server Integration

**Date**: 2025-11-14
**Goal**: Implement Daniel Miessler's Personal AI Infrastructure with real estate management integration

---

## 🎯 Implementation Strategy

### Core Principle
Set up Daniel's PAI architecture on this server to:
- Connect to **existing Odoo instance** (API integration)
- Integrate **existing Google Shared Drives** (4 PARA drives)
- Use **existing Docker services** as implementation tools (n8n, Supabase, Neo4j, Open WebUI)
- Add **real estate-specific skills** on top of PAI foundation

---

## 📋 Phase 1: PAI Foundation Setup (2-3 hours)

### Step 1: Clone and Install PAI
```bash
# Clone Daniel's repository
cd /root
git clone https://github.com/danielmiessler/Personal_AI_Infrastructure.git pai-repo

# Copy .claude structure to home directory
cp -r pai-repo/.claude ~/.claude

# Set environment variables
echo 'export PAI_DIR="/root/pai-repo"' >> ~/.bashrc
echo 'export PAI_HOME="$HOME"' >> ~/.bashrc
source ~/.bashrc
```

### Step 2: Configure Environment Variables
Create `~/.claude/.env` with:
```bash
# Odoo Integration (your existing instance)
ODOO_URL="https://your-odoo-instance.com"
ODOO_DB="your_database_name"
ODOO_USERNAME="your_username"
ODOO_PASSWORD="your_password"

# Google Drive Integration
GOOGLE_DRIVE_PROJECTS_ID="your_projects_drive_id"
GOOGLE_DRIVE_AREAS_ID="your_areas_drive_id"
GOOGLE_DRIVE_RESOURCES_ID="your_resources_drive_id"
GOOGLE_DRIVE_ARCHIVES_ID="your_archives_drive_id"
GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
GOOGLE_REFRESH_TOKEN="your_refresh_token"

# AI APIs (for Claude Code integration)
ANTHROPIC_API_KEY="your_anthropic_key"
OPENAI_API_KEY="your_openai_key"
PERPLEXITY_API_KEY="your_perplexity_key" # For research

# Existing Service URLs (this server)
N8N_URL="https://n8n.leadingai.info"
SUPABASE_URL="https://db.leadingai.info"
NEO4J_URL="https://neo4j.leadingai.info"
OPEN_WEBUI_URL="https://webui.leadingai.info"

# Database Connections
SUPABASE_KEY="your_supabase_anon_key"
SUPABASE_SERVICE_KEY="your_supabase_service_key"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj"
```

### Step 3: Install Dependencies
```bash
# Install Bun (JavaScript runtime for PAI)
curl -fsSL https://bun.sh/install | bash
source ~/.bashrc

# Verify installation
bun --version

# Install PAI dependencies
cd ~/.claude
bun install
```

---

## 📋 Phase 2: Real Estate Skills Setup (3-4 hours)

### Step 1: Create Custom Skills Directory Structure

```bash
mkdir -p ~/.claude/skills/{real-estate-core,property-management,deal-pipeline,financial-analysis}
```

### Skill Organization:

```
~/.claude/skills/
├── CORE/                          # PAI system identity (from Daniel)
├── real-estate-core/              # NEW: Real estate foundation
│   ├── SKILL.md
│   ├── workflows/
│   │   ├── odoo-sync.md
│   │   ├── property-lookup.md
│   │   └── portfolio-summary.md
│   └── scripts/
│       └── odoo-connector.ts
│
├── property-management/           # NEW: Property operations
│   ├── SKILL.md
│   ├── workflows/
│   │   ├── add-property.md
│   │   ├── update-financials.md
│   │   ├── maintenance-request.md
│   │   └── tenant-management.md
│   └── integrations/
│       ├── n8n-workflows/
│       └── supabase-functions/
│
├── deal-pipeline/                 # NEW: Acquisition management
│   ├── SKILL.md
│   ├── workflows/
│   │   ├── analyze-deal.md
│   │   ├── due-diligence.md
│   │   └── closing-checklist.md
│   └── templates/
│       └── deal-analysis.json
│
├── financial-analysis/            # NEW: Portfolio analytics
│   ├── SKILL.md
│   ├── workflows/
│   │   ├── monthly-report.md
│   │   ├── portfolio-performance.md
│   │   └── tax-preparation.md
│   └── scripts/
│       └── analytics-engine.ts
│
├── research/                      # From Daniel's PAI
├── development/                   # From Daniel's PAI
├── content-creation/              # From Daniel's PAI
└── fabric/                        # Daniel's 242+ patterns
```

### Step 2: Create SKILL.md Templates

**Example: `~/.claude/skills/real-estate-core/SKILL.md`**

```markdown
# Real Estate Core - Skill Definition

**Domain**: Real Estate Investment Management
**Purpose**: Foundation skill for all real estate operations, Odoo integration, and PARA file management
**Version**: 1.0.0

## Progressive Disclosure

### Tier 1: Metadata (Always Loaded) ~150 tokens
Real estate investment management core system integrating with:
- Odoo ERP (external instance)
- Google Shared Drives (PARA structure)
- Local AI services (n8n, Supabase, Neo4j)

**Capabilities**: Property lookup, Odoo sync, portfolio summaries, file organization

### Tier 2: Instructions (On-Demand) ~2000 tokens

#### Odoo Integration
Connect to external Odoo instance via API:
- Authentication: JSON-RPC 2.0
- Models: `real.estate.property`, `real.estate.tenant`, `real.estate.lease`
- Operations: search_read, create, write, unlink

#### Google Drive Integration
PARA structure across 4 Shared Drives:
- **PROJECTS**: Active deals, renovations, dispositions
- **AREAS**: Property portfolio, business operations, investment strategy
- **RESOURCES**: Knowledge base, tools, connections
- **ARCHIVES**: Completed projects, inactive areas

#### Local Services Integration
- **n8n**: Workflow automation (rent collection, alerts, reporting)
- **Supabase**: Supplemental data storage, real-time subscriptions
- **Neo4j**: Property relationships, market connections, investor network
- **Open WebUI**: AI-powered chat interface for property queries

### Tier 3: Resources (As-Needed) ~1000+ tokens
- Odoo API documentation: `/resources/odoo-api-reference.md`
- Google Drive API guide: `/resources/google-drive-api.md`
- Database schemas: `/resources/schemas/`
- Example queries: `/resources/examples/`

## Natural Language Triggers

This skill activates when you mention:
- "property" or "properties"
- "portfolio"
- "Odoo"
- "real estate"
- "LLC" or "company"
- "tenant" or "lease"
- "Google Drive" or "PARA"

## Dependencies

- **Required**: Odoo API access, Google Drive API credentials
- **Optional**: n8n webhooks, Supabase connection, Neo4j graph queries

## Integration Points

### Odoo Connector
```typescript
// Location: ~/.claude/skills/real-estate-core/scripts/odoo-connector.ts
import { xmlrpc } from 'odoo-xmlrpc';

class OdooConnector {
  async authenticate() { ... }
  async getProperties(filters) { ... }
  async createProperty(data) { ... }
  async updateProperty(id, data) { ... }
}
```

### Google Drive Manager
```typescript
// Location: ~/.claude/skills/real-estate-core/scripts/drive-manager.ts
class DriveManager {
  async uploadToPARA(file, category, path) { ... }
  async searchDocuments(query, drive) { ... }
  async organizeFiles() { ... }
}
```

### n8n Webhook Triggers
```bash
# Rent collection workflow
POST https://n8n.leadingai.info/webhook/rent-collected

# Maintenance request
POST https://n8n.leadingai.info/webhook/maintenance-request

# Financial report generation
POST https://n8n.leadingai.info/webhook/generate-report
```

## Quick Start

```bash
# Get property by address
claude-skill real-estate-core property-lookup "123 Main St"

# Sync Odoo properties to local cache
claude-skill real-estate-core odoo-sync --full

# Generate portfolio summary
claude-skill real-estate-core portfolio-summary --period=monthly
```

## Configuration

Environment variables in `~/.claude/.env`:
- `ODOO_URL`: Odoo instance URL
- `ODOO_DB`: Database name
- `ODOO_USERNAME`: API username
- `ODOO_PASSWORD`: API password
- `GOOGLE_DRIVE_*_ID`: Shared Drive IDs for PARA structure

## Workflows

Located in `./workflows/`:
- `odoo-sync.md`: Synchronize Odoo data
- `property-lookup.md`: Find property details
- `portfolio-summary.md`: Generate portfolio reports

## Error Handling

- **Odoo connection failed**: Falls back to cached data in Supabase
- **Google Drive API limit**: Queues operations, retries with exponential backoff
- **n8n webhook timeout**: Logs to error queue for manual review

---

**Last Updated**: 2025-11-14
**Maintainer**: Real Estate Operations Team
```

---

## 📋 Phase 3: Integration Bridges (2-3 hours)

### Create Integration Scripts

#### 1. Odoo API Connector
**File**: `~/.claude/skills/real-estate-core/scripts/odoo-connector.ts`

```typescript
import xmlrpc from 'xmlrpc';

export class OdooConnector {
  private url: string;
  private db: string;
  private username: string;
  private password: string;
  private uid: number | null = null;

  constructor() {
    this.url = process.env.ODOO_URL!;
    this.db = process.env.ODOO_DB!;
    this.username = process.env.ODOO_USERNAME!;
    this.password = process.env.ODOO_PASSWORD!;
  }

  async authenticate(): Promise<boolean> {
    const client = xmlrpc.createClient({ url: `${this.url}/xmlrpc/2/common` });

    return new Promise((resolve, reject) => {
      client.methodCall('authenticate', [
        this.db,
        this.username,
        this.password,
        {}
      ], (err: any, uid: number) => {
        if (err) reject(err);
        this.uid = uid;
        resolve(uid > 0);
      });
    });
  }

  async searchRead(model: string, domain: any[] = [], fields: string[] = []): Promise<any[]> {
    if (!this.uid) await this.authenticate();

    const client = xmlrpc.createClient({ url: `${this.url}/xmlrpc/2/object` });

    return new Promise((resolve, reject) => {
      client.methodCall('execute_kw', [
        this.db,
        this.uid,
        this.password,
        model,
        'search_read',
        [domain],
        { fields }
      ], (err: any, result: any[]) => {
        if (err) reject(err);
        resolve(result);
      });
    });
  }

  async create(model: string, values: object): Promise<number> {
    if (!this.uid) await this.authenticate();

    const client = xmlrpc.createClient({ url: `${this.url}/xmlrpc/2/object` });

    return new Promise((resolve, reject) => {
      client.methodCall('execute_kw', [
        this.db,
        this.uid,
        this.password,
        model,
        'create',
        [values]
      ], (err: any, id: number) => {
        if (err) reject(err);
        resolve(id);
      });
    });
  }

  async write(model: string, ids: number[], values: object): Promise<boolean> {
    if (!this.uid) await this.authenticate();

    const client = xmlrpc.createClient({ url: `${this.url}/xmlrpc/2/object` });

    return new Promise((resolve, reject) => {
      client.methodCall('execute_kw', [
        this.db,
        this.uid,
        this.password,
        model,
        'write',
        [ids, values]
      ], (err: any, success: boolean) => {
        if (err) reject(err);
        resolve(success);
      });
    });
  }

  // Helper methods for real estate
  async getProperties(companyId?: number): Promise<any[]> {
    const domain = companyId
      ? [['company_id', '=', companyId], ['active', '=', true]]
      : [['active', '=', true]];

    return this.searchRead('real.estate.property', domain, [
      'name', 'address', 'property_type', 'analytic_account_id',
      'acquisition_price', 'current_market_value', 'google_drive_folder_id'
    ]);
  }

  async getPropertyFinancials(propertyId: number, startDate?: string, endDate?: string): Promise<any[]> {
    const domain = [['property_id', '=', propertyId]];
    if (startDate) domain.push(['period_date', '>=', startDate]);
    if (endDate) domain.push(['period_date', '<=', endDate]);

    return this.searchRead('property.financial.metrics', domain, [
      'period_date', 'rental_income', 'total_expenses', 'net_cash_flow',
      'occupancy_rate', 'cap_rate', 'roi_ytd'
    ]);
  }
}

// Export singleton instance
export const odoo = new OdooConnector();
```

#### 2. Google Drive Manager
**File**: `~/.claude/skills/real-estate-core/scripts/drive-manager.ts`

```typescript
import { google } from 'googleapis';

export class DriveManager {
  private drive: any;
  private driveIds = {
    projects: process.env.GOOGLE_DRIVE_PROJECTS_ID!,
    areas: process.env.GOOGLE_DRIVE_AREAS_ID!,
    resources: process.env.GOOGLE_DRIVE_RESOURCES_ID!,
    archives: process.env.GOOGLE_DRIVE_ARCHIVES_ID!
  };

  constructor() {
    const auth = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET
    );
    auth.setCredentials({ refresh_token: process.env.GOOGLE_REFRESH_TOKEN });

    this.drive = google.drive({ version: 'v3', auth });
  }

  async uploadFile(
    fileName: string,
    content: Buffer | string,
    mimeType: string,
    paraCategory: 'projects' | 'areas' | 'resources' | 'archives',
    folderPath: string
  ): Promise<string> {
    // Get or create folder path
    const folderId = await this.getOrCreateFolderPath(paraCategory, folderPath);

    // Upload file
    const response = await this.drive.files.create({
      requestBody: {
        name: fileName,
        parents: [folderId],
        mimeType
      },
      media: {
        mimeType,
        body: content
      },
      fields: 'id,name,webViewLink'
    });

    return response.data.id;
  }

  async getOrCreateFolderPath(
    paraCategory: 'projects' | 'areas' | 'resources' | 'archives',
    path: string
  ): Promise<string> {
    const driveId = this.driveIds[paraCategory];
    const pathParts = path.split('/').filter(p => p.trim());

    let currentFolderId = driveId;

    for (const folderName of pathParts) {
      // Search for existing folder
      const searchResponse = await this.drive.files.list({
        q: `name='${folderName}' and '${currentFolderId}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false`,
        driveId,
        includeItemsFromAllDrives: true,
        supportsAllDrives: true,
        fields: 'files(id, name)'
      });

      if (searchResponse.data.files && searchResponse.data.files.length > 0) {
        currentFolderId = searchResponse.data.files[0].id;
      } else {
        // Create folder
        const createResponse = await this.drive.files.create({
          requestBody: {
            name: folderName,
            mimeType: 'application/vnd.google-apps.folder',
            parents: [currentFolderId]
          },
          supportsAllDrives: true,
          fields: 'id'
        });
        currentFolderId = createResponse.data.id;
      }
    }

    return currentFolderId;
  }

  async searchFiles(query: string, paraCategory?: 'projects' | 'areas' | 'resources' | 'archives'): Promise<any[]> {
    const driveIds = paraCategory ? [this.driveIds[paraCategory]] : Object.values(this.driveIds);
    const results: any[] = [];

    for (const driveId of driveIds) {
      const response = await this.drive.files.list({
        q: `fullText contains '${query}' and trashed=false`,
        driveId,
        includeItemsFromAllDrives: true,
        supportsAllDrives: true,
        fields: 'files(id, name, mimeType, webViewLink, createdTime, modifiedTime)'
      });

      if (response.data.files) {
        results.push(...response.data.files);
      }
    }

    return results;
  }

  async createPropertyFolder(propertyAddress: string, propertyId: number): Promise<string> {
    // Create in AREAS > PROPERTY-PORTFOLIO
    const folderName = `${propertyAddress.replace(/[^a-zA-Z0-9]/g, '-')}_${propertyId}`;
    const folderId = await this.getOrCreateFolderPath('areas', `PROPERTY-PORTFOLIO/${folderName}`);

    // Create subfolders
    const subfolders = ['Leases', 'Maintenance', 'Financial', 'Photos', 'Legal'];
    for (const subfolder of subfolders) {
      await this.drive.files.create({
        requestBody: {
          name: subfolder,
          mimeType: 'application/vnd.google-apps.folder',
          parents: [folderId]
        },
        supportsAllDrives: true
      });
    }

    return folderId;
  }
}

// Export singleton instance
export const driveManager = new DriveManager();
```

#### 3. n8n Workflow Triggers
**File**: `~/.claude/skills/property-management/integrations/n8n-workflows/README.md`

```markdown
# n8n Workflow Integrations

## Available Workflows

### 1. Rent Collection Automation
**Webhook**: `POST https://n8n.leadingai.info/webhook/rent-collected`
**Payload**:
```json
{
  "property_id": 123,
  "tenant_id": 456,
  "amount": 2500.00,
  "payment_date": "2025-11-01",
  "payment_method": "ACH"
}
```
**Actions**:
- Creates accounting entry in Odoo
- Updates property financial metrics
- Sends confirmation email to tenant
- Logs to Supabase for analytics

### 2. Maintenance Request Creation
**Webhook**: `POST https://n8n.leadingai.info/webhook/maintenance-request`
**Payload**:
```json
{
  "property_id": 123,
  "tenant_id": 456,
  "title": "Leaking faucet in bathroom",
  "description": "Water dripping from main bathroom faucet",
  "priority": "medium",
  "photos": ["photo_url1", "photo_url2"]
}
```
**Actions**:
- Creates maintenance request in Odoo
- Assigns to vendor based on category
- Uploads photos to Google Drive property folder
- Sends notifications to property manager

### 3. Monthly Financial Report Generation
**Webhook**: `POST https://n8n.leadingai.info/webhook/generate-report`
**Payload**:
```json
{
  "report_type": "monthly",
  "period": "2025-11",
  "property_ids": [123, 456, 789],
  "email_recipients": ["owner@example.com"]
}
```
**Actions**:
- Fetches financial data from Odoo
- Queries Neo4j for market comparisons
- Generates report with AI insights
- Uploads to Google Drive AREAS/PROPERTY-PORTFOLIO
- Emails PDF report to recipients
```

---

## 📋 Phase 4: Workflow Templates (1-2 hours)

### Create Workflow Files

**Example**: `~/.claude/skills/property-management/workflows/add-property.md`

```markdown
# Add Property Workflow

**Trigger Phrases**: "add property", "new property", "create property"
**Estimated Time**: 5-10 minutes
**Prerequisites**: Odoo access, Google Drive PARA structure

## Workflow Steps

### 1. Gather Property Information
```
Ask user for:
- Property address (full street address)
- Property type (single_family, multi_family, commercial, land)
- Company/LLC (if multiple entities)
- Acquisition date
- Acquisition price
- Current market value (optional)
- Property details (bedrooms, bathrooms, sq ft)
```

### 2. Create Property in Odoo
```typescript
import { odoo } from '../scripts/odoo-connector';

const propertyData = {
  name: address,
  address: address,
  city: city,
  state: state,
  zip_code: zip,
  property_type: type,
  company_id: companyId,
  acquisition_date: acquisitionDate,
  acquisition_price: price,
  current_market_value: marketValue,
  bedrooms: bedrooms,
  bathrooms: bathrooms,
  square_feet: sqft
};

const propertyId = await odoo.create('real.estate.property', propertyData);
```

### 3. Create Google Drive Folder
```typescript
import { driveManager } from '../scripts/drive-manager';

const folderId = await driveManager.createPropertyFolder(address, propertyId);

// Update Odoo with Google Drive folder ID
await odoo.write('real.estate.property', [propertyId], {
  google_drive_folder_id: folderId
});
```

### 4. Create Analytic Account
```typescript
// Create analytic account for property-level tracking
const analyticAccount = await odoo.create('account.analytic.account', {
  name: `Property: ${address}`,
  code: `PROP-${propertyId}`,
  company_id: companyId
});

// Link to property
await odoo.write('real.estate.property', [propertyId], {
  analytic_account_id: analyticAccount
});
```

### 5. Initialize Supabase Record (Optional)
```typescript
// Store supplemental data in Supabase for faster queries
const { data, error } = await supabase
  .from('properties')
  .insert({
    odoo_id: propertyId,
    address: address,
    google_drive_folder: folderId,
    created_at: new Date()
  });
```

### 6. Create Neo4j Node (Optional)
```cypher
// Create property node for relationship tracking
CREATE (p:Property {
  odoo_id: $propertyId,
  address: $address,
  type: $propertyType,
  acquisition_date: date($acquisitionDate)
})
```

### 7. Confirmation
```
Return to user:
- Property ID in Odoo
- Google Drive folder link
- Summary of created records
```

## Example Usage

```
User: Add a new property at 123 Main Street
Assistant: I'll help you add that property. Let me gather some information...

[Collects property details]