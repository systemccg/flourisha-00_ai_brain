# Flourisha AI Architecture
## PAI Best Practices + AI-Agnostic + Obsidian/Google Drive Integration

**Created:** 2025-11-19 (Updated 2025-12-06)
**Purpose:** Unified AI infrastructure that syncs with Google Drive and Obsidian

---

## Document Processing Architecture (New - 2025-12-06)

The AI Brain now includes a comprehensive document processing pipeline:

```
Document → DocumentProcessor → ExtractionBackend → KnowledgeIngestionService
                                    │                        │
                              ┌─────┴─────┐        ┌─────────┼─────────┐
                              │           │        │         │         │
                           Claude     Docling   Vector    Graph     Whole
                          (Primary)  (Fallback)  Store    Store     Store
```

### Key Services
- **DocumentProcessor** - Pluggable extraction with fallback support
- **KnowledgeIngestionService** - Orchestrates storage to all three stores
- **Extraction Backends** - Claude (accurate) and Docling (free/batch)

### Documentation
- [Document Processor](services/DOCUMENT_PROCESSOR.md)
- [Knowledge Ingestion](services/KNOWLEDGE_INGESTION.md)
- [Extraction Backends](services/EXTRACTION_BACKENDS.md)
- [Three-Store Overview](knowledge-stores/OVERVIEW.md)

---

## Core Innovation: AI Brain in Flourisha

**Key Insight:** By placing AI infrastructure in `/root/flourisha/00_AI_Brain/`, we get:
- ✅ **Syncs with Google Drive** - Access AI docs from any device
- ✅ **Available in Obsidian** - Edit skills and docs in Obsidian
- ✅ **PARA-organized** - `00_` prefix = system/foundation layer
- ✅ **Versioned** - Google Drive provides automatic versioning
- ✅ **Backed up** - Automatic cloud backup
- ✅ **Multi-device** - Edit skills on laptop, run on server

---

## The Complete Structure

```
/root/
├── flourisha/                         # Google Drive sync + Obsidian
│   ├── 01f_Flourisha_Projects/       # PARA: Projects
│   ├── 02f_Flourisha_Areas/          # PARA: Areas
│   ├── 03f_Flourisha_Resources/      # PARA: Resources
│   ├── 04f_Flourisha_Archives/       # PARA: Archives
│   │
│   └── 00_AI_Brain/                  # ⭐ AI INFRASTRUCTURE (NEW)
│       ├── skills/                   # ⭐ PAI Skills (canonical)
│       │   ├── CORE/                # System identity (Flourisha)
│       │   │   └── SKILL.md
│       │   ├── research/            # Research workflows
│       │   │   ├── SKILL.md        # Skill definition
│       │   │   ├── workflows/      # Specific workflows
│       │   │   │   ├── quick.md
│       │   │   │   ├── standard.md
│       │   │   │   └── extensive.md
│       │   │   ├── assets/         # Templates, resources
│       │   │   │   └── search-template.md
│       │   │   └── examples/       # ⭐ Example outputs
│       │   │       └── example-research-report.md
│       │   ├── fabric/
│       │   └── [other skills]/
│       │       ├── SKILL.md
│       │       ├── workflows/
│       │       ├── assets/
│       │       ├── examples/       # ⭐ Always include
│       │       └── scripts/
│       │
│       ├── docs/                    # System documentation
│       │   ├── README.md           # Master index
│       │   ├── SYSTEM_STARTUP_GUIDE.md
│       │   ├── startup/
│       │   │   ├── services.md
│       │   │   ├── mcp-servers.md
│       │   │   └── verification.md
│       │   ├── security/
│       │   │   ├── overview.md
│       │   │   ├── scanning.md
│       │   │   ├── firewall.md
│       │   │   └── protocols.md
│       │   ├── monitoring/
│       │   │   ├── overview.md
│       │   │   ├── netdata.md
│       │   │   ├── uptime-kuma.md
│       │   │   └── portainer.md
│       │   └── mcp-servers/
│       │       ├── overview.md
│       │       ├── server-list.md
│       │       └── troubleshooting.md
│       │
│       ├── scripts/                 # System automation
│       │   ├── startup/
│       │   │   ├── start_services_lean.py
│       │   │   └── start_mcp_servers.sh
│       │   ├── security/
│       │   │   ├── run_security_scan.sh
│       │   │   └── audit_system.sh
│       │   ├── monitoring/
│       │   │   └── health_check.sh
│       │   └── backup/
│       │       └── backup_configs.sh
│       │
│       └── context/                 # AI context files
│           ├── MASTER_CONTEXT.md   # System overview
│           ├── SERVICES.md         # Services context
│           ├── SECURITY.md         # Security context
│           └── MCP_SERVERS.md      # MCP context
│
├── .claude/                         # Claude-specific configs
│   ├── settings.json
│   ├── .mcp.json
│   ├── skills/                     # ⭐ SYMLINK to flourisha
│   │   └── [symlink → /root/flourisha/00_AI_Brain/skills/]
│   ├── hooks/                      # Claude hooks
│   ├── agents/                     # Claude agents
│   ├── commands/                   # Slash commands
│   └── docs/                       # Claude-specific docs
│
├── .gemini/                        # Gemini-specific (future)
│   ├── config.json
│   └── skills/                     # ⭐ SYMLINK to flourisha
│       └── [symlink → /root/flourisha/00_AI_Brain/skills/]
│
├── scripts/                        # Infrastructure scripts only
│   └── cloudflare_firewall_setup.sh
│
└── [projects]/                     # Your projects
    └── local-ai-packaged/
        ├── CONTEXT.md             # Project context
        └── [project files]
```

