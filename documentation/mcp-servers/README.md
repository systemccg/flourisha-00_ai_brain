# MCP Servers Documentation

This directory contains documentation about Model Context Protocol (MCP) server integrations, including Playwright for browser testing and Agent Sandboxes.

## Files in This Category

- **[PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md](./PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md)** - Playwright MCP server setup and usage
- **[MCP_SERVER_SETUP.md](./MCP_SERVER_SETUP.md)** - General MCP server setup procedures
- **[AGENT_SANDBOX_MCP.md](./AGENT_SANDBOX_MCP.md)** - Agent sandbox MCP integration

## What is MCP?

Model Context Protocol (MCP) is a standard for integrating external tools and services with Claude. MCP servers enable Claude to:
- Execute code in sandboxes
- Interact with databases
- Access file systems
- Run browser automation
- Execute shell commands

## Available Servers

### Playwright MCP
**Purpose:** Browser automation and testing
**Status:** ✅ Integrated and tested
**Key Capabilities:**
- Launch browser instances
- Navigate to URLs
- Take screenshots
- Test user interactions
- Automated testing workflows

**Quick Start:**
```
Read: PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md
```

### Agent Sandboxes MCP
**Purpose:** Execute code in isolated environments
**Status:** ✅ E2B integration (Phase 1)
**Status:** 🔄 Docker migration (Phase 2 in progress)

See: [../phase2/AGENT_SANDBOX_QUICK_START.md](../phase2/AGENT_SANDBOX_QUICK_START.md)

## Setup Instructions

1. **First time?** See [MCP_SERVER_SETUP.md](./MCP_SERVER_SETUP.md)
2. **Using Playwright?** Read [PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md](./PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md)
3. **Using Agent Sandboxes?** See [../phase2/AGENT_SANDBOX_QUICK_START.md](../phase2/AGENT_SANDBOX_QUICK_START.md)

## Common Tasks

### Run Browser Test
```bash
# Use Playwright MCP to test a web app
# See: PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md
```

### Execute Code in Sandbox
```bash
# Use E2B or Docker sandboxes
# See: ../phase2/AGENT_SANDBOX_QUICK_START.md
```

### Add New MCP Server
1. Install MCP server
2. Configure in Claude Code settings
3. Document in this directory
4. Update this README.md

## Related Documentation

- **Phase 2:** [../phase2/](../phase2/) - Docker sandbox migration
- **Infrastructure:** [../infrastructure/](../infrastructure/) - Server setup
- **Troubleshooting:** [../troubleshooting/](../troubleshooting/) - Common issues

## Troubleshooting

**MCP server not connecting?**
- Check Claude Code settings
- Verify server is running
- See troubleshooting docs

**Playwright tests failing?**
- Review browser logs
- Check screenshot output
- See PLAYWRIGHT_MCP_INTEGRATION_COMPLETE.md

---

**Last Updated:** 2025-12-05
**Maintainer:** Flourisha AI System
