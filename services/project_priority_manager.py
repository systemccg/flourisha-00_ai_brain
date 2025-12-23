"""
Project Priority Manager Service
Calculates project priorities and determines 'The One Thing' to focus on
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProjectPriority:
    """Project priority information"""
    project_name: str
    project_path: str
    priority: str  # 'Urgent', 'High', 'Normal', 'Low', 'Archived'
    score: int  # 0-100 for ranking
    reasons: List[str]
    deadline: Optional[datetime] = None
    last_modified: Optional[datetime] = None


@dataclass
class OneThingDecision:
    """The One Thing decision result"""
    project: str
    task: str
    why: str
    okr_contribution: str
    priority: str
    confidence: float


class ProjectPriorityManager:
    """
    Manages project priority calculation and 'The One Thing' determination
    """

    PRIORITY_SCORES = {
        'Urgent': 100,
        'High': 75,
        'Normal': 50,
        'Low': 25,
        'Archived': 0
    }

    def __init__(self, projects_dir: str = '/root/flourisha/01f_Projects'):
        """Initialize project priority manager"""
        self.projects_dir = Path(projects_dir)

    def calculate_project_priority(self, project_path: str) -> ProjectPriority:
        """
        Calculate priority for a single project using multiple signals

        Args:
            project_path: Path to project directory

        Returns:
            ProjectPriority object with calculated priority
        """
        path = Path(project_path)
        project_name = path.name
        reasons = []
        score = 50  # Default to Normal
        priority = 'Normal'
        deadline = None
        last_modified = None

        try:
            # Check if in Archives (highest signal)
            if 'Archive' in str(path) or 'archive' in str(path):
                return ProjectPriority(
                    project_name=project_name,
                    project_path=str(path),
                    priority='Archived',
                    score=0,
                    reasons=['Located in Archive directory']
                )

            # Check for explicit priority in PROJECT_REGISTRY.md
            registry_priority = self._check_registry_priority(path)
            if registry_priority:
                priority = registry_priority
                score = self.PRIORITY_SCORES[priority]
                reasons.append(f'Explicit priority in PROJECT_REGISTRY: {priority}')
                return ProjectPriority(
                    project_name=project_name,
                    project_path=str(path),
                    priority=priority,
                    score=score,
                    reasons=reasons
                )

            # Extract deadline from README or other docs
            deadline_info = self._extract_deadline(path)
            if deadline_info:
                deadline, days_until = deadline_info
                if days_until <= 7:
                    priority = 'Urgent'
                    score = 100
                    reasons.append(f'Deadline in {days_until} days')
                elif days_until <= 30:
                    priority = 'High'
                    score = 85
                    reasons.append(f'Deadline in {days_until} days')

            # Check recent activity (file modifications)
            last_modified_days = self._get_last_modified_days(path)
            if last_modified_days is not None:
                last_modified = datetime.now() - timedelta(days=last_modified_days)

                if last_modified_days <= 3 and score < 85:
                    priority = 'High'
                    score = max(score, 80)
                    reasons.append(f'Active: modified {last_modified_days} days ago')
                elif last_modified_days <= 14 and score < 75:
                    priority = 'Normal'
                    score = max(score, 60)
                    reasons.append(f'Recent activity: {last_modified_days} days ago')
                elif last_modified_days > 90:
                    priority = 'Low'
                    score = min(score, 30)
                    reasons.append(f'Inactive: {last_modified_days} days since update')

            # Check git commit activity if .git exists
            git_activity = self._check_git_activity(path)
            if git_activity:
                commits, days = git_activity
                if commits > 5 and days <= 7 and score < 85:
                    priority = 'High'
                    score = max(score, 80)
                    reasons.append(f'{commits} commits in last {days} days')

            # PARA location analysis
            para_priority = self._analyze_para_location(path)
            if para_priority:
                if para_priority == 'Archived':
                    priority = 'Archived'
                    score = 0
                    reasons.append('Located in PARA Archives')

            if not reasons:
                reasons.append('Default priority based on location')

        except Exception as e:
            logger.error(f"Error calculating priority for {project_path}: {e}")
            reasons.append(f'Error in calculation: {str(e)}')

        return ProjectPriority(
            project_name=project_name,
            project_path=str(path),
            priority=priority,
            score=score,
            reasons=reasons,
            deadline=deadline,
            last_modified=last_modified
        )

    def _check_registry_priority(self, path: Path) -> Optional[str]:
        """Check PROJECT_REGISTRY.md for explicit priority"""
        try:
            registry_files = [
                path / 'PROJECT_REGISTRY.md',
                path / 'README.md',
                path / 'project.md'
            ]

            for registry in registry_files:
                if registry.exists():
                    content = registry.read_text()
                    # Look for priority markers
                    if re.search(r'priority:\s*urgent', content, re.IGNORECASE):
                        return 'Urgent'
                    elif re.search(r'priority:\s*high', content, re.IGNORECASE):
                        return 'High'
                    elif re.search(r'priority:\s*normal', content, re.IGNORECASE):
                        return 'Normal'
                    elif re.search(r'priority:\s*low', content, re.IGNORECASE):
                        return 'Low'

        except Exception as e:
            logger.debug(f"Error checking registry priority: {e}")

        return None

    def _extract_deadline(self, path: Path) -> Optional[Tuple[datetime, int]]:
        """Extract deadline from project documentation"""
        try:
            doc_files = list(path.glob('**/*.md'))[:10]  # Check first 10 markdown files

            for doc_file in doc_files:
                try:
                    content = doc_file.read_text()

                    # Look for deadline patterns
                    deadline_patterns = [
                        r'deadline:\s*(\d{4}-\d{2}-\d{2})',
                        r'due:\s*(\d{4}-\d{2}-\d{2})',
                        r'due date:\s*(\d{4}-\d{2}-\d{2})',
                        r'target:\s*(\d{4}-\d{2}-\d{2})'
                    ]

                    for pattern in deadline_patterns:
                        match = re.search(pattern, content, re.IGNORECASE)
                        if match:
                            date_str = match.group(1)
                            deadline = datetime.strptime(date_str, '%Y-%m-%d')
                            days_until = (deadline - datetime.now()).days
                            return (deadline, days_until)

                except Exception as e:
                    logger.debug(f"Error reading {doc_file}: {e}")
                    continue

        except Exception as e:
            logger.debug(f"Error extracting deadline: {e}")

        return None

    def _get_last_modified_days(self, path: Path) -> Optional[int]:
        """Get days since last file modification in project"""
        try:
            # Get all files in project (excluding .git)
            files = [f for f in path.rglob('*') if f.is_file() and '.git' not in str(f)]

            if not files:
                return None

            # Find most recently modified file
            latest = max(files, key=lambda f: f.stat().st_mtime)
            mod_time = datetime.fromtimestamp(latest.stat().st_mtime)
            days_ago = (datetime.now() - mod_time).days

            return days_ago

        except Exception as e:
            logger.debug(f"Error getting last modified: {e}")
            return None

    def _check_git_activity(self, path: Path) -> Optional[Tuple[int, int]]:
        """Check git commit activity in last 7 days"""
        try:
            git_dir = path / '.git'
            if not git_dir.exists():
                return None

            # This is a simplified check - in production would use gitpython
            # For now, just check if git directory was recently modified
            git_mod = datetime.fromtimestamp(git_dir.stat().st_mtime)
            days_ago = (datetime.now() - git_mod).days

            # Estimate commits based on git dir activity
            if days_ago <= 3:
                return (7, 3)  # Assume active development
            elif days_ago <= 7:
                return (3, 7)
            else:
                return (0, days_ago)

        except Exception as e:
            logger.debug(f"Error checking git activity: {e}")
            return None

    def _analyze_para_location(self, path: Path) -> Optional[str]:
        """Determine priority based on PARA location"""
        path_str = str(path).lower()

        if 'archive' in path_str:
            return 'Archived'
        elif 'area' in path_str:
            return 'Normal'  # Areas are ongoing
        elif 'project' in path_str:
            return 'High'  # Active projects
        elif 'resource' in path_str:
            return 'Low'  # Reference material

        return None

    def get_all_project_priorities(self) -> Dict[str, ProjectPriority]:
        """
        Scan all projects and calculate priorities

        Returns:
            Dict mapping project name to ProjectPriority
        """
        priorities = {}

        try:
            if not self.projects_dir.exists():
                logger.warning(f"Projects directory not found: {self.projects_dir}")
                return priorities

            # Find all project directories (1-2 levels deep)
            for project_dir in self.projects_dir.iterdir():
                if project_dir.is_dir() and not project_dir.name.startswith('.'):
                    priority = self.calculate_project_priority(str(project_dir))
                    priorities[priority.project_name] = priority

                    # Check subdirectories
                    for subdir in project_dir.iterdir():
                        if subdir.is_dir() and not subdir.name.startswith('.'):
                            sub_priority = self.calculate_project_priority(str(subdir))
                            priorities[sub_priority.project_name] = sub_priority

        except Exception as e:
            logger.error(f"Error scanning projects: {e}")

        return priorities

    def determine_one_thing(
        self,
        okr_progress: Dict,
        project_priorities: Dict[str, ProjectPriority],
        yesterday_patterns: Optional[Dict] = None
    ) -> OneThingDecision:
        """
        Determine 'The One Thing' to focus on today

        Args:
            okr_progress: OKR progress data from okr_tracker
            project_priorities: Project priorities from get_all_project_priorities
            yesterday_patterns: Optional data about yesterday's work

        Returns:
            OneThingDecision with project, task, and rationale
        """
        try:
            # Filter to Urgent/High priority projects
            high_priority_projects = {
                name: proj for name, proj in project_priorities.items()
                if proj.priority in ['Urgent', 'High']
            }

            if not high_priority_projects:
                # Fallback to Normal priority if no urgent/high
                high_priority_projects = {
                    name: proj for name, proj in project_priorities.items()
                    if proj.priority == 'Normal'
                }

            # Identify lagging OKRs
            lagging_okrs = self._find_lagging_okrs(okr_progress)

            # Match projects to lagging OKRs
            best_match = self._match_project_to_okr(
                high_priority_projects,
                lagging_okrs,
                yesterday_patterns
            )

            if best_match:
                return best_match

            # Fallback: Just pick highest priority project
            if high_priority_projects:
                top_project = max(
                    high_priority_projects.values(),
                    key=lambda p: p.score
                )

                return OneThingDecision(
                    project=top_project.project_name,
                    task=self._get_next_task(top_project),
                    why=f"Highest priority project ({top_project.priority})",
                    okr_contribution="General progress",
                    priority=top_project.priority,
                    confidence=0.7
                )

            # Ultimate fallback
            return OneThingDecision(
                project="Daily Planning",
                task="Review and prioritize projects",
                why="No clear priority projects found",
                okr_contribution="Strategic planning",
                priority="Normal",
                confidence=0.5
            )

        except Exception as e:
            logger.error(f"Error determining one thing: {e}")
            return OneThingDecision(
                project="Error",
                task="Review project priorities",
                why=f"Error in calculation: {str(e)}",
                okr_contribution="System maintenance",
                priority="Normal",
                confidence=0.3
            )

    def _find_lagging_okrs(self, okr_progress: Dict) -> List[Dict]:
        """Extract lagging OKRs from progress data"""
        lagging = []

        for obj_id, progress in okr_progress.items():
            if hasattr(progress, 'key_results'):
                for kr in progress.key_results:
                    if kr.get('is_lagging', False):
                        lagging.append({
                            'objective_id': obj_id,
                            'objective_title': progress.title,
                            'kr_id': kr['id'],
                            'kr_title': kr['title'],
                            'progress_pct': kr['progress_pct']
                        })

        return lagging

    def _match_project_to_okr(
        self,
        projects: Dict[str, ProjectPriority],
        lagging_okrs: List[Dict],
        yesterday_patterns: Optional[Dict]
    ) -> Optional[OneThingDecision]:
        """Match projects to lagging OKRs and determine best focus"""

        if not lagging_okrs:
            return None

        # Simple keyword matching for now
        best_score = 0
        best_match = None

        for okr in lagging_okrs:
            okr_keywords = set(okr['kr_title'].lower().split())

            for project_name, project in projects.items():
                project_keywords = set(project_name.lower().split())

                # Calculate match score
                match_score = len(okr_keywords & project_keywords)

                # Boost if matches yesterday's work
                if yesterday_patterns and project_name in str(yesterday_patterns):
                    match_score += 2

                # Boost for urgency
                if project.priority == 'Urgent':
                    match_score += 3
                elif project.priority == 'High':
                    match_score += 1

                if match_score > best_score:
                    best_score = match_score
                    best_match = OneThingDecision(
                        project=project_name,
                        task=self._get_next_task(project),
                        why=f"Advances lagging OKR: {okr['kr_title']}",
                        okr_contribution=f"{okr['objective_title']} - {okr['kr_title']}",
                        priority=project.priority,
                        confidence=min(0.95, 0.6 + (match_score * 0.1))
                    )

        return best_match

    def _get_next_task(self, project: ProjectPriority) -> str:
        """Determine next specific task within project"""
        try:
            # Look for TODO.md or README.md with tasks
            project_path = Path(project.project_path)

            todo_files = [
                project_path / 'TODO.md',
                project_path / 'TASKS.md',
                project_path / 'README.md'
            ]

            for todo_file in todo_files:
                if todo_file.exists():
                    content = todo_file.read_text()

                    # Look for unchecked tasks
                    task_match = re.search(r'- \[ \] (.+)', content)
                    if task_match:
                        return task_match.group(1).strip()

                    # Look for "Next:" or "TODO:" sections
                    next_match = re.search(r'(?:Next|TODO):\s*(.+)', content, re.IGNORECASE)
                    if next_match:
                        return next_match.group(1).strip()

            # Generic fallback
            return f"Continue work on {project.project_name}"

        except Exception as e:
            logger.debug(f"Error getting next task: {e}")
            return f"Work on {project.project_name}"


# Convenience instance
project_priority_manager = ProjectPriorityManager()