---

## Why This Structure Works

### 1. Flourisha Integration
```
/root/flourisha/00_AI_Brain/
```

**Benefits:**
- ✅ **Google Drive sync** - Edit skills on any device
- ✅ **Obsidian access** - Use Obsidian to manage skills/docs
- ✅ **PARA alignment** - `00_` prefix = foundational system
- ✅ **Automatic backup** - Google Drive provides versioning
- ✅ **Cross-device** - Write skill on laptop, runs on server
- ✅ **Knowledge management** - AI docs part of PKM system

**PARA Context:**
- `01f_Projects` - Active projects
- `02f_Areas` - Ongoing responsibilities
- `03f_Resources` - Reference materials
- `04f_Archives` - Completed items
- `00_AI_Brain` - **System foundation (AI infrastructure)**

### 2. Complete Skill Structure

**From PAI (Daniel's best practices):**
```
skill-name/
├── SKILL.md          # Tier 2: Skill definition
├── workflows/        # Tier 3: Specific workflows
├── assets/           # Tier 3: Templates, resources
├── examples/         # ⭐ Example outputs (you added this)
└── scripts/          # Tier 3: Helper scripts
```

**Examples Directory Purpose:**
- Show what good output looks like
- Templates for complex formats
- Reference implementations
- Training examples for AI

**Example:**
```
/root/flourisha/00_AI_Brain/skills/research/examples/
├── example-quick-research.md       # Shows quick research output
├── example-comprehensive-report.md # Shows extensive research format
└── example-citation-style.md       # Shows proper citations
```

### 3. Symlinks for Vendor Compatibility

```bash
# Claude reads skills via symlink
/root/.claude/skills/ → /root/flourisha/00_AI_Brain/skills/

# Gemini reads skills via symlink (future)
/root/.gemini/skills/ → /root/flourisha/00_AI_Brain/skills/

# Actual skills stored once in Flourisha
/root/flourisha/00_AI_Brain/skills/
```

**Why symlinks:**
- ✅ Single source of truth (skills in Flourisha)
- ✅ Each AI vendor can find skills in expected location
- ✅ Update once in Flourisha, all AIs see changes
- ✅ Skills backed up to Google Drive automatically

---

## Progressive Disclosure (PAI Pattern)

### Tier 1: Metadata (Always Loaded)
```yaml
---
name: research
description: Multi-source research using perplexity, claude, gemini agents.
  USE WHEN user says 'research', 'find information', 'investigate'
---
```
**Location:** Skill SKILL.md frontmatter
**Size:** ~100 tokens
**When:** Loaded at startup for routing

### Tier 2: Instructions (Loaded When Triggered)
```markdown
# Research Skill

## Available Workflows
- Quick: 3 agents (5-10 min)
- Standard: 9 agents (15-20 min)
- Extensive: 24 agents (30-40 min)

## How It Works
[Full instructions]
```
**Location:** Skill SKILL.md body
**Size:** ~2000 tokens
**When:** Loaded when skill triggered

### Tier 3: Resources (Loaded As Needed)
```
workflows/quick.md           # Load when quick research
workflows/extensive.md       # Load when extensive research
assets/search-template.md    # Load when needed
examples/example-report.md   # Load for reference
```
**Location:** Skill subdirectories
**Size:** 500-2000 tokens each
**When:** Loaded only when accessed

---

## Obsidian Benefits

### Edit Skills in Obsidian

Since `/root/flourisha` syncs with Obsidian on your Windows machine (`G:\Shared drives\Flourisha_gDrive`):

**You can:**
1. **Edit skills in Obsidian** - Beautiful markdown editor
2. **Use Obsidian templates** - Create new skills from templates
3. **Link between skills** - Use `[[wikilinks]]` for cross-references
4. **Search across skills** - Obsidian's powerful search
5. **Version control** - See skill history via Google Drive
6. **Visual skill management** - Graph view of skill relationships

**Example Obsidian Workflow:**
```
1. Open Obsidian on Windows
2. Navigate to 00_AI_Brain/skills/
3. Edit research/SKILL.md
4. Save (auto-syncs to Google Drive)
5. Google Drive syncs to server
6. Claude on server sees updated skill
7. Skill immediately available
```

### Documentation in Obsidian

Your system docs in Obsidian:
```
00_AI_Brain/documentation/
├── SYSTEM_STARTUP_GUIDE.md  ← Read in Obsidian
├── startup/
│   ├── services.md          ← Link from Obsidian daily note
│   └── mcp-servers.md       ← Use Obsidian templates
└── security/
    └── overview.md          ← Searchable in Obsidian
```

**Benefits:**
- Use Obsidian daily notes to link to startup procedures
- Create templates for new documentation
- Search all docs instantly
- Visual graph of documentation relationships

---

## Implementation Plan

### Phase 1: Create Flourisha AI Brain Structure
```bash
# Create 00_AI_Brain directory structure
mkdir -p /root/flourisha/00_AI_Brain/{skills,docs,scripts,context}

# Create docs subdirectories
mkdir -p /root/flourisha/00_AI_Brain/documentation/{startup,security,monitoring,mcp-servers}

# Create scripts subdirectories
mkdir -p /root/flourisha/00_AI_Brain/scripts/{startup,security,monitoring,backup}
```

### Phase 2: Move Existing Skills
```bash
# Move skills from .claude to Flourisha
mv /root/.claude/skills/* /root/flourisha/00_AI_Brain/skills/

# Create symlink for Claude
rm -rf /root/.claude/skills
ln -s /root/flourisha/00_AI_Brain/skills /root/.claude/skills

# Verify symlink
ls -la /root/.claude/skills
# Should show: skills -> /root/flourisha/00_AI_Brain/skills
```

### Phase 3: Add Examples to Skills
```bash
# Add examples/ to each skill
cd /root/flourisha/00_AI_Brain/skills

for skill in */; do
  mkdir -p "$skill/examples"
  echo "# Example outputs for ${skill%/} skill" > "$skill/examples/README.md"
done
```

### Phase 4: Move Documentation
```bash
# Move system docs to Flourisha AI Brain
# From various locations to central location

# Startup docs
mv /root/local-ai-packaged/START_SERVICES_GUIDE.md \
   /root/flourisha/00_AI_Brain/documentation/startup/services.md

# Monitoring docs
mv /root/monitoring/MONITORING_TOOLS_GUIDE.md \
   /root/flourisha/00_AI_Brain/documentation/monitoring/overview.md

# Security docs
mv /root/monitoring/LYNIS_SECURITY_AUDIT.md \
   /root/flourisha/00_AI_Brain/documentation/security/scanning.md
```

### Phase 5: Move Scripts
```bash
# Move AI-managed scripts
mv /root/local-ai-packaged/start_services_lean.py \
   /root/flourisha/00_AI_Brain/scripts/startup/

# Update script references in docs
```

### Phase 6: Create Context Files
```bash
# Create master context
cat > /root/flourisha/00_AI_Brain/context/MASTER_CONTEXT.md << 'EOF'
# Flourisha System Context

## Quick Facts
- Server: Contabo VPS
- AI Infrastructure: /root/flourisha/00_AI_Brain/
- Skills: /root/flourisha/00_AI_Brain/skills/
- Docs: /root/flourisha/00_AI_Brain/documentation/

## Key Services
[Services list]

## Startup
See: /root/flourisha/00_AI_Brain/documentation/SYSTEM_STARTUP_GUIDE.md

## Security
See: /root/flourisha/00_AI_Brain/documentation/security/overview.md
EOF
```

### Phase 7: Update Project References
```bash
# Update CLAUDE.md → CONTEXT.md in projects
mv /root/local-ai-packaged/CLAUDE.md \
   /root/local-ai-packaged/CONTEXT.md

# Update references to point to Flourisha AI Brain
sed -i 's|/root/ai/|/root/flourisha/00_AI_Brain/|g' \
   /root/local-ai-packaged/CONTEXT.md
```

### Phase 8: Google Drive Sync Verification
```bash
# Verify Google Drive sync
rclone lsd Flourisha_gDrive: | grep 00_AI_Brain

# Should show:
# -1 2025-11-19 00:00:00    -1 00_AI_Brain

# Sync to Google Drive
cd /root
flourisha-push  # Your alias for: rclone sync flourisha/ Flourisha_gDrive:
```

---

## Skill Structure Template

When creating new skills, use this structure:

```
/root/flourisha/00_AI_Brain/skills/new-skill/
├── SKILL.md                  # Required: Skill definition
│   ├── Frontmatter          # Tier 1: name, description, triggers
│   └── Body                 # Tier 2: How to use, workflows available
├── workflows/               # Required: At least one workflow
│   ├── primary.md          # Main workflow
│   └── advanced.md         # Additional workflows
├── assets/                  # Optional: Templates, resources
│   ├── template.md
│   └── reference.md
├── examples/                # Required: Example outputs
│   ├── README.md
│   └── example-output.md
└── scripts/                 # Optional: Helper scripts
    └── helper.sh
```

**Minimum Required:**
- ✅ `SKILL.md` with frontmatter
- ✅ `workflows/` with at least one workflow
- ✅ `examples/` with at least README.md

**Recommended:**
- ✅ `assets/` for templates
- ✅ Multiple example outputs
- ✅ `scripts/` if automation needed

---

## Example: Research Skill (Complete)

```
/root/flourisha/00_AI_Brain/skills/research/
├── SKILL.md
│   # Frontmatter
│   ---
│   name: research
│   description: Multi-source research. USE WHEN user says 'research', 'find info'
│   ---
│
│   # Available Workflows
│   - workflows/quick.md - 3 agents, 5-10 min
│   - workflows/standard.md - 9 agents, 15-20 min
│   - workflows/extensive.md - 24 agents, 30-40 min
│
├── workflows/
│   ├── quick.md
│   │   # Quick Research (3 Agents)
│   │   Launch 3 parallel agents...
│   │
│   ├── standard.md
│   │   # Standard Research (9 Agents)
│   │   Launch 9 parallel agents...
│   │
│   └── extensive.md
│       # Extensive Research (24 Agents)
│       Launch 24 parallel agents with be-creative skill...
│
├── assets/
│   ├── research-template.md
│   │   # Research Report Template
│   │   ## Executive Summary
│   │   ## Key Findings...
│   │
│   └── citation-style.md
│       # Citation Guidelines
│       Use APA format...
│
└── examples/
    ├── README.md
    │   # Research Skill Examples
    │   This directory contains example outputs...
    │
    ├── quick-research-example.md
    │   # Quick Research: Murphy Beds
    │   **Query:** murphy beds market analysis
    │   **Mode:** Quick (3 agents)
    │   **Duration:** 8 minutes
    │   ## Summary...
    │
    └── extensive-research-example.md
        # Extensive Research: AI Trends 2025
        **Query:** artificial intelligence trends 2025
        **Mode:** Extensive (24 agents)
        **Duration:** 35 minutes
        ## Executive Summary...
```

---

## Obsidian Setup

### Add AI Brain to Obsidian Vault

**On Windows (Obsidian):**
1. Obsidian → Settings → Files & Links
2. Vault location: `G:\Shared drives\Flourisha_gDrive`
3. AI Brain visible at: `00_AI_Brain/`
4. Can now edit skills in Obsidian!

### Obsidian Templates for Skills

**Create:** `00_AI_Brain/templates/new-skill-template.md`

```markdown
---
name: {{skill-name}}
description: |
  {{description}}
  USE WHEN user says {{triggers}}
---

# {{Skill Name}} Skill

## Purpose
{{What this skill does}}

## Available Workflows

- **workflows/main.md** - {{Description}}

## Assets

- **assets/** - {{What assets are available}}

## Examples

- **examples/** - {{Example outputs}}

---

**Created:** {{date}}
**Updated:** {{date}}
```

**Use in Obsidian:**
1. Create new note in `00_AI_Brain/skills/`
2. Insert template
3. Fill in placeholders
4. Create workflows/ directory
5. Add examples/
6. Saves to Google Drive
7. Syncs to server
8. Claude immediately sees new skill!

---

## Benefits Summary

### From PAI (Daniel's Architecture) ✅
- ✅ Skills-as-Containers
- ✅ Progressive Disclosure (3-tier)
- ✅ workflows/, assets/, scripts/ structure
- ✅ **examples/** directory (your addition)
- ✅ Natural language routing
- ✅ Agent orchestration

### AI-Agnostic ✅
- ✅ Works with Claude, Gemini, Copilot
- ✅ CONTEXT.md (not CLAUDE.md)
- ✅ Symlinks for vendor compatibility
- ✅ Centralized documentation

### Flourisha Integration 🆕
- ✅ **Google Drive sync** - Multi-device access
- ✅ **Obsidian integration** - Edit in beautiful UI
- ✅ **PARA alignment** - `00_AI_Brain` = foundation
- ✅ **Automatic backup** - Cloud-based
- ✅ **PKM integration** - AI docs in knowledge base
- ✅ **Version control** - Google Drive versions

---

## Quick Commands

```bash
# Navigate to AI Brain
cd /root/flourisha/00_AI_Brain

# List all skills
ls -la skills/

# Create new skill
mkdir -p skills/new-skill/{workflows,assets,examples,scripts}

# Edit skill in terminal
nano skills/research/SKILL.md

# Sync to Google Drive
flourisha-push

# Pull from Google Drive (after editing in Obsidian)
flourisha-pull

# Verify Claude can see skills
ls -la /root/.claude/skills  # Should show symlink
```

---

## Next Steps

1. **Review this architecture** - Does it meet your needs?
2. **Phase 1: Create structure** - Set up 00_AI_Brain/
3. **Phase 2: Move skills** - Migrate with symlinks
4. **Phase 3: Add examples/** - To all existing skills
5. **Phase 4: Move docs** - Centralize in 00_AI_Brain/documentation/
6. **Phase 5: Test in Obsidian** - Edit a skill, verify sync
7. **Phase 6: Update references** - All projects point to new location
8. **Phase 7: Sync to Drive** - Push to Google Drive

**Ready to implement?**
