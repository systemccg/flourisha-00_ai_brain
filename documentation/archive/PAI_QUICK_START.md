# PAI Quick Start - Get Daniel's System Running Now

**Goal**: Install and configure Daniel Miessler's PAI on this server in under 1 hour

---

## ⚡ Quick Setup Steps

### Step 1: Install Bun Runtime (5 minutes)
```bash
# Install Bun (required for PAI)
curl -fsSL https://bun.sh/install | bash

# Add to PATH
echo 'export BUN_INSTALL="$HOME/.bun"' >> ~/.bashrc
echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
bun --version
```

### Step 2: Clone PAI Repository (2 minutes)
```bash
cd /root
git clone https://github.com/danielmiessler/Personal_AI_Infrastructure.git pai

# Set PAI environment variables
echo 'export PAI_DIR="/root/pai"' >> ~/.bashrc
echo 'export PAI_HOME="$HOME"' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Copy .claude Directory (2 minutes)
```bash
# Copy PAI structure to ~/.claude
cp -r /root/pai/.claude ~/.claude-pai

# Merge with existing .claude directory (preserves your current Claude Code state)
# Copy skills without overwriting existing files
cp -rn ~/.claude-pai/* ~/.claude/ 2>/dev/null || true

# Clean up
rm -rf ~/.claude-pai
```

### Step 4: Install PAI Dependencies (5 minutes)
```bash
cd /root/pai

# Install voice server dependencies (optional, for voice features)
cd voice-server
bun install

# Return to PAI root
cd /root/pai
```

### Step 5: Configure Environment (10 minutes)

Create `~/.claude/.env`:
```bash
cat > ~/.claude/.env << 'EOF'
# ===== PAI Core Configuration =====
PAI_DIR="/root/pai"
PAI_HOME="/root"

# ===== Odoo Integration (Your Existing Instance) =====
ODOO_URL="https://your-odoo-instance.com"
ODOO_DB="your_database_name"
ODOO_USERNAME="your_odoo_username"
ODOO_PASSWORD="your_odoo_password"

# ===== Google Shared Drives (PARA Structure) =====
GOOGLE_DRIVE_PROJECTS_ID="your_projects_drive_id"
GOOGLE_DRIVE_AREAS_ID="your_areas_drive_id"
GOOGLE_DRIVE_RESOURCES_ID="your_resources_drive_id"
GOOGLE_DRIVE_ARCHIVES_ID="your_archives_drive_id"

# Google OAuth (for Drive API access)
GOOGLE_CLIENT_ID="your_google_oauth_client_id"
GOOGLE_CLIENT_SECRET="your_google_oauth_client_secret"
GOOGLE_REFRESH_TOKEN="your_google_refresh_token"

# ===== AI API Keys =====
ANTHROPIC_API_KEY="your_anthropic_api_key"
OPENAI_API_KEY="your_openai_api_key"
PERPLEXITY_API_KEY="your_perplexity_api_key"

# ===== Existing Services (This Server) =====
N8N_URL="https://n8n.leadingai.info"
SUPABASE_URL="https://db.leadingai.info"
SUPABASE_ANON_KEY="your_supabase_anon_key"
SUPABASE_SERVICE_KEY="your_supabase_service_key"
NEO4J_URL="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="riJIO1Zep7Dg4Yv7XsPuqK40e4MF7Eaj"
OPEN_WEBUI_URL="https://webui.leadingai.info"

# ===== Server Configuration =====
TAILSCALE_IP="100.66.28.67"
TRAEFIK_URL="https://traefik.leadingai.info"
EOF
```

### Step 6: Create Real Estate Skills (15 minutes)

```bash
# Create custom skills directories
mkdir -p ~/.claude/skills/{real-estate-core,property-management,deal-pipeline,financial-analysis}

# Create basic SKILL.md for real estate core
cat > ~/.claude/skills/real-estate-core/SKILL.md << 'EOF'
# Real Estate Core

**Domain**: Real Estate Investment Management
**Purpose**: Foundation skill for Odoo integration, PARA file organization, and portfolio management

## Tier 1: Metadata (Always Loaded)
Real estate investment management integrating:
- External Odoo ERP instance (API)
- Google Shared Drives (PARA structure)
- Local services: n8n, Supabase, Neo4j, Open WebUI

**Triggers**: property, portfolio, real estate, LLC, tenant, Odoo, PARA

## Tier 2: Instructions (On-Demand)

### Odoo Connection
- URL: $ODOO_URL
- Authentication: JSON-RPC 2.0
- Models: real.estate.property, real.estate.tenant, property.financial.metrics

### Google Drive PARA
- Projects Drive: Active deals, renovations
- Areas Drive: Portfolio, operations
- Resources Drive: Knowledge, tools
- Archives Drive: Historical records

### Local Services
- n8n: Workflow automation
- Supabase: Supplemental data
- Neo4j: Relationship mapping
- Open WebUI: AI chat interface

## Quick Commands
- Get property: `property-lookup [address]`
- Portfolio summary: `portfolio-summary`
- Sync Odoo: `odoo-sync`

EOF

# Create workflows directory
mkdir -p ~/.claude/skills/real-estate-core/workflows

# Create basic property lookup workflow
cat > ~/.claude/skills/real-estate-core/workflows/property-lookup.md << 'EOF'
# Property Lookup Workflow

**Triggers**: "find property", "lookup property", "property details"

## Steps
1. Extract address from user query
2. Query Odoo API: search_read('real.estate.property')
3. Fetch financial metrics if found
4. Return property details with current performance

## Usage
```
User: "Find property at 123 Main Street"
Result: Property details + financial summary
```
EOF
```

### Step 7: Test PAI Installation (5 minutes)

```bash
# Check PAI directory structure
ls -la ~/.claude/skills/

# Verify environment variables
cat ~/.claude/.env | grep PAI_DIR

# Test Bun is working
cd /root/pai/voice-server && bun --version
```

---

## 🎯 What You Have Now

After completing these steps, you'll have:

1. ✅ **Daniel's PAI Framework** installed in `/root/pai/`
2. ✅ **Skills Directory** at `~/.claude/skills/` with:
   - All of Daniel's default skills (research, development, content-creation, fabric)
   - Custom real estate skills (real-estate-core, property-management, deal-pipeline, financial-analysis)
3. ✅ **Environment Variables** configured for:
   - Odoo API connection
   - Google Drive PARA integration
   - Existing services (n8n, Supabase, Neo4j)
4. ✅ **Bun Runtime** for executing PAI scripts

---

## 📋 Next Steps (After Basic Setup)

### Immediate (Next 1-2 hours)
1. **Configure Google OAuth**
   - Create OAuth credentials in Google Cloud Console
   - Get refresh token for Drive API access
   - Add to `~/.claude/.env`

2. **Test Odoo Connection**
   - Verify API credentials
   - Test property search query
   - Confirm analytic account access

3. **Create First Workflow**
   - Start with simple property lookup
   - Test Odoo → Claude Code integration
   - Verify response format

### Short Term (This Week)
1. **Build Core Workflows**
   - Add property
   - Update financials
   - Generate reports

2. **Integrate n8n**
   - Create webhook endpoints
   - Connect to PAI workflows
   - Test automation flows

3. **Set Up PARA Structure**
   - Verify Google Shared Drive access
   - Create folder templates
   - Test file routing

### Medium Term (This Month)
1. **AI Integration**
   - Connect Open WebUI to PAI skills
   - Create AI-powered property analysis
   - Build predictive models with Neo4j data

2. **Automation**
   - Rent collection workflows
   - Maintenance request routing
   - Monthly report generation

3. **Documentation**
   - Create skill usage guides
   - Document workflow patterns
   - Build team onboarding materials

---

## 🆘 Troubleshooting

### Bun Installation Issues
```bash
# If bun command not found
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
```

### .env File Not Loading
```bash
# Check file exists and has correct content
cat ~/.claude/.env

# Verify no syntax errors
grep -E "^[A-Z_]+=" ~/.claude/.env
```

### PAI Directory Permission Issues
```bash
# Fix permissions
chmod -R 755 /root/pai
chmod -R 755 ~/.claude
```

---

## 📞 What You Need to Provide

To complete the setup, I'll need:

1. **Odoo Instance Details**
   - URL: `https://your-odoo-instance.com`
   - Database name
   - API username and password

2. **Google Shared Drive IDs**
   - Projects Drive ID
   - Areas Drive ID
   - Resources Drive ID
   - Archives Drive ID

3. **Google OAuth Credentials**
   - Client ID
   - Client Secret
   - Refresh Token (I can help generate this)

4. **AI API Keys** (if you want AI features)
   - Anthropic API key (for Claude)
   - OpenAI API key (for GPT)
   - Perplexity API key (for research)

---

**Ready to start? Let me know if you want me to run the installation steps now, or if you need to gather the credentials first.**
