#!/usr/bin/env python3
"""
PARA Analyzer - AI Brain Phase 1
Scans PARA folders for changes and analyzes project priorities.

Trigger: Cron job every 4 hours
Output: /root/flourisha/00_AI_Brain/history/para-analysis/YYYY-MM-DD-HHMM.json
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
import logging
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(os.path.expanduser("~/.claude/.env"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
FLOURISHA_ROOT = Path("/root/flourisha")
AI_BRAIN_ROOT = FLOURISHA_ROOT / "00_AI_Brain"
HISTORY_DIR = AI_BRAIN_ROOT / "history" / "para-analysis"
STATE_FILE = HISTORY_DIR / ".last_run_state.json"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

PARA_FOLDERS = {
    "projects": FLOURISHA_ROOT / "01f_Flourisha_Projects",
    "areas": FLOURISHA_ROOT / "02f_Flourisha_Areas",
    "resources": FLOURISHA_ROOT / "03f_Flourisha_Resources",
    "archives": FLOURISHA_ROOT / "04f_Flourisha_Archives"
}

# File patterns to track
TRACKED_EXTENSIONS = {
    ".md", ".py", ".ts", ".js", ".tsx", ".jsx",
    ".json", ".yaml", ".yml", ".txt", ".csv",
    ".sh", ".sql", ".html", ".css"
}

IGNORED_PATTERNS = {
    "node_modules", ".git", "__pycache__", ".venv",
    "venv", "dist", "build", ".next", ".cache"
}


class PARAAnalyzer:
    """Analyzes PARA folder structure for changes and priorities."""

    def __init__(self):
        """Initialize PARA analyzer."""
        self.history_dir = HISTORY_DIR
        self.state_file = STATE_FILE
        self.last_run_state = self._load_last_run_state()

    def _load_last_run_state(self) -> Dict[str, Any]:
        """Load state from last run."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load last run state: {e}")

        return {
            "timestamp": None,
            "file_checksums": {},
            "project_priorities": {}
        }

    def _save_run_state(self, state: Dict[str, Any]) -> None:
        """Save current run state."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save run state: {e}")

    def _should_track_file(self, file_path: Path) -> bool:
        """Determine if file should be tracked."""
        # Check if any ignored pattern in path
        for pattern in IGNORED_PATTERNS:
            if pattern in str(file_path):
                return False

        # Check extension
        return file_path.suffix in TRACKED_EXTENSIONS

    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file."""
        try:
            md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    md5.update(chunk)
            return md5.hexdigest()
        except Exception as e:
            logger.debug(f"Could not checksum {file_path}: {e}")
            return ""

    async def scan_para_folders(self) -> Dict[str, List[Path]]:
        """
        Walk all PARA folders and collect tracked files.

        Returns:
            Dictionary mapping PARA category to list of file paths
        """
        para_files = {
            "projects": [],
            "areas": [],
            "resources": [],
            "archives": []
        }

        try:
            for category, folder_path in PARA_FOLDERS.items():
                if not folder_path.exists():
                    logger.warning(f"PARA folder not found: {folder_path}")
                    continue

                logger.info(f"Scanning {category}: {folder_path}")

                for root, dirs, files in os.walk(folder_path):
                    # Remove ignored directories from traversal
                    dirs[:] = [d for d in dirs if d not in IGNORED_PATTERNS]

                    root_path = Path(root)

                    for file_name in files:
                        file_path = root_path / file_name

                        if self._should_track_file(file_path):
                            para_files[category].append(file_path)

                logger.info(f"Found {len(para_files[category])} files in {category}")

        except Exception as e:
            logger.error(f"Error scanning PARA folders: {e}")

        return para_files

    async def detect_changes(
        self,
        current_files: Dict[str, List[Path]],
        since_timestamp: Optional[datetime]
    ) -> Dict[str, Any]:
        """
        Detect changes since last run.

        Args:
            current_files: Current file structure
            since_timestamp: Timestamp of last run

        Returns:
            Dictionary of detected changes
        """
        changes = {
            "new_files": [],
            "modified_files": [],
            "deleted_files": [],
            "moved_files": []
        }

        try:
            # Get previous checksums
            previous_checksums = self.last_run_state.get("file_checksums", {})
            current_checksums = {}

            # Track all current files
            all_current_files = set()
            for category, files in current_files.items():
                for file_path in files:
                    file_key = str(file_path)
                    all_current_files.add(file_key)

                    # Calculate current checksum
                    checksum = self._calculate_file_checksum(file_path)
                    current_checksums[file_key] = {
                        "checksum": checksum,
                        "modified": file_path.stat().st_mtime,
                        "size": file_path.stat().st_size,
                        "category": category
                    }

                    # Detect new files
                    if file_key not in previous_checksums:
                        changes["new_files"].append({
                            "path": file_key,
                            "category": category,
                            "size": file_path.stat().st_size,
                            "created": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })

                    # Detect modified files
                    elif previous_checksums[file_key]["checksum"] != checksum:
                        changes["modified_files"].append({
                            "path": file_key,
                            "category": category,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })

            # Detect deleted files
            previous_files = set(previous_checksums.keys())
            deleted_files = previous_files - all_current_files

            for file_key in deleted_files:
                changes["deleted_files"].append({
                    "path": file_key,
                    "category": previous_checksums[file_key].get("category", "unknown")
                })

            # Update state with current checksums
            self.last_run_state["file_checksums"] = current_checksums

            logger.info(f"Changes detected: {len(changes['new_files'])} new, "
                       f"{len(changes['modified_files'])} modified, "
                       f"{len(changes['deleted_files'])} deleted")

        except Exception as e:
            logger.error(f"Error detecting changes: {e}")

        return changes

    async def calculate_project_priority(
        self,
        project_path: Path
    ) -> Dict[str, Any]:
        """
        Calculate priority for a project based on multiple factors.

        Args:
            project_path: Path to project directory

        Returns:
            Priority information dictionary
        """
        priority_data = {
            "project": project_path.name,
            "priority_level": "Normal",
            "priority_score": 5.0,
            "factors": {},
            "deadline": None,
            "last_activity": None,
            "activity_level": "Low"
        }

        try:
            # Check README for deadline/priority metadata
            readme_path = project_path / "README.md"
            if readme_path.exists():
                with open(readme_path, 'r') as f:
                    content = f.read().lower()

                    # Extract deadline
                    if "deadline:" in content or "due:" in content:
                        # Simple extraction - can be enhanced
                        for line in content.split('\n'):
                            if "deadline:" in line or "due:" in line:
                                priority_data["factors"]["has_deadline"] = True
                                priority_data["priority_score"] += 2.0

                    # Extract explicit priority
                    if "priority: urgent" in content or "urgent" in content:
                        priority_data["priority_level"] = "Urgent"
                        priority_data["priority_score"] += 3.0
                    elif "priority: high" in content:
                        priority_data["priority_level"] = "High"
                        priority_data["priority_score"] += 2.0

            # Check git commits (if git repo)
            git_dir = project_path / ".git"
            if git_dir.exists():
                try:
                    # Get last commit time using git log
                    import subprocess
                    result = subprocess.run(
                        ["git", "log", "-1", "--format=%ct"],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    if result.returncode == 0 and result.stdout.strip():
                        commit_timestamp = int(result.stdout.strip())
                        last_commit = datetime.fromtimestamp(commit_timestamp)
                        priority_data["last_activity"] = last_commit.isoformat()

                        # Recent commits increase priority
                        days_since_commit = (datetime.now() - last_commit).days
                        if days_since_commit < 1:
                            priority_data["priority_score"] += 2.0
                            priority_data["activity_level"] = "Urgent"
                        elif days_since_commit < 7:
                            priority_data["priority_score"] += 1.0
                            priority_data["activity_level"] = "High"
                        elif days_since_commit < 30:
                            priority_data["activity_level"] = "Normal"
                        else:
                            priority_data["activity_level"] = "Low"

                        priority_data["factors"]["git_active"] = True
                        priority_data["factors"]["days_since_commit"] = days_since_commit

                except Exception as e:
                    logger.debug(f"Could not check git for {project_path}: {e}")

            # Check last modified time
            if not priority_data["last_activity"]:
                mtime = max(
                    (f.stat().st_mtime for f in project_path.rglob("*") if f.is_file()),
                    default=0
                )
                if mtime > 0:
                    last_modified = datetime.fromtimestamp(mtime)
                    priority_data["last_activity"] = last_modified.isoformat()

                    days_since_modified = (datetime.now() - last_modified).days
                    if days_since_modified < 1:
                        priority_data["activity_level"] = "Urgent"
                    elif days_since_modified < 7:
                        priority_data["activity_level"] = "High"

            # Normalize priority score
            priority_data["priority_score"] = min(10.0, priority_data["priority_score"])

            # Set priority level based on score
            if priority_data["priority_score"] >= 8.0:
                priority_data["priority_level"] = "Urgent"
            elif priority_data["priority_score"] >= 6.0:
                priority_data["priority_level"] = "High"
            elif priority_data["priority_score"] >= 4.0:
                priority_data["priority_level"] = "Normal"
            else:
                priority_data["priority_level"] = "Low"

        except Exception as e:
            logger.error(f"Error calculating priority for {project_path}: {e}")

        return priority_data

    async def analyze_activity_level(
        self,
        changes: Dict[str, Any],
        project_path: Path
    ) -> str:
        """
        Categorize project activity level based on recent changes.

        Args:
            changes: Detected changes
            project_path: Path to project

        Returns:
            Activity level: Urgent/High/Normal/Low/Archived
        """
        try:
            project_name = str(project_path)

            # Count changes for this project
            new_count = sum(1 for f in changes["new_files"] if project_name in f["path"])
            modified_count = sum(1 for f in changes["modified_files"] if project_name in f["path"])
            total_changes = new_count + modified_count

            if total_changes >= 10:
                return "Urgent"
            elif total_changes >= 5:
                return "High"
            elif total_changes >= 1:
                return "Normal"
            else:
                # Check if archived
                if "04f_Flourisha_Archives" in project_name:
                    return "Archived"
                return "Low"

        except Exception as e:
            logger.error(f"Error analyzing activity level: {e}")
            return "Low"

    async def generate_analysis(self) -> Dict[str, Any]:
        """
        Generate comprehensive PARA analysis.

        Returns:
            Complete analysis data structure
        """
        try:
            timestamp = datetime.now()
            since_last_run = self.last_run_state.get("timestamp")

            # Scan folders
            current_files = await self.scan_para_folders()

            # Detect changes
            changes = await self.detect_changes(
                current_files,
                datetime.fromisoformat(since_last_run) if since_last_run else None
            )

            # Analyze project priorities
            project_activity = {}
            projects_folder = PARA_FOLDERS["projects"]

            if projects_folder.exists():
                for project_dir in projects_folder.iterdir():
                    if project_dir.is_dir() and project_dir.name not in IGNORED_PATTERNS:
                        priority_data = await self.calculate_project_priority(project_dir)
                        activity_level = await self.analyze_activity_level(changes, project_dir)

                        # Count files changed
                        files_changed = sum(
                            1 for f in changes["new_files"] + changes["modified_files"]
                            if str(project_dir) in f["path"]
                        )

                        project_activity[project_dir.name] = {
                            "files_changed": files_changed,
                            "priority": priority_data,
                            "activity_level": activity_level
                        }

            # Detect priority changes
            previous_priorities = self.last_run_state.get("project_priorities", {})
            priority_changes = []

            for project, data in project_activity.items():
                current_level = data["priority"]["priority_level"]
                previous_level = previous_priorities.get(project, {}).get("priority_level", "Normal")

                if current_level != previous_level:
                    priority_changes.append({
                        "project": project,
                        "from": previous_level,
                        "to": current_level
                    })

            # Build analysis structure
            analysis = {
                "timestamp": timestamp.isoformat(),
                "since_last_run": since_last_run,
                "run_interval_hours": None,
                "changes": changes,
                "project_activity": project_activity,
                "priority_changes": priority_changes,
                "cross_references": [],  # Can be enhanced with content analysis
                "summary": {
                    "total_files_tracked": sum(len(files) for files in current_files.values()),
                    "total_changes": len(changes["new_files"]) + len(changes["modified_files"]),
                    "active_projects": sum(
                        1 for p in project_activity.values()
                        if p["activity_level"] in ["Urgent", "High"]
                    ),
                    "urgent_projects": [
                        name for name, data in project_activity.items()
                        if data["priority"]["priority_level"] == "Urgent"
                    ]
                },
                "metadata": {
                    "analyzer_version": "1.0.0",
                    "para_folders": {k: str(v) for k, v in PARA_FOLDERS.items()}
                }
            }

            # Calculate run interval
            if since_last_run:
                interval = timestamp - datetime.fromisoformat(since_last_run)
                analysis["run_interval_hours"] = round(interval.total_seconds() / 3600, 1)

            # Save analysis
            filename = timestamp.strftime("%Y-%m-%d-%H%M") + ".json"
            output_path = self.history_dir / filename

            with open(output_path, 'w') as f:
                json.dump(analysis, f, indent=2)

            logger.info(f"PARA analysis saved to {output_path}")

            # Update state
            self.last_run_state["timestamp"] = timestamp.isoformat()
            self.last_run_state["project_priorities"] = {
                name: data["priority"]
                for name, data in project_activity.items()
            }
            self._save_run_state(self.last_run_state)

            return analysis

        except Exception as e:
            logger.error(f"Error generating PARA analysis: {e}")
            raise


async def main():
    """Main entry point for PARA analyzer."""
    try:
        analyzer = PARAAnalyzer()
        analysis = await analyzer.generate_analysis()

        # Output summary
        print(json.dumps({
            "success": True,
            "timestamp": analysis["timestamp"],
            "total_changes": analysis["summary"]["total_changes"],
            "active_projects": analysis["summary"]["active_projects"],
            "urgent_projects": analysis["summary"]["urgent_projects"],
            "output_path": str(HISTORY_DIR / f"{datetime.now().strftime('%Y-%m-%d-%H%M')}.json")
        }, indent=2))

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
