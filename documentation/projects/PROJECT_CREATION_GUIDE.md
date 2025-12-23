# Project Creation Guide

**Location:** `/root/flourisha/00_AI_Brain/documentation/projects/`
**Created:** 2025-11-20
**Version:** 1.0

## Overview

The Flourisha project creation system provides standardized templates and automation for creating new projects following the PARA methodology.

## Quick Start

### Using the Script (Recommended)

```bash
# Interactive mode
/root/flourisha/00_AI_Brain/scripts/projects/new_project.sh

# Quick mode with parameters
/root/flourisha/00_AI_Brain/scripts/projects/new_project.sh \
  --template client \
  --name "Acme Corp Consulting" \
  --quick
```

### Manual Creation

1. Navigate to templates:
   ```bash
   cd /root/flourisha/03f_Flourisha_Resources/Project_Templates
   ```

2. Copy desired template to Projects folder:
   ```bash
   cp -r client-project /root/flourisha/01f_Flourisha_Projects/my-new-project
   ```

3. Customize the files manually

4. Sync to Google Drive:
   ```bash
   flourisha-bisync
   ```

## Available Templates

### 1. Client Project (`client-project/`)

**Use For:**
- Client consulting work
- Service delivery projects
- Contract-based engagements

**Includes:**
- Project brief and scope
- Client information tracking
- Deliverables management
- Meeting notes
- Invoicing and contracts folders

**Files:**
- `README.md` - Project overview
- `MEETINGS.md` - Meeting notes
- `DELIVERABLES.md` - Deliverable tracking
- `INVOICES.md` - Payment tracking
- `contracts/` - Contract storage

---

### 2. Research Project (`research-project/`)

**Use For:**
- Research initiatives
- Competitive analysis
- Market research
- Deep-dive investigations

**Includes:**
- Research questions framework
- Source tracking
- Findings documentation
- Analysis synthesis

**Files:**
- `README.md` - Research overview
- `SOURCES.md` - Source tracking and bibliography
- `FINDINGS.md` - Research findings
- `ANALYSIS.md` - Analysis and synthesis
- `data/` - Raw data storage
- `reports/` - Research reports

---

### 3. Development Project (`development-project/`)

**Use For:**
- Software development
- Technical implementations
- Code projects

**Includes:**
- Technical specifications
- Architecture decisions (ADRs)
- Implementation tracking
- Testing strategy
- Deployment procedures

**Files:**
- `README.md` - Project overview
- `SPECS.md` - Technical specifications
- `ARCHITECTURE.md` - Architecture decisions
- `TESTING.md` - Testing strategy
- `DEPLOYMENT.md` - Deployment guide
- `src/` - Source code
- `docs/` - Documentation
- `tests/` - Test files

---

### 4. General Project (`general-project/`)

**Use For:**
- Projects that don't fit other categories
- Flexible/miscellaneous work

**Includes:**
- Basic project structure
- Minimal assumptions

**Files:**
- `README.md` - Project overview
- `TASKS.md` - Task tracking
- `NOTES.md` - Running notes
- `RESOURCES.md` - Links and references

## Script Usage

### Interactive Mode

```bash
/root/flourisha/00_AI_Brain/scripts/projects/new_project.sh
```

The script will prompt you for:
1. Template selection (1-4 or name)
2. Project name
3. Git initialization (optional)
4. Google Drive sync (optional)

### Command-Line Mode

```bash
# Specify template and name
/root/flourisha/00_AI_Brain/scripts/projects/new_project.sh \
  --template research \
  --name "Q4 Market Analysis"

# Quick mode (skips optional prompts)
/root/flourisha/00_AI_Brain/scripts/projects/new_project.sh \
  -t development \
  -n "API Redesign" \
  --quick
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message |
| `--template TYPE` | `-t TYPE` | Template type (client/research/development/general) |
| `--name NAME` | `-n NAME` | Project name |
| `--quick` | `-q` | Quick mode (skip optional prompts) |

## What The Script Does

1. **Creates Project Structure**
   - Copies template to `01f_Flourisha_Projects/[project-name]/`
   - Sanitizes folder name (lowercase, hyphens, no special chars)

2. **Customizes Templates**
   - Replaces `[PROJECT NAME]` with actual project name
   - Replaces `[DATE]` with current date
   - Updates all markdown files

3. **Optional Git Initialization**
   - Initializes git repository
   - Creates `.gitignore`
   - Makes initial commit

4. **Optional Google Drive Sync**
   - Runs `flourisha-bisync` to sync project to Google Drive
   - Makes project available in Obsidian

## Template Placeholders

Templates use these placeholders that get automatically replaced:

| Placeholder | Replaced With | Example |
|-------------|---------------|---------|
| `[PROJECT NAME]` | Your project name | "Acme Corp Consulting" |
| `[CLIENT NAME]` | Your project name | "Acme Corp" |
| `[DATE]` | Current date | "2025-11-20" |

Additional placeholders to fill manually:
- `[EMAIL]`, `[PHONE]`, `[URL]` - Contact information
- `[AMOUNT]` - Financial amounts
- `[Description]` - Custom descriptions

## Project Naming Best Practices

**Good Names:**
- "acme-corp-consulting" (descriptive, clear)
- "q4-market-research" (includes timeframe)
- "api-v2-redesign" (includes version)

**Avoid:**
- "project1" (too generic)
- "temp" or "test" (unclear purpose)
- Special characters or spaces (use hyphens)

## Folder Structure

After creation, your project structure will look like:

```
01f_Flourisha_Projects/
└── my-project/
    ├── README.md
    ├── [Template-specific files]
    └── [Template-specific folders]
