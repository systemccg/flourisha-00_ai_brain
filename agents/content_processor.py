"""
Pydantic AI Content Processor Agent
Context-aware AI processing using Claude
"""
import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel


class ProcessedContentOutput(BaseModel):
    """Structured output from content processing agent"""
    summary: str = Field(..., description="2-3 paragraph summary of the content")
    key_insights: List[str] = Field(..., description="3-5 key insights or learnings")
    action_items: List[str] = Field(..., description="Actionable items extracted from content")
    tags: List[str] = Field(..., description="5-10 relevant tags for categorization")
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relevance score to the project (0.0 to 1.0)"
    )


class ContentProcessorAgent:
    """
    AI agent for processing content with project-specific context
    Uses Pydantic AI with Claude for structured outputs
    """

    def __init__(self):
        """Initialize the content processor agent"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        # Initialize Anthropic model (pydantic-ai v1.x uses string model name)
        self.model = 'anthropic:claude-sonnet-4-5-20250929'

        # Create agent with structured output
        self.agent = Agent(
            model=self.model,
            output_type=ProcessedContentOutput,
            system_prompt=self._get_base_system_prompt()
        )

    def _get_base_system_prompt(self) -> str:
        """Get the base system prompt for the agent"""
        return """You are an AI content processor for a multi-tenant content intelligence platform.

Your role is to analyze video transcripts, meeting notes, documents, and voice recordings to extract:
1. Clear, actionable summaries (2-3 paragraphs)
2. Key insights and learnings
3. Action items and next steps
4. Relevant tags for categorization
5. Relevance score to the specified project context

IMPORTANT GUIDELINES:
- Be concise but comprehensive
- Focus on actionable insights
- Translate technical concepts to the project's specific tech stack when provided
- Prioritize practical takeaways over theory
- Score relevance honestly (0.0 = not relevant, 1.0 = highly relevant)
"""

    def _build_project_context(
        self,
        project_name: Optional[str] = None,
        tech_stack: Optional[Dict[str, str]] = None,
        context_replacements: Optional[Dict[str, str]] = None
    ) -> str:
        """Build project-specific context for the prompt"""
        context_parts = []

        if project_name:
            context_parts.append(f"PROJECT: {project_name}")

        if tech_stack:
            context_parts.append("\nPROJECT TECH STACK:")
            for category, tech in tech_stack.items():
                context_parts.append(f"- {category}: {tech}")

        if context_replacements:
            context_parts.append("\nTECH TRANSLATION RULES:")
            context_parts.append("When you encounter these terms, translate them to our stack:")
            for original, replacement in context_replacements.items():
                context_parts.append(f"- '{original}' → '{replacement}'")

        return "\n".join(context_parts) if context_parts else ""

    async def process_content(
        self,
        title: str,
        transcript: str,
        content_type: str = "video",
        project_name: Optional[str] = None,
        tech_stack: Optional[Dict[str, str]] = None,
        context_replacements: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProcessedContentOutput:
        """
        Process content with AI analysis

        Args:
            title: Content title
            transcript: Full transcript/content text
            content_type: Type of content (video, meeting, note, etc.)
            project_name: Name of the project for context
            tech_stack: Project's tech stack preferences
            context_replacements: Terms to translate (e.g., "Qdrant" -> "Supabase")
            metadata: Additional metadata (author, date, duration, etc.)

        Returns:
            ProcessedContentOutput with summary, insights, actions, tags, and relevance
        """
        # Build project-specific context
        project_context = self._build_project_context(
            project_name, tech_stack, context_replacements
        )

        # Build full prompt
        user_prompt = f"""Analyze this {content_type}:

TITLE: {title}
"""

        if project_context:
            user_prompt += f"\n{project_context}\n"

        if metadata:
            user_prompt += "\nMETADATA:\n"
            for key, value in metadata.items():
                user_prompt += f"- {key}: {value}\n"

        user_prompt += f"""
TRANSCRIPT/CONTENT:
{transcript}

Please provide a comprehensive analysis with:
1. A clear 2-3 paragraph summary
2. Key insights (3-5 main takeaways)
3. Action items (specific, actionable next steps)
4. Relevant tags (5-10 tags for categorization)
5. Relevance score (how relevant is this to the project context)

Remember to translate any tech stack terms to our specific stack when applicable.
"""

        # Run agent
        result = await self.agent.run(user_prompt)

        # pydantic-ai v1.x returns result.output instead of result.data
        return result.output


# Convenience function for quick usage
async def process_video_transcript(
    title: str,
    transcript: str,
    project_config: Optional[Dict[str, Any]] = None
) -> ProcessedContentOutput:
    """
    Quick function to process a video transcript

    Args:
        title: Video title
        transcript: Video transcript
        project_config: Optional dict with project_name, tech_stack, context_replacements

    Returns:
        ProcessedContentOutput
    """
    processor = ContentProcessorAgent()

    project_name = None
    tech_stack = None
    context_replacements = None

    if project_config:
        project_name = project_config.get('name')
        tech_stack = project_config.get('tech_stack')
        context_replacements = project_config.get('context_replacements')

    return await processor.process_content(
        title=title,
        transcript=transcript,
        content_type="video",
        project_name=project_name,
        tech_stack=tech_stack,
        context_replacements=context_replacements
    )
