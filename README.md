# Flourisha AI Brain

**Version:** 1.0
**Created:** 2025-11-19
**Architecture:** PAI v1.2.0 + AI-Agnostic + Obsidian Integration

---

## Overview

The **Flourisha AI Brain** is your centralized AI infrastructure that:
- ✅ Works with **any AI** (Claude, Gemini, Copilot, etc.)
- ✅ Syncs with **Google Drive** for multi-device access
- ✅ Editable in **Obsidian** for beautiful knowledge management
- ✅ Follows **PAI best practices** (Skills-as-Containers)
- ✅ Integrates with **PARA** methodology (`00_` = foundation)

---

## Directory Structure

```
00_AI_Brain/
├── README.md                  # This file
├── skills/                    # PAI Skills (symlinked to AI vendors)
│   ├── CORE/                 # Flourisha identity
│   ├── research/             # Research workflows
│   ├── fabric/               # Fabric patterns
│   └── [other skills]/
│       ├── SKILL.md         # Skill definition
│       ├── workflows/       # Specific workflows
│       ├── assets/          # Templates, resources
│       ├── examples/        # Example outputs
│       └── scripts/         # Helper scripts
├── docs/                     # System documentation
│   ├── README.md            # Documentation index
│   ├── startup/             # Startup procedures
│   ├── security/            # Security docs
│   ├── monitoring/          # Monitoring guides
│   ├── mcp-servers/         # MCP documentation
│   └── [other categories]/
├── scripts/                  # System automation
│   ├── startup/             # Service startup scripts
│   ├── security/            # Security scripts
│   ├── monitoring/          # Monitoring scripts
│   └── backup/              # Backup scripts
└── context/                  # AI context files
    ├── MASTER_CONTEXT.md    # System overview
    └── [other contexts]/
```

---

## Quick Start

### For AI Assistants

**Read this first:**
```markdown
/root/flourisha/00_AI_Brain/context/MASTER_CONTEXT.md
```

**Then explore:**
- Skills: `/root/flourisha/00_AI_Brain/skills/`
- Docs: `/root/flourisha/00_AI_Brain/documentation/README.md`
- Scripts: `/root/flourisha/00_AI_Brain/scripts/`

### For Humans

**In Terminal:**
```bash
# Navigate to AI Brain
cd /root/flourisha/00_AI_Brain

# Browse skills
ls -la skills/

# Read master context
cat context/MASTER_CONTEXT.md

# View docs index
cat docs/README.md
```

**In Obsidian (Windows):**
1. Open Obsidian
2. Navigate to `00_AI_Brain/`
3. Edit skills, docs, or context files
4. Changes auto-sync via Google Drive

---

## Skills Architecture

### Structure (PAI v1.2.0)

Every skill follows this pattern:

```
skill-name/
├── SKILL.md          # Core definition (Tier 2)
│   ├── Frontmatter  # name, description, triggers (Tier 1)
│   └── Body         # Instructions, workflows
├── workflows/        # Specific task workflows (Tier 3)
│   ├── main.md
│   └── advanced.md
├── assets/           # Templates, resources (Tier 3)
│   └── template.md
├── examples/         # Example outputs (Tier 3)
│   └── example.md
└── scripts/          # Helper scripts (Tier 3)
    └── helper.sh
```

### Progressive Disclosure

**Tier 1:** Metadata (always loaded, ~100 tokens)
- Skill name, description, triggers
- Loaded at startup for routing

**Tier 2:** Instructions (loaded when triggered, ~2000 tokens)
- Full SKILL.md with instructions
- Available workflows
- How to use the skill

**Tier 3:** Resources (loaded as needed, 500-2000 tokens each)
- Individual workflow files
- Assets and templates
- Examples and scripts

### Creating New Skills

```bash
# Navigate to skills
cd /root/flourisha/00_AI_Brain/skills

# Create new skill structure
mkdir -p new-skill/{workflows,assets,examples,scripts}

# Create SKILL.md
cat > new-skill/SKILL.md << 'EOF'
---
name: new-skill
description: |
  Brief description.
  USE WHEN user says 'trigger phrase', 'keyword'
---

# New Skill

## Available Workflows
- workflows/main.md - Primary workflow

## Assets
- assets/ - Supporting resources

## Examples
- examples/ - Example outputs
EOF

# Create example README
echo "# Examples for new-skill" > new-skill/examples/README.md
```

---

## Multi-Vendor Support

### How It Works

**Skills live here once:**
```
/root/flourisha/00_AI_Brain/skills/
```

**AI vendors access via symlinks:**
```bash
# Claude
/root/.claude/skills → /root/flourisha/00_AI_Brain/skills/

# Gemini (future)
/root/.gemini/skills → /root/flourisha/00_AI_Brain/skills/
```

**Benefits:**
- ✅ Update skill once, all AIs see it
- ✅ Edit in Obsidian, syncs to server
- ✅ Automatic Google Drive backup
- ✅ Works with any AI tool

### Vendor-Specific Configs

Each AI has its own config directory:
- **Claude:** `/root/.claude/` (hooks, agents, commands)
- **Gemini:** `/root/.gemini/` (future configs)

Shared resources (skills, docs, scripts) in AI Brain.

---

## Google Drive & Obsidian Integration

### Sync Setup

