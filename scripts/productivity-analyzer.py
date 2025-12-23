#!/usr/bin/env python3
"""
Productivity Analyzer - AI Brain Phase 1
Analyzes daily productivity and generates insights for morning reports.

Triggered by: evening-productivity-analysis.ts hook
Output: /root/flourisha/00_AI_Brain/history/daily-analysis/YYYY-MM-DD.json
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
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
AI_BRAIN_ROOT = Path("/root/flourisha/00_AI_Brain")
HISTORY_DIR = AI_BRAIN_ROOT / "history" / "daily-analysis"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

# Productivity scoring weights
IDEAL_WORK_HOURS_MIN = 6.0
IDEAL_WORK_HOURS_MAX = 8.0
IDEAL_DEEP_WORK_RATIO = 0.6  # 60%+
SCORING_WEIGHTS = {
    "hours_worked": 0.25,
    "deep_work_ratio": 0.35,
    "accomplishments": 0.25,
    "focus_quality": 0.15
}


class ProductivityAnalyzer:
    """Analyzes daily productivity and generates insights."""

    def __init__(self):
        """Initialize productivity analyzer."""
        self.history_dir = HISTORY_DIR
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not set - AI analysis will be limited")

    async def calculate_productivity_score(self, session_data: Dict[str, Any]) -> float:
        """
        Calculate productivity score from 1-10 based on multiple factors.

        Args:
            session_data: Dictionary containing work session data

        Returns:
            Productivity score between 1.0 and 10.0
        """
        try:
            hours_worked = session_data.get("hours_worked", 0.0)
            deep_work_hours = session_data.get("deep_work_hours", 0.0)
            shallow_work_hours = session_data.get("shallow_work_hours", 0.0)
            accomplishments = session_data.get("accomplishments", [])
            focus_quality = session_data.get("focus_quality", {})
            blockers = session_data.get("blockers", [])

            # Score components (each normalized to 0-10)
            scores = {}

            # 1. Hours worked score (target: 6-8 hours)
            if hours_worked >= IDEAL_WORK_HOURS_MIN and hours_worked <= IDEAL_WORK_HOURS_MAX:
                scores["hours_worked"] = 10.0
            elif hours_worked < IDEAL_WORK_HOURS_MIN:
                scores["hours_worked"] = max(0, (hours_worked / IDEAL_WORK_HOURS_MIN) * 10.0)
            else:  # Overwork penalty
                penalty = min(0.3, (hours_worked - IDEAL_WORK_HOURS_MAX) * 0.05)
                scores["hours_worked"] = max(7.0, 10.0 - penalty * 10)

            # 2. Deep work ratio score (target: 60%+)
            total_work = deep_work_hours + shallow_work_hours
            if total_work > 0:
                deep_work_ratio = deep_work_hours / total_work
                if deep_work_ratio >= IDEAL_DEEP_WORK_RATIO:
                    scores["deep_work_ratio"] = 10.0
                else:
                    scores["deep_work_ratio"] = (deep_work_ratio / IDEAL_DEEP_WORK_RATIO) * 10.0
            else:
                scores["deep_work_ratio"] = 0.0

            # 3. Accomplishments score (quality over quantity)
            accomplishment_count = len(accomplishments)
            if accomplishment_count >= 5:
                scores["accomplishments"] = 10.0
            elif accomplishment_count >= 3:
                scores["accomplishments"] = 8.0
            elif accomplishment_count >= 1:
                scores["accomplishments"] = 6.0
            else:
                scores["accomplishments"] = 3.0

            # Penalty for blockers
            blocker_penalty = min(2.0, len(blockers) * 0.5)
            scores["accomplishments"] = max(0, scores["accomplishments"] - blocker_penalty)

            # 4. Focus quality score (from session data)
            avg_focus = focus_quality.get("average", 7.0)
            scores["focus_quality"] = min(10.0, avg_focus)

            # Calculate weighted score
            final_score = sum(
                scores[key] * SCORING_WEIGHTS[key]
                for key in SCORING_WEIGHTS.keys()
            )

            # Round to 1 decimal place
            return round(final_score, 1)

        except Exception as e:
            logger.error(f"Error calculating productivity score: {e}")
            return 5.0  # Default middle score on error

    async def detect_patterns(self, daily_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect productivity patterns from last 5 days.

        Args:
            daily_history: List of daily analysis data from past 5 days

        Returns:
            Dictionary of detected patterns
        """
        patterns = {
            "peak_energy_times": [],
            "energy_dips": [],
            "context_switching_impact": None,
            "time_of_day_correlation": {},
            "weekly_trend": None,
            "best_productivity_day": None,
            "consistency_score": 0.0
        }

        try:
            if not daily_history or len(daily_history) < 2:
                return patterns

            # Extract energy tracking data by time of day
            energy_by_hour = {}
            productivity_scores = []
            context_switches = []

            for day in daily_history:
                energy_tracking = day.get("energy_tracking", {})
                for time_str, level in energy_tracking.items():
                    hour = int(time_str.split(":")[0])
                    if hour not in energy_by_hour:
                        energy_by_hour[hour] = []
                    energy_by_hour[hour].append(level)

                productivity_scores.append(day.get("productivity_score", 0))

                # Track context switching
                projects = day.get("projects_worked_on", {})
                if len(projects) > 0:
                    context_switches.append(len(projects))

            # Identify peak energy times (average energy > 7)
            for hour, levels in energy_by_hour.items():
                avg_energy = sum(levels) / len(levels)
                if avg_energy >= 7.0:
                    patterns["peak_energy_times"].append({
                        "hour": hour,
                        "average_energy": round(avg_energy, 1)
                    })

            # Identify energy dips (average energy < 5)
            for hour, levels in energy_by_hour.items():
                avg_energy = sum(levels) / len(levels)
                if avg_energy < 5.0:
                    patterns["energy_dips"].append({
                        "hour": hour,
                        "average_energy": round(avg_energy, 1)
                    })

            # Context switching impact
            if len(context_switches) >= 3:
                avg_switches = sum(context_switches) / len(context_switches)
                if avg_switches > 5:
                    patterns["context_switching_impact"] = "High - Consider focusing on fewer projects"
                elif avg_switches > 3:
                    patterns["context_switching_impact"] = "Moderate - Manageable but watch for fragmentation"
                else:
                    patterns["context_switching_impact"] = "Low - Good focus on key projects"

            # Weekly trend
            if len(productivity_scores) >= 3:
                recent_avg = sum(productivity_scores[-3:]) / 3
                earlier_avg = sum(productivity_scores[:-3]) / max(1, len(productivity_scores) - 3)

                if recent_avg > earlier_avg + 0.5:
                    patterns["weekly_trend"] = "Improving"
                elif recent_avg < earlier_avg - 0.5:
                    patterns["weekly_trend"] = "Declining"
                else:
                    patterns["weekly_trend"] = "Stable"

            # Best productivity day
            if productivity_scores:
                max_score = max(productivity_scores)
                max_index = productivity_scores.index(max_score)
                patterns["best_productivity_day"] = {
                    "date": daily_history[max_index].get("date"),
                    "score": max_score
                }

            # Consistency score (lower std dev = higher consistency)
            if len(productivity_scores) >= 3:
                mean_score = sum(productivity_scores) / len(productivity_scores)
                variance = sum((x - mean_score) ** 2 for x in productivity_scores) / len(productivity_scores)
                std_dev = variance ** 0.5
                patterns["consistency_score"] = round(max(0, 10 - std_dev), 1)

        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")

        return patterns

    async def map_okr_contribution(
        self,
        work_items: List[Dict[str, Any]],
        okrs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map completed tasks to OKR key results and calculate progress.

        Args:
            work_items: List of completed tasks/accomplishments
            okrs: OKR data structure

        Returns:
            Dictionary mapping work to OKR contributions
        """
        okr_contribution = {
            "objectives_touched": [],
            "key_results_advanced": [],
            "total_progress_percent": 0.0,
            "work_item_mapping": {}
        }

        try:
            if not okrs or not work_items:
                return okr_contribution

            objectives = okrs.get("objectives", [])

            for item in work_items:
                item_text = item.get("description", "").lower()
                item_tags = item.get("tags", [])

                for obj_index, objective in enumerate(objectives):
                    obj_title = objective.get("title", "").lower()
                    key_results = objective.get("key_results", [])

                    # Check if work item relates to this objective
                    for kr_index, kr in enumerate(key_results):
                        kr_description = kr.get("description", "").lower()

                        # Simple keyword matching (can be enhanced with NLP)
                        if any(keyword in item_text for keyword in kr_description.split()[:5]):
                            contribution = {
                                "objective": objective.get("title"),
                                "key_result": kr.get("description"),
                                "work_item": item.get("description"),
                                "estimated_progress": 5.0  # Default 5% progress per item
                            }

                            okr_contribution["key_results_advanced"].append(contribution)

                            if objective.get("title") not in okr_contribution["objectives_touched"]:
                                okr_contribution["objectives_touched"].append(objective.get("title"))

                            # Store mapping
                            okr_contribution["work_item_mapping"][item.get("description")] = {
                                "objective": objective.get("title"),
                                "key_result": kr.get("description")
                            }

            # Calculate total progress percentage
            if okr_contribution["key_results_advanced"]:
                total_estimated = sum(
                    kr.get("estimated_progress", 0)
                    for kr in okr_contribution["key_results_advanced"]
                )
                okr_contribution["total_progress_percent"] = round(total_estimated, 1)

        except Exception as e:
            logger.error(f"Error mapping OKR contribution: {e}")

        return okr_contribution

    async def load_daily_history(self, days: int = 5) -> List[Dict[str, Any]]:
        """
        Load daily analysis history from past N days.

        Args:
            days: Number of days to load

        Returns:
            List of daily analysis data
        """
        history = []

        try:
            for i in range(days):
                date = datetime.now() - timedelta(days=i+1)
                date_str = date.strftime("%Y-%m-%d")
                file_path = self.history_dir / f"{date_str}.json"

                if file_path.exists():
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        history.append(data)

        except Exception as e:
            logger.error(f"Error loading daily history: {e}")

        return history

    async def generate_daily_analysis(
        self,
        session_data: Dict[str, Any],
        okrs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive daily productivity analysis.

        Args:
            session_data: Work session data from evening hook
            okrs: Optional OKR data for contribution mapping

        Returns:
            Complete daily analysis data structure
        """
        try:
            # Load historical data for pattern detection
            daily_history = await self.load_daily_history(days=5)

            # Calculate productivity score
            productivity_score = await self.calculate_productivity_score(session_data)

            # Detect patterns
            patterns = await self.detect_patterns(daily_history)

            # Map OKR contribution
            work_items = session_data.get("accomplishments", [])
            okr_contribution = {}
            if okrs:
                okr_contribution = await self.map_okr_contribution(work_items, okrs)

            # Build analysis structure
            analysis = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat(),
                "productivity_score": productivity_score,
                "hours_worked": session_data.get("hours_worked", 0.0),
                "deep_work_hours": session_data.get("deep_work_hours", 0.0),
                "shallow_work_hours": session_data.get("shallow_work_hours", 0.0),
                "accomplishments": work_items,
                "tools_used": session_data.get("tools_used", {}),
                "projects_worked_on": session_data.get("projects_worked_on", {}),
                "patterns_detected": patterns,
                "blockers": session_data.get("blockers", []),
                "energy_tracking": session_data.get("energy_tracking", {}),
                "focus_quality": session_data.get("focus_quality", {}),
                "okr_contribution": okr_contribution,
                "notes": session_data.get("notes", ""),
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "analyzer_version": "1.0.0"
                }
            }

            # Save to history
            date_str = datetime.now().strftime("%Y-%m-%d")
            output_path = self.history_dir / f"{date_str}.json"

            with open(output_path, 'w') as f:
                json.dump(analysis, f, indent=2)

            logger.info(f"Daily analysis saved to {output_path}")
            logger.info(f"Productivity score: {productivity_score}/10")

            return analysis

        except Exception as e:
            logger.error(f"Error generating daily analysis: {e}")
            raise


async def main():
    """Main entry point for productivity analyzer."""

    # Parse command line arguments
    if len(sys.argv) < 2:
        logger.error("Usage: productivity-analyzer.py <session_data_json>")
        sys.exit(1)

    try:
        # Load session data from argument or stdin
        session_data_str = sys.argv[1]
        session_data = json.loads(session_data_str)

        # Load OKR data if available
        okrs = None
        okr_path = Path("/root/flourisha/00_AI_Brain/context/okrs.json")
        if okr_path.exists():
            with open(okr_path, 'r') as f:
                okrs = json.load(f)

        # Create analyzer and generate analysis
        analyzer = ProductivityAnalyzer()
        analysis = await analyzer.generate_daily_analysis(session_data, okrs)

        # Output summary to stdout
        print(json.dumps({
            "success": True,
            "productivity_score": analysis["productivity_score"],
            "date": analysis["date"],
            "output_path": str(HISTORY_DIR / f"{analysis['date']}.json")
        }, indent=2))

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON input: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
