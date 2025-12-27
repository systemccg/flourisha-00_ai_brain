"""
A2A (Agent-to-Agent) Protocol Models

Pydantic models for A2A protocol API responses.
Following Google's Agent-to-Agent protocol format with Flourisha extensions.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class AgentCard(BaseModel):
    """A2A-compatible agent card."""
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    description: str = Field(..., description="Agent description")
    cardUrl: Optional[str] = Field(None, description="URL to full agent card JSON")
    agentPath: Optional[str] = Field(None, description="Path to agent definition file")
    tags: List[str] = Field(default_factory=list, description="Agent tags for discovery")
    vendor: str = Field(default="multi", description="AI vendor (multi, claude, gemini)")
    category: str = Field(..., description="Agent category")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    authorizationRequired: bool = Field(default=False, description="Requires explicit authorization")
    voiceId: Optional[str] = Field(None, description="ElevenLabs voice ID for notifications")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "engineer",
                "name": "Software Engineer",
                "description": "Professional software engineering expertise",
                "category": "development",
                "tags": ["engineering", "implementation", "testing"],
                "capabilities": ["code-implementation", "debugging", "testing"],
                "authorizationRequired": False
            }
        }
    }


class SkillCard(BaseModel):
    """A2A-compatible skill card."""
    id: str = Field(..., description="Unique skill identifier")
    name: str = Field(..., description="Human-readable skill name")
    description: str = Field(..., description="Skill description")
    type: str = Field(..., description="Skill type (skill, context, meta-skill, template)")
    skillPath: Optional[str] = Field(None, description="Path to skill definition file")
    tags: List[str] = Field(default_factory=list, description="Skill tags for discovery")
    slashCommand: Optional[str] = Field(None, description="Slash command trigger (e.g., /research)")
    autoload: bool = Field(default=False, description="Auto-loaded at session start")
    mcpServers: List[str] = Field(default_factory=list, description="Required MCP servers")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "research",
                "name": "Research Orchestration",
                "description": "Multi-source research with parallel agents",
                "type": "skill",
                "tags": ["research", "orchestration", "multi-agent"],
                "slashCommand": "/research",
                "autoload": False
            }
        }
    }


class SlashCommand(BaseModel):
    """Slash command mapping."""
    command: str = Field(..., description="The slash command (e.g., /research)")
    skillId: str = Field(..., description="Associated skill ID")
    skillName: str = Field(..., description="Human-readable skill name")
    description: str = Field(..., description="What the command does")

    model_config = {
        "json_schema_extra": {
            "example": {
                "command": "/research",
                "skillId": "research",
                "skillName": "Research Orchestration",
                "description": "Multi-source research with parallel agents"
            }
        }
    }


class SystemCapability(BaseModel):
    """A system capability."""
    id: str = Field(..., description="Capability identifier")
    enabled: bool = Field(..., description="Whether capability is enabled")
    description: str = Field(..., description="Capability description")
    supportedAgents: List[str] = Field(default_factory=list, description="Agents supporting this capability")
    config: Optional[Dict[str, Any]] = Field(None, description="Capability-specific configuration")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "voiceSystem",
                "enabled": True,
                "description": "Voice notification system for agent completions",
                "supportedAgents": ["engineer", "researcher", "architect"],
                "config": {"endpoint": "http://localhost:8888/notify"}
            }
        }
    }


class A2ARegistry(BaseModel):
    """Complete A2A registry response."""
    protocolVersion: str = Field(..., description="A2A protocol version")
    registryVersion: str = Field(..., description="Registry version")
    updated: str = Field(..., description="Last update timestamp")
    description: str = Field(..., description="Registry description")


class AgentsResponse(BaseModel):
    """Response for agents endpoint."""
    total: int = Field(..., description="Total number of agents")
    agents: List[AgentCard] = Field(..., description="List of agent cards")
    categories: Dict[str, List[str]] = Field(default_factory=dict, description="Agents by category")


class SkillsResponse(BaseModel):
    """Response for skills endpoint."""
    total: int = Field(..., description="Total number of skills")
    skills: List[SkillCard] = Field(..., description="List of skill cards")
    categories: Dict[str, List[str]] = Field(default_factory=dict, description="Skills by category")
    slashCommands: List[SlashCommand] = Field(default_factory=list, description="Available slash commands")


class CapabilitiesResponse(BaseModel):
    """Response for capabilities endpoint."""
    systemCapabilities: List[SystemCapability] = Field(..., description="System capabilities")
    transportProtocols: Dict[str, Any] = Field(default_factory=dict, description="Supported transports")
    extensions: Dict[str, str] = Field(default_factory=dict, description="Available extensions")


class A2AFullResponse(BaseModel):
    """Full A2A registry with all components."""
    registry: A2ARegistry = Field(..., description="Registry metadata")
    agents: AgentsResponse = Field(..., description="All agents")
    skills: SkillsResponse = Field(..., description="All skills")
    capabilities: CapabilitiesResponse = Field(..., description="System capabilities")
