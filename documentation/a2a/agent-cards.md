# Agent Card Specification

**Version:** 1.0.0
**A2A Protocol:** 0.1.0
**Created:** 2025-11-19

---

## Overview

Agent Cards are JSON manifests that declare an agent's capabilities, skills, and interface according to the A2A protocol. They enable discovery, capability matching, and standardized communication.

---

## Required Structure

### Minimal Agent Card

```json
{
  "protocolVersion": "0.1.0",
  "provider": {
    "name": "Flourisha AI Brain",
    "url": "https://flourisha.local",
    "organization": "Personal AI Infrastructure"
  },
  "agent": {
    "id": "agent-id",
    "name": "Agent Name",
    "version": "1.0.0",
    "description": "What this agent does",
    "url": "file:///root/flourisha/00_AI_Brain/agents/agent-id"
  },
  "capabilities": {
    "streaming": false,
    "pushNotifications": false,
    "stateTransitionHistory": false,
    "extensions": []
  },
  "skills": [],
  "transport": {
    "preferred": "internal",
    "endpoints": {
      "internal": "file:///root/flourisha/00_AI_Brain/agents/agent-id"
    }
  },
  "securitySchemes": {},
  "metadata": {}
}
```

---

## Field Descriptions

### protocolVersion
**Required**
A2A protocol version this agent card conforms to.

```json
"protocolVersion": "0.1.0"
```

### provider
**Required**
Information about who provides this agent.

```json
"provider": {
  "name": "Flourisha AI Brain",
  "url": "https://flourisha.local",
  "organization": "Personal AI Infrastructure"
}
```

### agent
**Required**
Core agent identity and metadata.

```json
"agent": {
  "id": "gemini-researcher",           // Unique identifier
  "name": "Gemini Researcher",         // Human-readable name
  "version": "1.0.0",                  // Semantic version
  "description": "Multi-perspective research...",  // What it does
  "url": "file:///root/flourisha/..."  // Location
}
```

### capabilities
**Required**
Declares agent's technical capabilities.

```json
"capabilities": {
  "streaming": true,              // Supports real-time streaming
  "pushNotifications": true,      // Can send async notifications
  "stateTransitionHistory": true, // Tracks task state changes
  "extensions": [                 // Custom capabilities
    "voice-system",
    "parallel-orchestration"
  ]
}
```

### skills
**Required (can be empty array)**
Array of skills this agent provides.

```json
"skills": [
  {
    "id": "skill-id",
    "description": "What this skill does",
    "tags": ["tag1", "tag2"],
    "examples": [
      "Example use case 1",
      "Example use case 2"
    ],
    "inputModes": {
      "text/plain": true,
      "application/json": true
    },
    "outputModes": {
      "text/markdown": true,
      "application/json": true
    },
    "securitySchemes": []  // Optional per-skill security
  }
]
```

### transport
**Required**
How to communicate with this agent.

```json
"transport": {
  "preferred": "internal",
  "endpoints": {
    "internal": "file:///root/flourisha/00_AI_Brain/agents/agent-id",
    "jsonrpc": "https://api.example.com/agent-id/rpc"  // Optional
  }
}
```

**Transport Types:**
- `internal` - File-based invocation within PAI
- `jsonrpc` - JSON-RPC 2.0 endpoint
- `grpc` - gRPC endpoint
- `rest` - REST API endpoint

### securitySchemes
**Optional**
Security and authorization requirements.

```json
"securitySchemes": {
  "authorization-required": {
    "type": "custom",
    "description": "Requires explicit authorization for security testing"
  }
}
```

### metadata
**Optional**
Additional agent-specific metadata.

```json
"metadata": {
  "model": "sonnet",
  "color": "yellow",
  "voiceId": "iLVmqjzCGGvqtMCk6vVQ",
  "voiceEnabled": true,
  "vendor": "multi"
}
```

---

## Skill Specification

### Skill Fields

#### id
**Required**
Unique skill identifier within this agent.