**Locations:**
- **Server:** `/root/flourisha/00_AI_Brain/`
- **Google Drive:** `Flourisha_gDrive/00_AI_Brain/`
- **Obsidian (Windows):** `G:\Shared drives\Flourisha_gDrive\00_AI_Brain\`

**Sync Commands:**
```bash
# Pull from Google Drive
flourisha-pull

# Push to Google Drive
flourisha-push

# Check Drive sync status
rclone lsd Flourisha_gDrive: | grep 00_AI_Brain
```

### Editing in Obsidian

**Workflow:**
1. Open Obsidian on Windows
2. Navigate to `00_AI_Brain/`
3. Edit any skill, doc, or context file
4. Save (auto-syncs to Google Drive)
5. Google Drive syncs to server
6. AI sees updated content immediately

**Benefits:**
- Beautiful markdown editor
- Graph view of relationships
- Powerful search across all docs
- Templates for new skills
- Multi-device access

---

## Documentation

### Start Here

**[`documentation/DOCUMENTATION_MAP.md`](documentation/DOCUMENTATION_MAP.md)** - Master documentation index

### Document Processing (New - 2025-12-06)

| Service | Description |
|---------|-------------|
| [Document Processor](documentation/services/DOCUMENT_PROCESSOR.md) | Extract text from PDFs, images |
| [Knowledge Ingestion](documentation/services/KNOWLEDGE_INGESTION.md) | Pipeline to all stores |
| [Extraction Backends](documentation/services/EXTRACTION_BACKENDS.md) | Claude vs Docling backends |

### Knowledge Stores

| Store | Description |
|-------|-------------|
| [Three-Store Overview](documentation/knowledge-stores/OVERVIEW.md) | Vector + Graph + Whole |
| [Database Schema](documentation/database/DATABASE_SCHEMA.md) | Supabase tables |
| [Vector Store](documentation/database/VECTOR_STORE.md) | pgvector embeddings |
| [Graph Store](documentation/knowledge-stores/GRAPH_STORE.md) | Neo4j/Graphiti |

### Other Guides

- **Startup:** [`documentation/startup/services.md`](documentation/startup/services.md)
- **Security:** [`documentation/security/scanning.md`](documentation/security/scanning.md)
- **Monitoring:** [`documentation/monitoring/overview.md`](documentation/monitoring/overview.md)

### Context Files

**[`context/MASTER_CONTEXT.md`](context/MASTER_CONTEXT.md)** - System overview
- Quick facts
- Key services
- Navigation
- Contact info

---

## Scripts

### Startup Scripts

**[`scripts/startup/start_services_lean.py`](scripts/startup/start_services_lean.py)**
- Selective service startup
- Full documentation in file

**Usage:**
```bash
# Start everything
python3 /root/flourisha/00_AI_Brain/scripts/startup/start_services_lean.py

# Start specific service
python3 /root/flourisha/00_AI_Brain/scripts/startup/start_services_lean.py --services neo4j

# List available services
python3 /root/flourisha/00_AI_Brain/scripts/startup/start_services_lean.py --list
```

### Other Scripts

- **Security:** `scripts/security/` - Security scanning, audits
- **Monitoring:** `scripts/monitoring/` - Health checks, monitoring
- **Backup:** `scripts/backup/` - Backup automation

---

## Maintenance

### Updating Skills

**On Server:**
```bash
cd /root/flourisha/00_AI_Brain/skills/skill-name
nano SKILL.md
flourisha-push  # Sync to Google Drive
```

**In Obsidian:**
1. Edit skill in Obsidian
2. Save (auto-syncs)
3. Done!

### Adding Documentation

**On Server:**
```bash
cd /root/flourisha/00_AI_Brain/documentation/category
nano new-doc.md
flourisha-push
```

**In Obsidian:**
1. Create new note in docs/
2. Write documentation
3. Auto-syncs to server

### Version Control

**Google Drive provides automatic versioning:**
- File history available in Google Drive
- Can restore previous versions
- No manual git commits needed for docs/skills

---

## Architecture Principles

### Single Source of Truth
- Skills stored once in AI Brain
- Symlinked to vendor configs
- Edit once, works everywhere

### Progressive Disclosure
- Small metadata always loaded
- Full instructions loaded on trigger
- Resources loaded as needed

### Vendor Isolation
- Shared resources in AI Brain
- Vendor-specific configs separate
- Clean boundaries

### PARA Integration
- `00_AI_Brain` = System foundation
- Part of Flourisha knowledge system
- Syncs with projects, areas, resources

---

## Quick Commands

```bash
# Navigate
cd /root/flourisha/00_AI_Brain

# List skills
ls -la skills/

# Read master context
cat context/MASTER_CONTEXT.md

# View docs
cat docs/README.md

# Sync to Google Drive
flourisha-push

# Pull from Google Drive
flourisha-pull

# Search everything
grep -r "search term" /root/flourisha/00_AI_Brain/
```

---

## Support

### For AI Assistants

1. Always read [`context/MASTER_CONTEXT.md`](context/MASTER_CONTEXT.md) first
2. Reference specific docs as needed
3. Don't load everything at once

### For Humans

1. Browse in Obsidian for best experience
2. Use terminal for quick edits
3. Google Drive keeps everything backed up

---

## Version History

- **v1.0** (2025-11-19) - Initial AI Brain structure
  - Skills-as-Containers (PAI v1.2.0)
  - AI-agnostic architecture
  - Google Drive + Obsidian integration
  - Multi-vendor support via symlinks

---

**Questions?** All documentation is in [`documentation/`](docs/README.md)
