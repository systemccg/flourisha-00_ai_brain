# Knowledge Base

Central repository for N8N workflow migration documentation, standalone scripts, and code implementations.

## Overview

This folder contains all resources related to the N8N workflow migration project, including:
- Workflow migration documentation
- Standalone scripts and utilities
- Code implementations and examples
- Implementation guides
- Troubleshooting and best practices

## Folder Structure

```
knowledge-base/
├── README.md                                 (This file)
├── workflows/                                (N8N workflow documentation)
│   ├── README.md                            (Workflow index)
│   ├── MIGRATION_GUIDE.md                   (How to migrate workflows)
│   ├── WORKFLOW_PATTERNS.md                 (Common patterns)
│   └── [specific workflow docs]
│
├── scripts/                                  (Standalone scripts)
│   ├── README.md                            (Scripts index)
│   ├── n8n_backup.sh                        (Backup scripts)
│   ├── n8n_restore.sh                       (Restore scripts)
│   ├── workflow_export.sh                   (Export workflows)
│   └── [utility scripts]
│
├── code/                                     (Code implementations)
│   ├── README.md                            (Code index)
│   ├── python/                              (Python implementations)
│   ├── nodejs/                              (Node.js implementations)
│   └── [other languages]
│
└── guides/                                   (Implementation guides)
    ├── README.md                            (Guides index)
    ├── GETTING_STARTED.md                   (Quick start)
    ├── BEST_PRACTICES.md                    (N8N best practices)
    ├── TROUBLESHOOTING.md                   (Common issues)
    └── [specific guides]
```

## Quick Start

### For Workflow Migration
1. Read: [workflows/MIGRATION_GUIDE.md](workflows/MIGRATION_GUIDE.md)
2. Review: [workflows/WORKFLOW_PATTERNS.md](workflows/WORKFLOW_PATTERNS.md)
3. Follow: Implementation steps

### For Scripts
1. List available: [scripts/README.md](scripts/README.md)
2. Choose script for your task
3. Run with: `bash scripts/[script_name].sh`

### For Code Implementation
1. Choose language: [code/README.md](code/README.md)
2. Review examples
3. Adapt for your use case

## Files in This Category

### Core Documentation

**[N8N_PATTERN_IMPLEMENTATION.md](./N8N_PATTERN_IMPLEMENTATION.md)** - Complete N8N RAG Pattern Implementation
- Three-table architecture (document_metadata, documents_pg, document_rows)
- Processing pipeline: YouTube, documents, emails → embeddings → knowledge graph
- Version control with content hashing
- Agentic chunking (400-1000 characters, Claude-powered)
- Vector embeddings (OpenAI text-embedding-3-small, 1536 dimensions)
- Knowledge graph storage (Neo4j + Graphiti episodic memory)
- PARA file organization (Google Drive sync)
- Background workers (queue processing, Gmail monitoring)
- Multi-tenant isolation with RLS policies
- Production-ready implementation

### Related Topics
- **Architecture:** [../FLOURISHA_AI_ARCHITECTURE.md](../FLOURISHA_AI_ARCHITECTURE.md)
- **Infrastructure:** [../infrastructure/](../infrastructure/)
- **Troubleshooting:** [../troubleshooting/](../troubleshooting/)

## Creating New Documentation Here

When adding N8N-related content:

1. **Workflows** - Place in `workflows/` folder
2. **Scripts** - Place in `scripts/` folder with `.sh` extension
3. **Code** - Place in `code/[language]/` folder
4. **Guides** - Place in `guides/` folder
5. Update relevant README.md files

## Best Practices

- Keep scripts standalone and well-documented
- Use consistent naming conventions
- Include usage examples
- Document dependencies
- Add troubleshooting sections

## Standards

- Scripts: Bash with `#!/bin/bash` header
- Code: Language-specific standards
- Documentation: Markdown with clear headings
- Naming: UPPER_CASE_WITH_UNDERSCORES for docs, lowercase_with_underscores for scripts

---

**Last Updated:** 2025-12-05
**Purpose:** Centralized N8N workflow migration knowledge base
**Maintainer:** Flourisha AI System