```

## Customizing Templates

### Modifying Existing Templates

1. Edit template files in:
   ```
   /root/flourisha/03f_Flourisha_Resources/Project_Templates/
   ```

2. Changes will apply to all future projects created from that template

3. Sync changes:
   ```bash
   flourisha-bisync
   ```

### Creating New Templates

1. Create new folder in templates directory:
   ```bash
   cd /root/flourisha/03f_Flourisha_Resources/Project_Templates
   mkdir custom-template
   ```

2. Add template files with placeholders

3. Update script if you want it in the menu:
   - Edit `/root/flourisha/00_AI_Brain/scripts/projects/new_project.sh`
   - Add your template to `list_templates()` function

4. Sync to Google Drive:
   ```bash
   flourisha-bisync
   ```

## Workflow Integration

### With Obsidian

1. Create project using script
2. Run `flourisha-bisync` (if not auto-synced)
3. Open Obsidian on Windows
4. Navigate to `01f_Flourisha_Projects/[your-project]`
5. Edit and enhance project files in Obsidian
6. Changes sync automatically via Google Drive

### With Git

If you initialized git during project creation:

```bash
cd /root/flourisha/01f_Flourisha_Projects/my-project

# Make changes
git add .
git commit -m "Update project status"

# Add remote and push (if needed)
git remote add origin [repo-url]
git push -u origin main
```

## PARA Methodology

Projects in the PARA system are:

- **Time-Bound:** Have a specific end goal or completion date
- **Outcome-Focused:** Working toward specific deliverables
- **Active:** Currently being worked on

### When to Archive

Move to `04f_Flourisha_Archives/` when:
- Project objectives are met
- Project is cancelled/abandoned
- Project inactive for 90+ days
- All deliverables completed and payments received (client projects)

## Troubleshooting

### Script Won't Run

**Issue:** Permission denied

**Solution:**
```bash
chmod +x /root/flourisha/00_AI_Brain/scripts/projects/new_project.sh
```

---

### Project Already Exists

**Issue:** "Project 'name' already exists"

**Solution:**
1. Choose a different name, or
2. Delete/rename existing project

---

### Sync to Google Drive Fails

**Issue:** flourisha-bisync errors

**Solution:**
1. Check rclone configuration:
   ```bash
   rclone listremotes
   ```

2. Run sync manually later:
   ```bash
   flourisha-bisync
   ```

---

### Template Not Found

**Issue:** Template directory doesn't exist

**Solution:**
```bash
# Verify templates exist
ls -la /root/flourisha/03f_Flourisha_Resources/Project_Templates/

# If missing, pull from Google Drive
flourisha-bisync
```

## Examples

### Example 1: Client Project

```bash
$ /root/flourisha/00_AI_Brain/scripts/projects/new_project.sh

Select template (1-4 or name): 1
Enter project name: Acme Corp Website Redesign
Initialize git repository? (y/n): y
Sync to Google Drive now? (y/n): y

✓ Project Created Successfully!
Location: /root/flourisha/01f_Flourisha_Projects/acme-corp-website-redesign
```

### Example 2: Research Project (Quick Mode)

```bash
$ /root/flourisha/00_AI_Brain/scripts/projects/new_project.sh \
  -t research \
  -n "Competitor Analysis Q4" \
  -q

✓ Template: research-project
✓ Project name: Competitor Analysis Q4
✓ Project structure created
✓ Template customized
✓ Project Created Successfully!
```

### Example 3: Development Project

```bash
$ /root/flourisha/00_AI_Brain/scripts/projects/new_project.sh \
  --template development \
  --name "Payment API Integration"

# Follow prompts...
# Result: Fully set up development project with specs, architecture docs, etc.
```

## Advanced Usage

### Batch Creation

Create multiple projects programmatically:

```bash
#!/bin/bash
projects=(
    "client:Project A"
    "research:Market Study B"
    "development:Feature C"
)

for project in "${projects[@]}"; do
    template=$(echo $project | cut -d: -f1)
    name=$(echo $project | cut -d: -f2)

    /root/flourisha/00_AI_Brain/scripts/projects/new_project.sh \
        -t "$template" \
        -n "$name" \
        -q
done
```

### Custom Post-Creation Actions

Add a post-creation hook by editing the script's `main()` function:

```bash
# After create_project() call, add:
if [ "$template" = "development-project" ]; then
    # Initialize npm/bun project
    cd "$project_path"
    bun init -y
fi
```

## Best Practices

1. **Name Descriptively:** Use clear, specific project names
2. **Use Appropriate Template:** Match template to project type
3. **Customize Immediately:** Fill in template placeholders right away
4. **Sync Regularly:** Run `flourisha-bisync` to keep Google Drive updated
5. **Archive When Done:** Move completed projects to Archives
6. **Update Templates:** Improve templates based on experience

## Related Documentation

- [PARA Methodology](../PARA_METHODOLOGY.md)
- [Google Drive Sync](../sync/GOOGLE_DRIVE_SYNC.md)
- [Obsidian Integration](../obsidian/OBSIDIAN_INTEGRATION.md)
- [Project Templates README](/root/flourisha/03f_Flourisha_Resources/Project_Templates/README.md)

---

**Created:** 2025-11-20
**Last Updated:** 2025-11-20
**Maintained By:** Greg Wasmuth / Flourisha AI
