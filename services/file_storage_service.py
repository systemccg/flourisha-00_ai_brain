"""
PARA File Storage Service
Organizes content files using the PARA methodology:
- Projects: Active projects with outcomes
- Areas: Ongoing areas of responsibility
- Resources: Reference materials
- Archives: Inactive items
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json


class PARAFileStorage:
    """
    Service for managing content files in PARA structure
    Stores markdown files synced with Google Drive
    """

    def __init__(self, base_path: str = "/root/flourisha"):
        """
        Initialize PARA storage

        Args:
            base_path: Base directory for Flourisha (synced with Google Drive)
        """
        self.base_path = Path(base_path)

        # PARA structure
        self.para_paths = {
            "projects": self.base_path / "01f_Flourisha_Projects",
            "areas": self.base_path / "02f_Flourisha_Areas",
            "resources": self.base_path / "03f_Flourisha_Resources",
            "archives": self.base_path / "04f_Flourisha_Archives"
        }

        # Content storage within PARA
        self.content_paths = {
            "projects": self.para_paths["projects"] / "Content_Intelligence",
            "areas": self.para_paths["areas"] / "Content_Intelligence",
            "resources": self.para_paths["resources"] / "Content_Intelligence",
            "archives": self.para_paths["archives"] / "Content_Intelligence"
        }

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Create PARA directory structure if it doesn't exist"""
        for category, path in self.content_paths.items():
            path.mkdir(parents=True, exist_ok=True)

            # Create subdirectories for content types
            (path / "YouTube").mkdir(exist_ok=True)
            (path / "Voice_Notes").mkdir(exist_ok=True)
            (path / "Meetings").mkdir(exist_ok=True)
            (path / "Documents").mkdir(exist_ok=True)
            (path / "Limitless").mkdir(exist_ok=True)

    def _get_content_path(
        self,
        para_category: str,
        content_type: str,
        project_name: Optional[str] = None
    ) -> Path:
        """
        Get the storage path for content

        Args:
            para_category: 'projects', 'areas', 'resources', or 'archives'
            content_type: Type of content (youtube_video, voice_note, etc.)
            project_name: Optional project name for projects category

        Returns:
            Path object for content storage
        """
        base = self.content_paths.get(para_category, self.content_paths["resources"])

        # Map content types to folders
        type_mapping = {
            "youtube_video": "YouTube",
            "voice_note": "Voice_Notes",
            "meeting_transcript": "Meetings",
            "document": "Documents",
            "limitless_note": "Limitless"
        }

        content_folder = type_mapping.get(content_type, "Documents")
        path = base / content_folder

        # Add project subfolder if in projects category
        if para_category == "projects" and project_name:
            project_slug = self._slugify(project_name)
            path = path / project_slug

        path.mkdir(parents=True, exist_ok=True)
        return path

    def _slugify(self, text: str) -> str:
        """Convert text to filesystem-safe slug"""
        # Simple slugification
        slug = text.lower()
        slug = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in slug)
        slug = slug.strip('_').replace('__', '_')
        return slug[:100]  # Limit length

    def _generate_filename(
        self,
        title: str,
        content_id: str,
        timestamp: datetime
    ) -> str:
        """
        Generate unique filename for content

        Args:
            title: Content title
            content_id: Unique content ID
            timestamp: Creation timestamp

        Returns:
            Filename with timestamp and slug
        """
        date_str = timestamp.strftime("%Y-%m-%d")
        title_slug = self._slugify(title)
        # Format: YYYY-MM-DD_title-slug_id.md
        return f"{date_str}_{title_slug}_{content_id[:8]}.md"

    def save_content(
        self,
        content_id: str,
        title: str,
        content_type: str,
        summary: str,
        key_insights: list,
        action_items: list,
        tags: list,
        source_url: Optional[str] = None,
        transcript: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        para_category: str = "resources",
        project_name: Optional[str] = None
    ) -> str:
        """
        Save content as markdown file in PARA structure

        Args:
            content_id: Unique content identifier
            title: Content title
            content_type: Type of content
            summary: AI-generated summary
            key_insights: List of insights
            action_items: List of actions
            tags: List of tags
            source_url: Optional source URL
            transcript: Optional full transcript
            metadata: Additional metadata
            para_category: PARA category (projects/areas/resources/archives)
            project_name: Project name if para_category is 'projects'

        Returns:
            Relative file path from base_path
        """
        # Get storage path
        storage_path = self._get_content_path(para_category, content_type, project_name)

        # Generate filename
        timestamp = datetime.utcnow()
        filename = self._generate_filename(title, content_id, timestamp)
        file_path = storage_path / filename

        # Build markdown content
        markdown = self._build_markdown(
            title=title,
            content_type=content_type,
            summary=summary,
            key_insights=key_insights,
            action_items=action_items,
            tags=tags,
            source_url=source_url,
            transcript=transcript,
            metadata=metadata,
            content_id=content_id,
            timestamp=timestamp
        )

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        # Return relative path
        return str(file_path.relative_to(self.base_path))

    def _build_markdown(
        self,
        title: str,
        content_type: str,
        summary: str,
        key_insights: list,
        action_items: list,
        tags: list,
        source_url: Optional[str],
        transcript: Optional[str],
        metadata: Optional[Dict[str, Any]],
        content_id: str,
        timestamp: datetime
    ) -> str:
        """Build markdown content with proper formatting"""

        lines = [
            f"# {title}",
            "",
            "---",
            "",
            "## Metadata",
            "",
            f"- **Content ID**: `{content_id}`",
            f"- **Type**: {content_type.replace('_', ' ').title()}",
            f"- **Created**: {timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC",
        ]

        if source_url:
            lines.append(f"- **Source**: [{source_url}]({source_url})")

        if metadata:
            for key, value in metadata.items():
                if value:
                    lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")

        if tags:
            lines.extend([
                "",
                "**Tags**: " + ", ".join(f"`{tag}`" for tag in tags)
            ])

        lines.extend([
            "",
            "---",
            "",
            "## Summary",
            "",
            summary,
            ""
        ])

        if key_insights:
            lines.extend([
                "## Key Insights",
                ""
            ])
            for insight in key_insights:
                lines.append(f"- {insight}")
            lines.append("")

        if action_items:
            lines.extend([
                "## Action Items",
                ""
            ])
            for action in action_items:
                lines.append(f"- [ ] {action}")
            lines.append("")

        if transcript:
            lines.extend([
                "---",
                "",
                "## Full Transcript",
                "",
                "```",
                transcript,
                "```",
                ""
            ])

        return "\n".join(lines)

    def move_to_archive(self, file_path: str) -> str:
        """
        Move a file to the Archives category

        Args:
            file_path: Current file path (relative to base_path)

        Returns:
            New file path in archives
        """
        current_path = self.base_path / file_path
        if not current_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine content type and filename
        filename = current_path.name
        content_type = current_path.parent.name

        # Build archive path
        archive_path = self.content_paths["archives"] / content_type
        archive_path.mkdir(parents=True, exist_ok=True)
        new_path = archive_path / filename

        # Move file
        current_path.rename(new_path)

        return str(new_path.relative_to(self.base_path))

    def read_content(self, file_path: str) -> str:
        """
        Read content file

        Args:
            file_path: Relative file path from base_path

        Returns:
            File contents
        """
        full_path = self.base_path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()


# Singleton instance
_storage_service = None


def get_file_storage() -> PARAFileStorage:
    """Get or create PARA file storage singleton"""
    global _storage_service
    if _storage_service is None:
        _storage_service = PARAFileStorage()
    return _storage_service
