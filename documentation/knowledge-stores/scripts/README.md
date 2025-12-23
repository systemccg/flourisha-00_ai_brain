# N8N Utility Scripts

Standalone scripts for N8N operations, backups, migrations, and maintenance.

## Available Scripts

### Backup & Restore
- `n8n_backup.sh` (coming soon) - Backup N8N workflows and data
- `n8n_restore.sh` (coming soon) - Restore N8N workflows and data

### Workflow Management
- `workflow_export.sh` (coming soon) - Export workflows to files
- `workflow_import.sh` (coming soon) - Import workflows from files

## Usage

All scripts are standalone and can be run with:
```bash
bash scripts/[script_name].sh [options]
```

## Script Standards

All scripts in this folder:
- Include `#!/bin/bash` header
- Have clear usage documentation
- Include error handling
- Support `--help` flag
- Are standalone (no external dependencies except standard unix tools)

---

**Last Updated:** 2025-12-05
**Purpose:** N8N utility scripts
