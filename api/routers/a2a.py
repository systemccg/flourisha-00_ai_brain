"""
A2A (Agent-to-Agent) Registry API Router

REST API for Agent-to-Agent protocol registry.
Provides A2A-compatible agent cards, skill cards with slash command mappings,
and aggregated system capabilities.

Acceptance Criteria:
- Agents returns A2A-compatible agent cards
- Skills includes slash command mappings
- Capabilities aggregates all agent capabilities
"""
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, List

from fastapi import APIRouter, Depends, Request, Query

from models.response import APIResponse, ResponseMeta
from models.a2a import (
    AgentCard,
    SkillCard,
    SlashCommand,
    SystemCapability,
    A2ARegistry,
    AgentsResponse,
    SkillsResponse,
    CapabilitiesResponse,
    A2AFullResponse,
)
from middleware.auth import get_current_user, get_optional_user, UserContext

router = APIRouter(prefix="/api/a2a", tags=["A2A Protocol"])

# Pacific timezone for timestamps
PACIFIC = ZoneInfo("America/Los_Angeles")

# Registry paths
A2A_DIR = Path("/root/flourisha/00_AI_Brain/a2a/registry")
SKILLS_REGISTRY = A2A_DIR / "skills.json"
AGENTS_REGISTRY = A2A_DIR / "agents.json"
CAPABILITIES_REGISTRY = A2A_DIR / "capabilities.json"

# Agent voice mappings (from CORE skill)
AGENT_VOICE_IDS = {
    "kai": "gNbIwdcnM3B17qzBs2JY",
    "perplexity-researcher": "gNbIwdcnM3B17qzBs2JY",
    "claude-researcher": "gNbIwdcnM3B17qzBs2JY",
    "gemini-researcher": "gNbIwdcnM3B17qzBs2JY",
    "pentester": "gNbIwdcnM3B17qzBs2JY",
    "engineer": "gNbIwdcnM3B17qzBs2JY",
    "principal-engineer": "gNbIwdcnM3B17qzBs2JY",
    "designer": "gNbIwdcnM3B17qzBs2JY",
    "architect": "gNbIwdcnM3B17qzBs2JY",
    "artist": "gNbIwdcnM3B17qzBs2JY",
    "writer": "gNbIwdcnM3B17qzBs2JY",
}


def load_registry(path: Path) -> dict:
    """Load a registry JSON file."""
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def build_agent_cards(agents_data: dict) -> List[AgentCard]:
    """Build AgentCard objects from registry data."""
    cards = []
    for agent in agents_data.get('agents', []):
        cards.append(AgentCard(
            id=agent.get('id', ''),
            name=agent.get('name', ''),
            description=agent.get('description', ''),
            cardUrl=agent.get('cardUrl'),
            agentPath=agent.get('agentPath'),
            tags=agent.get('tags', []),
            vendor=agent.get('vendor', 'multi'),
            category=agent.get('category', 'general'),
            capabilities=agent.get('capabilities', []),
            authorizationRequired=agent.get('authorizationRequired', False),
            voiceId=AGENT_VOICE_IDS.get(agent.get('id')),
        ))
    return cards


def build_skill_cards(skills_data: dict) -> tuple[List[SkillCard], List[SlashCommand]]:
    """Build SkillCard objects and extract slash commands."""
    cards = []
    slash_commands = []

    for skill in skills_data.get('skills', []):
        card = SkillCard(
            id=skill.get('id', ''),
            name=skill.get('name', ''),
            description=skill.get('description', ''),
            type=skill.get('type', 'skill'),
            skillPath=skill.get('skillPath'),
            tags=skill.get('tags', []),
            slashCommand=skill.get('slashCommand'),
            autoload=skill.get('autoload', False),
            mcpServers=skill.get('mcpServers', []),
        )
        cards.append(card)

        # Extract slash command if present
        if skill.get('slashCommand'):
            slash_commands.append(SlashCommand(
                command=skill['slashCommand'],
                skillId=skill.get('id', ''),
                skillName=skill.get('name', ''),
                description=skill.get('description', ''),
            ))

    return cards, slash_commands


