# AG-UI + A2UI Integration Plan

**Agent-Driven User Interfaces for Flourisha**

*Created: 2025-01-02 | Status: Planning*

---

## Executive Summary

This document outlines the integration of two complementary protocols for agent-driven UIs:

- **AG-UI** (CopilotKit): Streaming transport layer for agent-frontend communication
- **A2UI** (Google): Declarative UI rendering from agent responses

Together, these enable Flourisha to have real-time, streaming conversations with agents that can dynamically generate interactive UI components.

---

## Protocol Overview

### AG-UI (Agent-User Interaction Protocol)

**Creator:** CopilotKit
**Version:** 0.0.41 (178K weekly npm downloads)
**Documentation:** [docs.ag-ui.com](https://docs.ag-ui.com/)
**GitHub:** [github.com/ag-ui-protocol/ag-ui](https://github.com/ag-ui-protocol/ag-ui)

**What it does:**
- Bi-directional streaming between agent backends and frontends
- Event-based protocol over SSE or WebSockets
- Handles messages, tool calls, state synchronization

**Event Types:**
| Event | Purpose |
|-------|---------|
| `TEXT_MESSAGE_CONTENT` | Streaming text from agent |
| `TOOL_CALL_START` | Agent invoking a tool |
| `TOOL_CALL_END` | Tool execution complete |
| `STATE_DELTA` | Shared state update |
| `RUN_STARTED` | Agent run begins |
| `RUN_FINISHED` | Agent run completes |

**TypeScript SDK:**
```bash
bun add @ag-ui/core @ag-ui/client
```

### A2UI (Agent-to-User Interface)

**Creator:** Google
**Version:** 0.8 (Public Preview)
**Documentation:** [a2ui.org](https://a2ui.org/)
**GitHub:** [github.com/google/A2UI](https://github.com/google/A2UI)

**What it does:**
- Declarative JSON format for describing UI components
- Security-first: no code execution, just data
- Component catalog concept (pre-approved widgets only)
- Framework-agnostic rendering

**How it works:**
```
1. Agent generates JSON payload describing UI structure
2. JSON transported via AG-UI (or other transport)
3. Client's A2UI Renderer parses the JSON
4. Renderer maps abstract components to concrete implementations
```

**Example A2UI Message:**
```json
{
  "type": "a2ui",
  "components": [
    {
      "id": "card-1",
      "type": "Card",
      "props": {
        "title": "Energy Status",
        "variant": "elevated"
      },
      "children": ["stat-1", "chart-1"]
    },
    {
      "id": "stat-1",
      "type": "Stat",
      "props": {
        "label": "Current Energy",
        "value": 7,
        "max": 10
      }
    }
  ]
}
```

---

## Architecture

### Current Flourisha Frontend Stack

| Layer | Technology |
|-------|------------|
| Framework | Next.js 15.1 |
| React | v19 |
| UI Library | Chakra UI v3 |
| Data Fetching | TanStack React Query |
| Auth | Firebase |
| API Client | Axios |

**Source:** `/root/flourisha/00_AI_Brain/frontend/`

### Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flourisha Frontend                        │
├─────────────────────────────────────────────────────────────┤
│  CopilotKitProvider                                          │
│  ├── AgentContext (useAgent hook)                            │
│  ├── A2UIRenderer                                            │
│  │   └── Component Catalog (Chakra mappings)                 │
│  └── React Query (existing data layer)                       │
├─────────────────────────────────────────────────────────────┤
│  Existing Components                                         │
│  ├── energy/       - EnergyWidget, EnergyChart               │
│  ├── knowledge/    - GraphVisualization, NodeDetail          │
│  ├── reports/      - MorningReport, Blockers                 │
│  ├── search/       - SearchBar, SearchResults                │
│  └── documents/    - Upload, Preview                         │
└─────────────────────────────────────────────────────────────┘
                           ↕ AG-UI (SSE)
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI + Claude)                 │
│  ├── /api/v1/agent/stream  ← AG-UI endpoint                  │
│  ├── AG-UI Encoder (Python)                                  │
│  ├── A2UI Message Generator                                  │
│  └── Claude/Anthropic API                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Catalog

The A2UI component catalog maps abstract component types to Flourisha's Chakra UI implementations.

### Proposed Catalog

```typescript
// src/lib/a2ui/catalog.ts

import {
  Card, Box, VStack, HStack, SimpleGrid,
  Stat, StatLabel, StatNumber, StatHelpText,
  Progress, Badge, Button, Input, Select,
  Heading, Text
} from '@chakra-ui/react'

// Flourisha-specific components
import { EnergyWidget } from '@/components/energy'
import { OKRProgressCard } from '@/components/reports'
import { GraphNode } from '@/components/knowledge'

export const flourishaA2UICatalog = {
  // Layout Components
  'Card': Card,
  'Box': Box,
  'VStack': VStack,
  'HStack': HStack,
  'Grid': SimpleGrid,

  // Data Display
  'Stat': StatComponent,
  'Progress': Progress,
  'Badge': Badge,
  'Heading': Heading,
  'Text': Text,

  // Interactive
  'Button': Button,
  'Input': Input,
  'Select': Select,

  // Flourisha Domain Components
  'EnergyWidget': EnergyWidget,
  'OKRProgress': OKRProgressCard,
  'KnowledgeNode': GraphNode,
  'TaskItem': TaskListItem,
  'Blocker': BlockerCard,
  'SearchResult': SearchResultCard,
}
```

### Component Mapping Rules

| A2UI Type | Chakra Component | Notes |
|-----------|------------------|-------|
| `Card` | `Card` | Supports variant, size |
| `Stat` | `Stat` + children | Custom wrapper |
| `Progress` | `Progress` | value, max, colorScheme |
| `Button` | `Button` | onClick mapped to action events |
| `Chart` | Recharts wrapper | For energy/OKR charts |

---

## Implementation Phases

### Phase 1: Foundation

**Goal:** Add CopilotKit provider and AG-UI client

**Files to create:**
```
src/
├── lib/
│   └── agent/
│       ├── provider.tsx      # CopilotKitProvider wrapper
│       ├── client.ts         # AG-UI client configuration
│       └── types.ts          # AG-UI event types
├── contexts/
│   └── agent-context.tsx     # Agent state management
└── hooks/
    └── use-agent.ts          # useAgent hook wrapper
```

**Dependencies:**
```bash
bun add @copilotkit/react-core @copilotkit/react-ui @ag-ui/core @ag-ui/client
```

**Tasks:**
- [ ] Install AG-UI and CopilotKit packages
- [ ] Create CopilotKitProvider wrapper in app layout
- [ ] Configure AG-UI client for SSE streaming
- [ ] Add AgentContext for global agent state

### Phase 2: A2UI Renderer

**Goal:** Build component catalog and A2UI renderer

**Files to create:**
```
src/
├── lib/
│   └── a2ui/
│       ├── catalog.ts        # Component catalog
│       ├── renderer.tsx      # A2UI Renderer component
│       ├── types.ts          # A2UI message types
│       └── validators.ts     # Component prop validation
└── components/
    └── agent/
        └── a2ui-container.tsx  # Container for A2UI output
```

**Tasks:**
- [ ] Define component catalog with Chakra mappings
- [ ] Build A2UIRenderer component
- [ ] Add prop validation for security
- [ ] Create container component for agent UI output

### Phase 3: Agent Chat Interface

**Goal:** Create conversational UI with streaming

**Files to create:**
```
src/
└── components/
    └── agent/
        ├── agent-chat.tsx       # Main chat component
        ├── message-list.tsx     # Message history
        ├── message-input.tsx    # User input
        ├── streaming-text.tsx   # Streaming text display
        └── tool-call-card.tsx   # Tool execution display
```

**Tasks:**
- [ ] Build AgentChat component with streaming support
- [ ] Add message history with React Query persistence
- [ ] Implement tool call visualization
- [ ] Add human-in-the-loop interrupt handling

### Phase 4: Backend Integration

**Goal:** Add AG-UI encoder to FastAPI backend

**Files to create:**
```
/root/flourisha/00_AI_Brain/api/
├── routers/
│   └── agent.py              # /api/v1/agent/stream endpoint
└── services/
    └── ag_ui/
        ├── encoder.py        # AG-UI event encoder
        ├── a2ui_generator.py # A2UI message generator
        └── types.py          # Python AG-UI types
```

**Dependencies:**
```bash
uv add ag-ui-core ag-ui-encoder
```

**Tasks:**
- [ ] Create /api/v1/agent/stream SSE endpoint
- [ ] Build AG-UI event encoder
- [ ] Integrate with Claude API for agent responses
- [ ] Add A2UI message generation for UI components

### Phase 5: Feature Integration

**Goal:** Connect AG-UI/A2UI to existing features

**Integration Points:**

| Feature | Integration |
|---------|-------------|
| Morning Report | A2UI: Interactive briefing with action buttons |
| Knowledge Graph | AG-UI: Streaming exploration narration |
| Document Upload | AG-UI: Real-time extraction feedback |
| Energy Tracking | A2UI: Dynamic energy widgets |
| Search | AG-UI: Conversational search refinement |

**Tasks:**
- [ ] Add agent-powered morning report generation
- [ ] Integrate knowledge graph with agent exploration
- [ ] Add streaming document processing feedback
- [ ] Create conversational search interface

---

## Security Considerations

### A2UI Security Model

1. **Component Catalog is Allow-list Only**
   - Agents can only request pre-approved components
   - Unknown component types are rejected

2. **Prop Validation**
   - All component props are validated before rendering
   - No arbitrary code execution

3. **Action Sandboxing**
   - Button/input actions emit events, not execute code
   - All actions routed through controlled handlers

### Implementation

```typescript
// src/lib/a2ui/validators.ts

export function validateComponent(component: A2UIComponent): boolean {
  // Check component type is in catalog
  if (!catalog[component.type]) {
    console.warn(`Unknown A2UI component: ${component.type}`)
    return false
  }

  // Validate props against schema
  const schema = componentSchemas[component.type]
  return validateProps(component.props, schema)
}
```

---

## API Endpoint Design

### /api/v1/agent/stream

**Method:** GET (SSE) or WebSocket
**Auth:** Bearer token (Firebase JWT)

**Request:**
```typescript
interface AgentStreamRequest {
  message: string
  context?: {
    current_page?: string
    selected_items?: string[]
    user_state?: Record<string, unknown>
  }
  conversation_id?: string
}
```

**Response (SSE Events):**
```
event: TEXT_MESSAGE_CONTENT
data: {"content": "Let me check your energy levels..."}

event: TOOL_CALL_START
data: {"tool": "get_energy_history", "args": {"days": 7}}

event: A2UI_RENDER
data: {"components": [{"type": "EnergyWidget", ...}]}

event: RUN_FINISHED
data: {"run_id": "abc123", "status": "complete"}
```

---

## Testing Strategy

### Unit Tests
- Component catalog validation
- A2UI renderer with mock components
- AG-UI event parsing

### Integration Tests
- End-to-end streaming flow
- Component rendering from agent responses
- Error handling and recovery

### E2E Tests
- Add to existing Playwright suite
- Test agent chat interactions
- Verify A2UI component rendering

---

## Migration Path

### Minimal Viable Integration

Start with a simple agent chat sidebar that doesn't affect existing functionality:

1. Add CopilotKitProvider to layout
2. Create floating chat button
3. Build basic AgentChat component
4. Connect to new /api/v1/agent/stream endpoint

This allows gradual rollout without disrupting current features.

### Progressive Enhancement

Once stable, progressively enhance existing features:

1. Add "Ask Agent" buttons to existing pages
2. Replace static morning reports with A2UI versions
3. Add conversational mode to search
4. Enable agent-powered document analysis

---

## References

- [AG-UI Documentation](https://docs.ag-ui.com/)
- [A2UI Official Site](https://a2ui.org/)
- [CopilotKit Documentation](https://docs.copilotkit.ai/)
- [Google A2UI GitHub](https://github.com/google/A2UI)
- [AG-UI Protocol GitHub](https://github.com/ag-ui-protocol/ag-ui)
- [CopilotKit Blog: A2UI + AG-UI](https://www.copilotkit.ai/blog/build-with-googles-new-a2ui-spec-agent-user-interfaces-with-a2ui-ag-ui)

---

## Changelog

| Date | Change |
|------|--------|
| 2025-01-02 | Initial document created |