#### description
**Required**
Clear description of what this skill does.

#### tags
**Required**
Array of tags for discovery and categorization.

```json
"tags": ["research", "parallel", "gemini", "synthesis"]
```

#### examples
**Required**
Real-world usage examples.

```json
"examples": [
  "Research best mattress for heavy users over $5000",
  "Latest quantum computing practical applications"
]
```

#### inputModes
**Required**
Supported input content types.

```json
"inputModes": {
  "text/plain": true,
  "application/json": true,
  "text/markdown": false
}
```

#### outputModes
**Required**
Supported output content types.

```json
"outputModes": {
  "text/markdown": true,
  "application/json": true,
  "text/plain": true
}
```

#### securitySchemes
**Optional**
Per-skill security requirements (references agent.securitySchemes).

```json
"securitySchemes": ["authorization-required"]
```

---

## Creating Agent Cards

### For New Agents

1. Create agent directory:
   ```bash
   mkdir -p /root/flourisha/00_AI_Brain/agents/my-agent
   ```

2. Create AGENT.md with implementation

3. Create agent-card.json:
   ```bash
   cd /root/flourisha/00_AI_Brain/agents/my-agent
   nano agent-card.json
   ```

4. Validate:
   ```bash
   /root/flourisha/00_AI_Brain/scripts/a2a/validate-cards.sh
   ```

5. Update registry:
   ```bash
   /root/flourisha/00_AI_Brain/scripts/a2a/sync-registry.sh --agents
   ```

### For Existing Agents

Agent cards have already been generated for all existing agents. To modify:

1. Edit the agent-card.json file
2. Validate changes
3. Sync registry if needed

---

## Examples

### Research Agent

See: `/root/flourisha/00_AI_Brain/agents/gemini-researcher/agent-card.json`

Key features:
- Multiple skills declared
- Streaming and push notifications enabled
- Voice system integration
- Parallel orchestration capability

### Development Agent

See: `/root/flourisha/00_AI_Brain/agents/engineer/agent-card.json`

Key features:
- Code implementation skills
- Testing and debugging capabilities
- Permissions declared in metadata
- Multiple I/O modes

### Security Agent

See: `/root/flourisha/00_AI_Brain/agents/pentester/agent-card.json`

Key features:
- Authorization-required security scheme
- Per-skill security declarations
- Clear usage context requirements

---

## Validation

Run validation after creating or modifying agent cards:

```bash
/root/flourisha/00_AI_Brain/scripts/a2a/validate-cards.sh
```

The script checks:
- ✓ Valid JSON syntax
- ✓ Required fields present
- ⚠ Recommended fields (warnings)

---

## Best Practices

### ✅ DO

- Use semantic versioning for agent.version
- Provide clear, actionable examples
- Tag skills comprehensively for discovery
- Declare all I/O modes accurately
- Keep descriptions concise but complete
- Update version when capabilities change

### ❌ DON'T

- Don't use generic descriptions
- Don't leave skills array empty (unless truly no skills)
- Don't forget to validate after changes
- Don't duplicate skill IDs within an agent
- Don't omit required fields

---

## Troubleshooting

### Invalid JSON
```bash
# Check JSON syntax
jq . agent-card.json
```

### Missing Fields
```bash
# Validate required fields
/root/flourisha/00_AI_Brain/scripts/a2a/validate-cards.sh
```

### Registry Out of Sync
```bash
# Regenerate registry
/root/flourisha/00_AI_Brain/scripts/a2a/sync-registry.sh --agents
```

---

## Resources

- **A2A Spec**: https://a2a-protocol.org/latest/specification/
- **Example Cards**: `/root/flourisha/00_AI_Brain/agents/*/agent-card.json`
- **Validation Script**: `/root/flourisha/00_AI_Brain/scripts/a2a/validate-cards.sh`
- **Registry**: `/root/flourisha/00_AI_Brain/a2a/registry/agents.json`

---

**Last Updated:** 2025-11-19
