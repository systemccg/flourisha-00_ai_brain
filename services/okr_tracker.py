"""
OKR Tracker Service
Manages quarterly Objectives and Key Results with weekly measurement and progress tracking
"""
import os
import yaml
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from supabase import create_client, Client
from dotenv import load_dotenv
import asyncio
import logging

# Load environment variables
load_dotenv('/root/.claude/.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class KeyResult:
    """Represents a single Key Result"""
    id: str
    title: str
    target: float
    unit: str
    current: float = 0.0

    @property
    def progress_pct(self) -> float:
        """Calculate progress percentage"""
        if self.target == 0:
            return 0.0
        return min(100.0, (self.current / self.target) * 100)

    @property
    def is_lagging(self) -> bool:
        """Determine if KR is behind schedule based on week of quarter"""
        # Assume 13 weeks per quarter
        current_week = self._get_week_of_quarter()
        expected_progress = (current_week / 13) * 100
        return self.progress_pct < (expected_progress - 10)  # 10% tolerance

    def _get_week_of_quarter(self) -> int:
        """Get current week number within quarter (1-13)"""
        now = datetime.now()
        quarter_start = self._get_quarter_start(now)
        days_into_quarter = (now - quarter_start).days
        return min(13, (days_into_quarter // 7) + 1)

    def _get_quarter_start(self, date: datetime) -> datetime:
        """Get start date of current quarter"""
        quarter = (date.month - 1) // 3
        month = quarter * 3 + 1
        return datetime(date.year, month, 1)


@dataclass
class Objective:
    """Represents a quarterly Objective with Key Results"""
    id: str
    title: str
    description: str
    owner: str
    target_completion: str
    key_results: List[KeyResult]

    @property
    def progress_pct(self) -> float:
        """Calculate overall objective progress as average of KRs"""
        if not self.key_results:
            return 0.0
        return sum(kr.progress_pct for kr in self.key_results) / len(self.key_results)

    @property
    def lagging_krs(self) -> List[KeyResult]:
        """Get list of lagging key results"""
        return [kr for kr in self.key_results if kr.is_lagging]


@dataclass
class OKRProgress:
    """Container for OKR progress data"""
    objective_id: str
    title: str
    progress_pct: float
    key_results: List[Dict[str, Any]]


@dataclass
class OneThingCandidate:
    """Candidate task for 'The One Thing' focus"""
    task: str
    project: str
    okr_id: str
    okr_title: str
    kr_id: str
    kr_title: str
    priority_score: float
    rationale: str


class OKRTrackerService:
    """
    OKR Tracking Service with quarterly goal management and progress measurement
    Implements singleton pattern with async initialization
    """

    _instance: Optional['OKRTrackerService'] = None
    _client: Optional[Client] = None
    _initialized: bool = False
    _okrs: Dict[str, Objective] = {}
    _quarter: Optional[str] = None

    def __new__(cls):
        """Singleton pattern to reuse connection"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize OKR tracker"""
        if not self._initialized:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_SERVICE_KEY', os.getenv('SUPABASE_KEY'))

            if url and key:
                self._client = create_client(url, key)
            else:
                logger.warning("Supabase credentials not found, running in offline mode")

            self._initialized = True

    async def initialize(self, quarter: Optional[str] = None):
        """Async initialization - load OKRs for specified quarter"""
        if quarter is None:
            quarter = self._get_current_quarter()

        await self.load_okrs(quarter)
        logger.info(f"OKR Tracker initialized for {quarter}")

    def _get_current_quarter(self) -> str:
        """Get current quarter in format 'Q1_2026'"""
        now = datetime.now()
        quarter_num = ((now.month - 1) // 3) + 1
        return f"Q{quarter_num}_{now.year}"

    async def load_okrs(self, quarter: str, tenant_id: str = 'default') -> bool:
        """
        Load OKRs from Supabase for specified quarter, with YAML fallback

        Args:
            quarter: Quarter identifier (e.g., 'Q1_2026')
            tenant_id: Tenant identifier for multi-tenant support

        Returns:
            bool: True if loaded successfully
        """
        self._okrs = {}
        self._quarter = quarter
        self._tenant_id = tenant_id

        # Try Supabase first
        if self._client:
            try:
                result = self._client.table('okr_tracking').select('*').eq(
                    'tenant_id', tenant_id
                ).eq('quarter', quarter).execute()

                if result.data:
                    # Group by objective_id
                    objectives_map = {}
                    for row in result.data:
                        obj_id = row['objective_id']
                        if obj_id not in objectives_map:
                            objectives_map[obj_id] = {
                                'id': obj_id,
                                'title': row['objective_title'],
                                'description': row.get('objective_description', ''),
                                'owner': row.get('owner', ''),
                                'target_completion': row.get('target_completion_date', ''),
                                'key_results': []
                            }

                        objectives_map[obj_id]['key_results'].append({
                            'id': row['key_result_id'],
                            'title': row['key_result_title'],
                            'target': float(row['key_result_target']),
                            'unit': row.get('key_result_unit', 'units'),
                            'current': float(row.get('key_result_current', 0)),
                            'db_id': row['id']  # Store DB UUID for updates
                        })

                    # Convert to Objective dataclasses
                    for obj_id, obj_data in objectives_map.items():
                        key_results = []
                        for kr_data in obj_data['key_results']:
                            kr = KeyResult(
                                id=kr_data['id'],
                                title=kr_data['title'],
                                target=kr_data['target'],
                                unit=kr_data['unit'],
                                current=kr_data['current']
                            )
                            # Store db_id for later updates
                            kr._db_id = kr_data.get('db_id')
                            key_results.append(kr)

                        objective = Objective(
                            id=obj_data['id'],
                            title=obj_data['title'],
                            description=obj_data['description'],
                            owner=obj_data['owner'],
                            target_completion=obj_data['target_completion'],
                            key_results=key_results
                        )
                        self._okrs[objective.id] = objective

                    logger.info(f"Loaded {len(self._okrs)} objectives from Supabase for {quarter}")
                    return True

            except Exception as e:
                logger.warning(f"Error loading from Supabase, falling back to YAML: {e}")

        # Fallback to YAML file
        return await self._load_okrs_from_yaml(quarter)

    async def _load_okrs_from_yaml(self, quarter: str) -> bool:
        """Fallback: Load OKRs from YAML file"""
        try:
            okr_dir = Path('/root/flourisha/00_AI_Brain/okr')
            okr_file = okr_dir / f"{quarter}.yaml"

            if not okr_file.exists():
                logger.error(f"OKR file not found: {okr_file}")
                return False

            with open(okr_file, 'r') as f:
                data = yaml.safe_load(f)

            for obj_data in data.get('objectives', []):
                key_results = []
                for kr_data in obj_data.get('key_results', []):
                    kr = KeyResult(
                        id=kr_data['id'],
                        title=kr_data['title'],
                        target=float(kr_data['target']),
                        unit=kr_data.get('unit', 'units'),
                        current=float(kr_data.get('current', 0))
                    )
                    key_results.append(kr)

                objective = Objective(
                    id=obj_data['id'],
                    title=obj_data['title'],
                    description=obj_data['description'],
                    owner=obj_data['owner'],
                    target_completion=obj_data['target_completion'],
                    key_results=key_results
                )
                self._okrs[objective.id] = objective

            logger.info(f"Loaded {len(self._okrs)} objectives from YAML for {quarter}")
            return True

        except Exception as e:
            logger.error(f"Error loading OKRs from YAML: {e}")
            return False

    async def get_okr_progress(self, period: str = 'weekly') -> Dict[str, OKRProgress]:
        """
        Calculate progress for all OKRs for specified period

        Args:
            period: Time period ('weekly', 'monthly', 'quarterly')

        Returns:
            Dict mapping objective_id to OKRProgress
        """
        progress_data = {}

        for obj_id, objective in self._okrs.items():
            kr_list = []
            for kr in objective.key_results:
                kr_list.append({
                    'id': kr.id,
                    'title': kr.title,
                    'target': kr.target,
                    'current': kr.current,
                    'unit': kr.unit,
                    'progress_pct': kr.progress_pct,
                    'is_lagging': kr.is_lagging
                })

            progress_data[obj_id] = OKRProgress(
                objective_id=obj_id,
                title=objective.title,
                progress_pct=objective.progress_pct,
                key_results=kr_list
            )

        return progress_data

    async def get_weekly_focus(self) -> List[Dict[str, Any]]:
        """
        Identify Key Results that are lagging and need focus this week

        Returns:
            List of dicts with prioritized KRs for weekly focus
        """
        focus_items = []

        for objective in self._okrs.values():
            for kr in objective.lagging_krs:
                gap = self._calculate_progress_gap(kr)

                focus_items.append({
                    'objective_id': objective.id,
                    'objective_title': objective.title,
                    'kr_id': kr.id,
                    'kr_title': kr.title,
                    'current': kr.current,
                    'target': kr.target,
                    'unit': kr.unit,
                    'progress_pct': kr.progress_pct,
                    'progress_gap': gap,
                    'priority': 'high' if gap > 20 else 'medium'
                })

        # Sort by progress gap (largest gaps first)
        focus_items.sort(key=lambda x: x['progress_gap'], reverse=True)

        return focus_items

    def _calculate_progress_gap(self, kr: KeyResult) -> float:
        """Calculate how far behind schedule a KR is"""
        current_week = kr._get_week_of_quarter()
        expected_progress = (current_week / 13) * 100
        return max(0, expected_progress - kr.progress_pct)

    async def measure_daily_contribution(
        self,
        work_items: List[str],
        tenant_id: str = 'default'
    ) -> Dict[str, float]:
        """
        Map work items to OKRs and calculate contribution percentage

        Args:
            work_items: List of work item descriptions from daily activity
            tenant_id: Tenant identifier

        Returns:
            Dict mapping okr_id to contribution_pct
        """
        contributions = {}

        # Simple keyword matching for now
        # Future enhancement: Use LLM for semantic matching
        for obj_id, objective in self._okrs.items():
            total_matches = 0

            for work_item in work_items:
                work_item_lower = work_item.lower()

                # Check if work item relates to objective or KRs
                if self._matches_okr(work_item_lower, objective):
                    total_matches += 1

            if total_matches > 0:
                # Calculate contribution as percentage of work items
                contribution_pct = (total_matches / len(work_items)) * 100
                contributions[obj_id] = contribution_pct

        return contributions

    def _matches_okr(self, work_item: str, objective: Objective) -> bool:
        """Check if work item matches objective or any KR"""
        # Extract keywords from objective and KRs
        keywords = set()

        # Add objective keywords
        keywords.update(objective.title.lower().split())
        keywords.update(objective.description.lower().split())

        # Add KR keywords
        for kr in objective.key_results:
            keywords.update(kr.title.lower().split())

        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = keywords - stop_words

        # Check if any keyword appears in work item
        return any(keyword in work_item for keyword in keywords if len(keyword) > 3)

    async def generate_okr_report(self, period: str = 'weekly') -> Dict[str, Any]:
        """
        Generate comprehensive OKR report with progress, trends, and blockers

        Args:
            period: Report period ('weekly', 'monthly', 'quarterly')

        Returns:
            Comprehensive report dict
        """
        progress = await self.get_okr_progress(period)
        focus = await self.get_weekly_focus()

        # Calculate summary statistics
        total_objectives = len(self._okrs)
        avg_progress = sum(p.progress_pct for p in progress.values()) / total_objectives if total_objectives > 0 else 0

        on_track = sum(1 for obj in self._okrs.values() if obj.progress_pct >= 70)
        at_risk = sum(1 for obj in self._okrs.values() if 40 <= obj.progress_pct < 70)
        behind = sum(1 for obj in self._okrs.values() if obj.progress_pct < 40)

        report = {
            'quarter': self._quarter,
            'period': period,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_objectives': total_objectives,
                'average_progress': round(avg_progress, 1),
                'on_track': on_track,
                'at_risk': at_risk,
                'behind': behind
            },
            'objectives': [asdict(p) for p in progress.values()],
            'weekly_focus': focus,
            'recommendations': self._generate_recommendations(focus)
        }

        return report

    def _generate_recommendations(self, focus_items: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations based on focus items"""
        recommendations = []

        if not focus_items:
            recommendations.append("All OKRs are on track! Maintain current momentum.")
        else:
            top_focus = focus_items[0]
            recommendations.append(
                f"Priority: Focus on '{top_focus['kr_title']}' - currently {top_focus['progress_gap']:.1f}% behind schedule"
            )

            if len(focus_items) > 1:
                recommendations.append(
                    f"Secondary focus: {len(focus_items) - 1} other KRs need attention this week"
                )

        return recommendations

    async def get_one_thing_candidates(self) -> List[OneThingCandidate]:
        """
        Return top 3 tasks that advance lagging Key Results for morning report

        Returns:
            List of OneThingCandidate objects sorted by priority
        """
        candidates = []
        focus_items = await self.get_weekly_focus()

        # Take top 5 lagging KRs
        for focus in focus_items[:5]:
            # Generate candidate task for this KR
            candidate = OneThingCandidate(
                task=self._generate_task_for_kr(focus),
                project=focus['objective_title'],
                okr_id=focus['objective_id'],
                okr_title=focus['objective_title'],
                kr_id=focus['kr_id'],
                kr_title=focus['kr_title'],
                priority_score=focus['progress_gap'],
                rationale=f"Closes {focus['progress_gap']:.1f}% gap on {focus['kr_title']}"
            )
            candidates.append(candidate)

        # Sort by priority score
        candidates.sort(key=lambda x: x.priority_score, reverse=True)

        return candidates[:3]

    def _generate_task_for_kr(self, focus_item: Dict[str, Any]) -> str:
        """Generate specific actionable task for a KR"""
        kr_title = focus_item['kr_title']
        current = focus_item['current']
        target = focus_item['target']
        unit = focus_item['unit']

        # Simple task generation - can be enhanced with LLM
        gap = target - current

        if 'complete' in kr_title.lower() or 'deploy' in kr_title.lower():
            return f"Work on next item for: {kr_title}"
        elif 'maintain' in kr_title.lower():
            return f"Review and improve: {kr_title}"
        else:
            return f"Progress {kr_title} (need {gap:.0f} more {unit})"

    async def update_kr_progress(
        self,
        objective_id: str,
        kr_id: str,
        new_value: float,
        tenant_id: str = 'default',
        notes: str = None
    ) -> bool:
        """
        Update progress for a specific Key Result

        Args:
            objective_id: Objective identifier
            kr_id: Key Result identifier
            new_value: New current value
            tenant_id: Tenant identifier
            notes: Optional notes about the update

        Returns:
            bool: True if updated successfully
        """
        try:
            objective = self._okrs.get(objective_id)
            if not objective:
                logger.error(f"Objective not found: {objective_id}")
                return False

            for kr in objective.key_results:
                if kr.id == kr_id:
                    old_value = kr.current
                    kr.current = new_value
                    logger.info(f"Updated {kr.title}: {old_value} -> {new_value} ({kr.progress_pct:.1f}%)")

                    # Persist to Supabase
                    if self._client:
                        await self._persist_kr_update(
                            objective_id, kr_id, old_value, new_value,
                            tenant_id or self._tenant_id, notes
                        )

                    return True

            logger.error(f"Key Result not found: {kr_id}")
            return False

        except Exception as e:
            logger.error(f"Error updating KR progress: {e}")
            return False

    async def _persist_kr_update(
        self,
        objective_id: str,
        kr_id: str,
        old_value: float,
        new_value: float,
        tenant_id: str,
        notes: str = None
    ):
        """Persist KR update to Supabase okr_tracking table"""
        if not self._client:
            return

        try:
            # Update the okr_tracking record
            result = self._client.table('okr_tracking').update({
                'key_result_current': new_value
            }).eq('tenant_id', tenant_id).eq(
                'objective_id', objective_id
            ).eq('key_result_id', kr_id).eq(
                'quarter', self._quarter
            ).execute()

            if result.data:
                logger.info(f"Persisted KR update to Supabase: {objective_id}/{kr_id}")

                # Try to record progress history if the table exists
                try:
                    db_id = result.data[0].get('id') if result.data else None
                    if db_id:
                        self._client.table('okr_progress_history').insert({
                            'okr_tracking_id': db_id,
                            'previous_value': old_value,
                            'new_value': new_value,
                            'change_type': 'progress_update',
                            'notes': notes
                        }).execute()
                except Exception:
                    # okr_progress_history table may not exist yet
                    pass
            else:
                logger.warning(f"No record found to update for {objective_id}/{kr_id}")

        except Exception as e:
            logger.error(f"Error persisting KR update: {e}")


# Singleton instance
okr_tracker = OKRTrackerService()