def build_system_capabilities(caps_data: dict) -> List[SystemCapability]:
    """Build SystemCapability objects from registry data."""
    capabilities = []
    sys_caps = caps_data.get('systemCapabilities', {})

    for cap_id, cap_data in sys_caps.items():
        if isinstance(cap_data, dict):
            capabilities.append(SystemCapability(
                id=cap_id,
                enabled=cap_data.get('enabled', False),
                description=cap_data.get('description', ''),
                supportedAgents=cap_data.get('supportedAgents', []),
                config={k: v for k, v in cap_data.items()
                       if k not in ['enabled', 'description', 'supportedAgents']},
            ))

    return capabilities


@router.get("/", response_model=APIResponse[A2AFullResponse])
async def get_full_registry(
    request: Request,
    user: UserContext = Depends(get_optional_user),
) -> APIResponse[A2AFullResponse]:
    """
    Get complete A2A registry.

    Returns all agents, skills with slash commands, and system capabilities
    in a single response. This is the full registry dump.

    **Authentication:** Optional (public endpoint for discovery)

    **Returns:**
    - registry: Protocol and registry metadata
    - agents: All registered agents with cards
    - skills: All skills with slash command mappings
    - capabilities: System-wide capabilities
    """
    meta_dict = request.state.get_meta()

    try:
        # Load all registries
        agents_data = load_registry(AGENTS_REGISTRY)
        skills_data = load_registry(SKILLS_REGISTRY)
        caps_data = load_registry(CAPABILITIES_REGISTRY)

        # Build agents response
        agent_cards = build_agent_cards(agents_data)
        agents_by_cat = {}
        for cat_name, cat_data in agents_data.get('categories', {}).items():
            agents_by_cat[cat_name] = cat_data.get('agents', [])

        agents_response = AgentsResponse(
            total=len(agent_cards),
            agents=agent_cards,
            categories=agents_by_cat,
        )

        # Build skills response
        skill_cards, slash_commands = build_skill_cards(skills_data)
        skills_by_cat = {}
        for cat_name, cat_data in skills_data.get('categories', {}).items():
            skills_by_cat[cat_name] = cat_data.get('skills', [])

        skills_response = SkillsResponse(
            total=len(skill_cards),
            skills=skill_cards,
            categories=skills_by_cat,
            slashCommands=slash_commands,
        )

        # Build capabilities response
        sys_capabilities = build_system_capabilities(caps_data)
        capabilities_response = CapabilitiesResponse(
            systemCapabilities=sys_capabilities,
            transportProtocols=caps_data.get('transportProtocols', {}),
            extensions=caps_data.get('extensions', {}),
        )

        # Build registry metadata
        registry = A2ARegistry(
            protocolVersion=agents_data.get('protocolVersion', '0.1.0'),
            registryVersion=agents_data.get('registryVersion', '1.0.0'),
            updated=agents_data.get('updated', datetime.now(PACIFIC).isoformat()),
            description="Flourisha AI Brain A2A Protocol Registry",
        )

        full_response = A2AFullResponse(
            registry=registry,
            agents=agents_response,
            skills=skills_response,
            capabilities=capabilities_response,
        )

        return APIResponse(
            success=True,
            data=full_response,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/agents", response_model=APIResponse[AgentsResponse])
async def get_agents(
    request: Request,
    category: Optional[str] = Query(None, description="Filter by category"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    user: UserContext = Depends(get_optional_user),
) -> APIResponse[AgentsResponse]:
    """
    Get all A2A-compatible agent cards.

    Returns agents registered in the A2A protocol with their cards,
    capabilities, and metadata.

    **Authentication:** Optional (public endpoint for discovery)

    **Query Parameters:**
    - category: Filter by agent category (research, development, security)
    - tag: Filter by agent tag

    **Returns:**
    - agents: List of A2A-compatible agent cards
    - categories: Agents organized by category
    - total: Total agent count
    """
    meta_dict = request.state.get_meta()

    try:
        agents_data = load_registry(AGENTS_REGISTRY)
        agent_cards = build_agent_cards(agents_data)

        # Apply filters
        if category:
            agent_cards = [a for a in agent_cards if a.category == category]
        if tag:
            agent_cards = [a for a in agent_cards if tag in a.tags]

        # Build categories
        agents_by_cat = {}
        for cat_name, cat_data in agents_data.get('categories', {}).items():
            agents_by_cat[cat_name] = cat_data.get('agents', [])

        response = AgentsResponse(
            total=len(agent_cards),
            agents=agent_cards,
            categories=agents_by_cat,
        )

        return APIResponse(
            success=True,
            data=response,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/agents/{agent_id}", response_model=APIResponse[AgentCard])
async def get_agent(
    agent_id: str,
    request: Request,
    user: UserContext = Depends(get_optional_user),
) -> APIResponse[AgentCard]:
    """
    Get a specific agent card by ID.

    **Authentication:** Optional

    **Path Parameters:**
    - agent_id: The agent identifier (e.g., 'engineer', 'researcher')
    """
    meta_dict = request.state.get_meta()

    try:
        agents_data = load_registry(AGENTS_REGISTRY)
        agent_cards = build_agent_cards(agents_data)

        for agent in agent_cards:
            if agent.id == agent_id:
                return APIResponse(
                    success=True,
                    data=agent,
                    meta=ResponseMeta(**meta_dict),
                )

        return APIResponse(
            success=False,
            error=f"Agent not found: {agent_id}",
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/skills", response_model=APIResponse[SkillsResponse])
async def get_skills(
    request: Request,
    category: Optional[str] = Query(None, description="Filter by category"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    type: Optional[str] = Query(None, description="Filter by skill type"),
    user: UserContext = Depends(get_optional_user),
) -> APIResponse[SkillsResponse]:
    """
    Get all skills with slash command mappings.

    Returns skills registered in the A2A protocol along with their
    slash command triggers for invocation.

    **Authentication:** Optional (public endpoint for discovery)

    **Query Parameters:**
    - category: Filter by skill category
    - tag: Filter by skill tag
    - type: Filter by skill type (skill, context, meta-skill, template)

    **Returns:**
    - skills: List of skill cards
    - slashCommands: Available slash command mappings
    - categories: Skills organized by category
    """
    meta_dict = request.state.get_meta()

    try:
        skills_data = load_registry(SKILLS_REGISTRY)
        skill_cards, slash_commands = build_skill_cards(skills_data)

        # Apply filters
        if category:
            # Find skills in the category
            cat_skills = skills_data.get('categories', {}).get(category, {}).get('skills', [])
            skill_cards = [s for s in skill_cards if s.id in cat_skills]
        if tag:
            skill_cards = [s for s in skill_cards if tag in s.tags]
        if type:
            skill_cards = [s for s in skill_cards if s.type == type]

        # Filter slash commands to match filtered skills
        skill_ids = {s.id for s in skill_cards}
        slash_commands = [c for c in slash_commands if c.skillId in skill_ids]

        # Build categories
        skills_by_cat = {}
        for cat_name, cat_data in skills_data.get('categories', {}).items():
            skills_by_cat[cat_name] = cat_data.get('skills', [])

        response = SkillsResponse(
            total=len(skill_cards),
            skills=skill_cards,
            categories=skills_by_cat,
            slashCommands=slash_commands,
        )

        return APIResponse(
            success=True,
            data=response,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/skills/{skill_id}", response_model=APIResponse[SkillCard])
async def get_skill(
    skill_id: str,
    request: Request,
    user: UserContext = Depends(get_optional_user),
) -> APIResponse[SkillCard]:
    """
    Get a specific skill card by ID.

    **Authentication:** Optional

    **Path Parameters:**
    - skill_id: The skill identifier (e.g., 'research', 'create-skill')
    """
    meta_dict = request.state.get_meta()

    try:
        skills_data = load_registry(SKILLS_REGISTRY)
        skill_cards, _ = build_skill_cards(skills_data)

        for skill in skill_cards:
            if skill.id == skill_id:
                return APIResponse(
                    success=True,
                    data=skill,
                    meta=ResponseMeta(**meta_dict),
                )

        return APIResponse(
            success=False,
            error=f"Skill not found: {skill_id}",
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/commands", response_model=APIResponse[List[SlashCommand]])
async def get_slash_commands(
    request: Request,
    user: UserContext = Depends(get_optional_user),
) -> APIResponse[List[SlashCommand]]:
    """
    Get all available slash commands.

    Returns a flat list of slash command to skill mappings
    for easy command lookup.

    **Authentication:** Optional
    """
    meta_dict = request.state.get_meta()

    try:
        skills_data = load_registry(SKILLS_REGISTRY)
        _, slash_commands = build_skill_cards(skills_data)

        return APIResponse(
            success=True,
            data=slash_commands,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/capabilities", response_model=APIResponse[CapabilitiesResponse])
async def get_capabilities(
    request: Request,
    user: UserContext = Depends(get_optional_user),
) -> APIResponse[CapabilitiesResponse]:
    """
    Get aggregated system capabilities.

    Returns all system-wide capabilities including voice system,
    parallel orchestration, integrations, and supported extensions.

    **Authentication:** Optional (public endpoint for discovery)

    **Returns:**
    - systemCapabilities: List of system capabilities with status
    - transportProtocols: Supported communication protocols
    - extensions: Available system extensions
    """
    meta_dict = request.state.get_meta()

    try:
        caps_data = load_registry(CAPABILITIES_REGISTRY)
        sys_capabilities = build_system_capabilities(caps_data)

        response = CapabilitiesResponse(
            systemCapabilities=sys_capabilities,
            transportProtocols=caps_data.get('transportProtocols', {}),
            extensions=caps_data.get('extensions', {}),
        )

        return APIResponse(
            success=True,
            data=response,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/capabilities/{capability_id}", response_model=APIResponse[SystemCapability])
async def get_capability(
    capability_id: str,
    request: Request,
    user: UserContext = Depends(get_optional_user),
) -> APIResponse[SystemCapability]:
    """
    Get a specific system capability by ID.

    **Authentication:** Optional

    **Path Parameters:**
    - capability_id: The capability identifier (e.g., 'voiceSystem', 'parallelOrchestration')
    """
    meta_dict = request.state.get_meta()

    try:
        caps_data = load_registry(CAPABILITIES_REGISTRY)
        sys_capabilities = build_system_capabilities(caps_data)

        for cap in sys_capabilities:
            if cap.id == capability_id:
                return APIResponse(
                    success=True,
                    data=cap,
                    meta=ResponseMeta(**meta_dict),
                )

        return APIResponse(
            success=False,
            error=f"Capability not found: {capability_id}",
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )


@router.get("/discovery", response_model=APIResponse[dict])
async def discovery(
    request: Request,
) -> APIResponse[dict]:
    """
    A2A discovery endpoint.

    Standard A2A protocol discovery endpoint for service discovery.
    Returns minimal registry info for initial handshake.

    **Authentication:** None (public discovery endpoint)
    """
    meta_dict = request.state.get_meta()

    try:
        agents_data = load_registry(AGENTS_REGISTRY)
        skills_data = load_registry(SKILLS_REGISTRY)
        caps_data = load_registry(CAPABILITIES_REGISTRY)

        discovery_info = {
            "name": "Flourisha AI Brain",
            "description": "Personal AI Infrastructure with A2A protocol support",
            "protocolVersion": agents_data.get('protocolVersion', '0.1.0'),
            "registryVersion": agents_data.get('registryVersion', '1.0.0'),
            "endpoints": {
                "agents": "/api/a2a/agents",
                "skills": "/api/a2a/skills",
                "commands": "/api/a2a/commands",
                "capabilities": "/api/a2a/capabilities",
                "full": "/api/a2a/",
            },
            "counts": {
                "agents": len(agents_data.get('agents', [])),
                "skills": len(skills_data.get('skills', [])),
                "capabilities": len(caps_data.get('systemCapabilities', {})),
            },
            "transportProtocols": list(caps_data.get('transportProtocols', {}).keys()),
        }

        return APIResponse(
            success=True,
            data=discovery_info,
            meta=ResponseMeta(**meta_dict),
        )

    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            meta=ResponseMeta(**meta_dict),
        )
