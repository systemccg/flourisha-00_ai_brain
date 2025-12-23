# Agent Factory & A2A Coordination

Temporal agent creation and Agent-to-Agent (A2A) protocol for multi-agent orchestration in Flourisha.

## Overview

The Agent Factory enables dynamic creation of purpose-built agents for specific, time-bound tasks. Combined with A2A protocol, it provides structured agent coordination and lifecycle management.

**Department:** System Evolution (Department 4)

---

## Agent Factory Pattern

### Naming Convention

Temporal agents use a standardized naming pattern:
```
agent_Purpose_YYYYMMDD
```

**Examples:**
- `agent_CompetitorAnalysis_20260115`
- `agent_NewsletterWriter_20260120`
- `agent_DatabaseOptimizer_20260125`
- `agent_UserResearchSynthesizer_20260120`

### Agent Metadata Schema

```python
{
  "agent_id": "agent_CompetitorAnalysis_20260115",
  "purpose": "Analyze top 5 competitors in AI automation space",
  "created_at": "2026-01-15T09:00:00Z",
  "deadline": "2026-01-16T17:00:00Z",
  "status": "active",  # active, completed, failed, archived
  "parent_department": "execution_agents",
  "required_capabilities": ["research", "analysis", "reporting"],
  "context_sources": ["knowledge_intelligence", "strategic_command"]
}
```

### Agent Lifecycle

```
┌──────────────┐
│   Creation   │  Agent factory instantiates with specific purpose
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Execution   │  Agent performs defined task with context
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Reporting   │  Results stored and communicated
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Feedback    │  Quality assessment captured
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Archival    │  Agent archived with learnings extracted
└──────────────┘
```

### Factory Implementation

```python
class AgentFactory:
    async def create_agent(
        self,
        purpose: str,
        deadline: datetime,
        capabilities: list
    ) -> str:
        """Create temporal agent with specific purpose."""
        agent_id = f"agent_{purpose.replace(' ', '')}_{datetime.now().strftime('%Y%m%d')}"
        # Register in Supabase agent_registry table
        # Initialize with context from relevant departments
        return agent_id

    async def execute_agent(self, agent_id: str) -> dict:
        """Execute agent task and capture results."""
        # Load agent context
        # Execute with appropriate model (haiku/sonnet/opus)
        # Store results
        return {"status": "completed", "output": result}

    async def capture_feedback(
        self,
        agent_id: str,
        outcome: str,
        quality: int
    ) -> None:
        """Store agent execution feedback for continuous improvement."""
        # Insert into agent_feedback table
        # Update agent performance metrics
        pass

    async def archive_agent(self, agent_id: str) -> None:
        """Archive completed agent and extract learnings."""
        # Mark as archived
        # Extract patterns for future agent optimization
        pass
```

---

## A2A Protocol Integration

### Agent-to-Agent Communication

Standardized protocol for agent coordination:

| Component | Purpose |
|-----------|---------|
| **Context Handoff** | Pass relevant context between agents |
| **Result Aggregation** | Combine outputs from multiple agents |
| **Failure Handling** | Retry logic and graceful degradation |
| **Message Format** | JSON-based structured communication |

### A2A Message Structure

```json
{
  "message_id": "msg_abc123",
  "from_agent": "claude-researcher",
  "to_agent": "writer",
  "timestamp": "2026-01-15T10:30:00Z",
  "type": "context_handoff",
  "payload": {
    "task_context": "Research completed on competitor analysis",
    "key_findings": [...],
    "suggested_next_steps": [...]
  }
}
```

### Multi-Agent Coordination Example

```python
# A2A coordination for content creation pipeline
async def create_content_pipeline(topic: str):
    # Step 1: Research
    research_result = await claude_researcher.execute(
        query=topic,
        mode="standard"
    )

    # Step 2: Content Draft (receives research context)
    content_draft = await writer.execute(
        context=research_result,
        task="Create comprehensive article"
    )

    # Step 3: Edit and Refine
    final_content = await editor.execute(
        draft=content_draft,
        style_guide="flourisha_voice"
    )

    return final_content
```

### Agent Card Integration

All agents have A2A-compliant agent cards in:
```
/root/flourisha/00_AI_Brain/agents/{agent-name}/agent-card.json
```

Agent card structure:
- Identity (id, name, version, description)
- Capabilities (streaming, push notifications, extensions)
- Skills declaration (with examples, tags, I/O modes)
- Transport endpoints
- Security schemes

---

## Execution Context

All execution agents receive enriched context from other departments:

| Context Type | Source | Purpose |
|--------------|--------|---------|
| **User Context** | Strategic Command | Preferences, communication style |
| **Knowledge Context** | Knowledge Intelligence | RAG-retrieved relevant knowledge |
| **Strategic Context** | Strategic Command | Current priorities, OKRs |
| **Personality Context** | Knowledge Intelligence | Contact profiles (for email/communication) |

### Context Assembly

```python
async def assemble_agent_context(agent_id: str, task: dict) -> dict:
    """Assemble full context for agent execution."""
    return {
        "user_preferences": await get_user_context(),
        "relevant_knowledge": await rag_query(task["topic"]),
        "current_okrs": await get_active_okrs(),
        "personality_profiles": await get_relevant_profiles(task),
        "task_details": task
    }
```

---

## Discovery & Registry

### Agent Registry

Located at `/root/flourisha/00_AI_Brain/a2a/registry/agents.json`:

```json
{
  "agents": [
    {
      "id": "gemini-researcher",
      "name": "Gemini Researcher",
      "category": "research",
      "tags": ["research", "web", "multi-perspective"],
      "card_url": "agents/gemini-researcher/agent-card.json"
    }
  ]
}
```

### Finding Agents by Capability

```bash
# Find all research agents
jq '.agents[] | select(.tags[] | contains("research"))' \
  /root/flourisha/00_AI_Brain/a2a/registry/agents.json

# List agent capabilities
jq -r '.agents[] | "\(.name): \(.tags | join(", "))"' \
  /root/flourisha/00_AI_Brain/a2a/registry/agents.json
```

---

## Monitoring & Feedback

### Agent Performance Tracking

| Metric | Description | Target |
|--------|-------------|--------|
| Execution success rate | % of agents completing successfully | 90%+ |
| Average completion time | Time from creation to completion | Context-dependent |
| Quality ratings | Post-execution user ratings | 4+/5 |
| A2A handoff success | % of successful context transfers | 95%+ |

### Feedback Loop

```
Monitor Operations → Capture Feedback → Analyze Patterns → Generate Insights → Implement Changes → (repeat)
```

Feedback stored in `agent_feedback` table:
- agent_id
- execution_timestamp
- outcome (success/partial/failed)
- quality_score (1-5)
- feedback_notes
- learnings_extracted

---

## Deployment Triggers

### Manual Trigger
```bash
# Via PAI skills system
/research "AI agent architecture patterns 2026"
```

### Automated Trigger
```python
# Via morning report identifying high-priority research need
await agent_factory.create_agent(
    purpose="ResearchCompetitorPricing",
    agent_type="research",
    mode="standard",
    deadline="2026-01-20"
)
```

### Promotion from Ideas
Improvement ideas can be promoted to agent tasks:
```bash
# Convert improvement idea to agent task
# Move from improvement-ideas/ to active agent execution
# Track in agent_registry
```

---

## Related Documentation

- [A2A_IMPLEMENTATION_COMPLETE.md](../A2A_IMPLEMENTATION_COMPLETE.md) - Full A2A implementation details
- [FLOURISHA_AI_ARCHITECTURE.md](../FLOURISHA_AI_ARCHITECTURE.md) - System overview
- [a2a/overview.md](../a2a/overview.md) - A2A protocol documentation
- [a2a/agent-cards.md](../a2a/agent-cards.md) - Agent card specification

---

*Part of Pillar 4: EXECUTE (Agentic Operations) in the Flourisha Five Pillars Architecture*
