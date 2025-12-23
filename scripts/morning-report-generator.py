#!/usr/bin/env python3
"""
Morning Report Generator - AI Brain Phase 1
Generates comprehensive morning report with THE ONE THING.

Trigger: Cron job at 7 AM daily
Output: HTML email to gwasmuth@gmail.com
"""

import os
import sys
import json
import asyncio
import logging
import smtplib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
DAILY_ANALYSIS_DIR = AI_BRAIN_ROOT / "history" / "daily-analysis"
PARA_ANALYSIS_DIR = AI_BRAIN_ROOT / "history" / "para-analysis"
CONTEXT_DIR = AI_BRAIN_ROOT / "context"

# Email configuration from environment
GMAIL_USER = os.getenv("GMAIL_USER", "gwasmuth@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "gwasmuth@gmail.com")


class MorningReportGenerator:
    """Generates comprehensive morning productivity reports."""

    def __init__(self):
        """Initialize morning report generator."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.gmail_user = GMAIL_USER
        self.gmail_password = GMAIL_APP_PASSWORD

        if not self.gmail_password:
            logger.warning("GMAIL_APP_PASSWORD not set - email sending will fail")

    async def load_evening_analysis(self) -> Optional[Dict[str, Any]]:
        """
        Load yesterday's productivity analysis.

        Returns:
            Yesterday's analysis data or None
        """
        try:
            yesterday = datetime.now() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")
            file_path = DAILY_ANALYSIS_DIR / f"{date_str}.json"

            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"No evening analysis found for {date_str}")
                return None

        except Exception as e:
            logger.error(f"Error loading evening analysis: {e}")
            return None

    async def load_latest_para_analysis(self) -> Optional[Dict[str, Any]]:
        """
        Load most recent PARA analysis.

        Returns:
            Latest PARA analysis or None
        """
        try:
            # Get all PARA analysis files
            analysis_files = sorted(PARA_ANALYSIS_DIR.glob("*.json"), reverse=True)

            if analysis_files:
                with open(analysis_files[0], 'r') as f:
                    return json.load(f)
            else:
                logger.warning("No PARA analysis found")
                return None

        except Exception as e:
            logger.error(f"Error loading PARA analysis: {e}")
            return None

    async def load_okrs(self) -> Optional[Dict[str, Any]]:
        """
        Load OKR data from context.

        Returns:
            OKR data or None
        """
        try:
            okr_path = CONTEXT_DIR / "okrs.json"

            if okr_path.exists():
                with open(okr_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning("No OKR file found")
                return None

        except Exception as e:
            logger.error(f"Error loading OKRs: {e}")
            return None

    async def determine_one_thing(
        self,
        okrs: Optional[Dict[str, Any]],
        para_analysis: Optional[Dict[str, Any]],
        yesterday_analysis: Optional[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Determine THE ONE THING to focus on today.

        Logic:
        1. OKR progress - which objective is most behind?
        2. Project urgency - any urgent deadlines?
        3. Yesterday's momentum - continue what's working?

        Args:
            okrs: OKR data
            para_analysis: PARA analysis
            yesterday_analysis: Yesterday's productivity data

        Returns:
            Dictionary with one_thing, rationale, objective, project
        """
        one_thing = {
            "task": "Review and prioritize project roadmap",
            "rationale": "No specific data available to determine priority",
            "objective": None,
            "project": None,
            "estimated_impact": "Medium"
        }

        try:
            # Priority 1: Urgent projects from PARA
            if para_analysis:
                urgent_projects = para_analysis.get("summary", {}).get("urgent_projects", [])

                if urgent_projects:
                    project = urgent_projects[0]
                    one_thing["task"] = f"Focus on urgent project: {project}"
                    one_thing["rationale"] = "This project has been flagged as urgent with recent activity"
                    one_thing["project"] = project
                    one_thing["estimated_impact"] = "High"
                    return one_thing

            # Priority 2: OKR progress - find most behind
            if okrs:
                objectives = okrs.get("objectives", [])
                most_behind = None
                min_progress = 100.0

                for obj in objectives:
                    current_progress = obj.get("progress", 0)
                    target_progress = obj.get("target_progress", 25)  # Q1 = 25% of year

                    if current_progress < target_progress and current_progress < min_progress:
                        min_progress = current_progress
                        most_behind = obj

                if most_behind:
                    key_results = most_behind.get("key_results", [])
                    if key_results:
                        kr = key_results[0]
                        one_thing["task"] = f"Advance '{kr.get('description')}'"
                        one_thing["rationale"] = f"This key result is {int(target_progress - min_progress)}% behind Q1 target"
                        one_thing["objective"] = most_behind.get("title")
                        one_thing["estimated_impact"] = "High"
                        return one_thing

            # Priority 3: Continue yesterday's momentum
            if yesterday_analysis:
                accomplishments = yesterday_analysis.get("accomplishments", [])
                productivity_score = yesterday_analysis.get("productivity_score", 0)

                if accomplishments and productivity_score >= 7.0:
                    # Continue the momentum
                    last_project = yesterday_analysis.get("projects_worked_on", {})
                    if last_project:
                        main_project = max(last_project.items(), key=lambda x: x[1])[0]
                        one_thing["task"] = f"Continue momentum on {main_project}"
                        one_thing["rationale"] = f"Yesterday's productivity was strong ({productivity_score}/10) - maintain focus"
                        one_thing["project"] = main_project
                        one_thing["estimated_impact"] = "Medium"
                        return one_thing

        except Exception as e:
            logger.error(f"Error determining one thing: {e}")

        return one_thing

    async def generate_html_report(
        self,
        one_thing: Dict[str, str],
        yesterday_analysis: Optional[Dict[str, Any]],
        para_analysis: Optional[Dict[str, Any]],
        okrs: Optional[Dict[str, Any]]
    ) -> str:
        """
        Generate HTML email report.

        Args:
            one_thing: THE ONE THING to focus on
            yesterday_analysis: Yesterday's productivity data
            para_analysis: Latest PARA analysis
            okrs: OKR data

        Returns:
            HTML string
        """
        today = datetime.now().strftime("%A, %B %d, %Y")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                }}
                .one-thing {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 8px;
                    margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                }}
                .one-thing h2 {{
                    color: white;
                    margin-top: 0;
                    font-size: 24px;
                }}
                .one-thing .task {{
                    font-size: 20px;
                    font-weight: 600;
                    margin: 10px 0;
                }}
                .one-thing .rationale {{
                    font-size: 14px;
                    opacity: 0.9;
                    margin-top: 10px;
                }}
                .section {{
                    margin: 25px 0;
                    padding: 20px;
                    background: #f8f9fa;
                    border-left: 4px solid #3498db;
                    border-radius: 4px;
                }}
                .score {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #27ae60;
                }}
                .score.low {{ color: #e74c3c; }}
                .score.medium {{ color: #f39c12; }}
                .priority-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                    margin-right: 10px;
                }}
                .urgent {{ background: #e74c3c; color: white; }}
                .high {{ background: #f39c12; color: white; }}
                .normal {{ background: #3498db; color: white; }}
                .low {{ background: #95a5a6; color: white; }}
                .accomplishment {{
                    padding: 8px 12px;
                    margin: 5px 0;
                    background: white;
                    border-left: 3px solid #27ae60;
                    border-radius: 3px;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #7f8c8d;
                    font-size: 12px;
                    text-align: center;
                }}
                ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                li {{
                    margin: 8px 0;
                    padding-left: 20px;
                    position: relative;
                }}
                li:before {{
                    content: "•";
                    position: absolute;
                    left: 0;
                    color: #3498db;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌅 Good Morning, Greg!</h1>
                <p style="color: #7f8c8d; font-size: 14px;">{today}</p>

                <!-- THE ONE THING -->
                <div class="one-thing">
                    <h2>🎯 THE ONE THING</h2>
                    <div class="task">{one_thing['task']}</div>
                    <div class="rationale">{one_thing['rationale']}</div>
                    {f'<div style="margin-top: 15px; font-size: 13px;">📊 Estimated Impact: {one_thing["estimated_impact"]}</div>' if one_thing.get('estimated_impact') else ''}
                </div>
        """

        # Yesterday Recap
        if yesterday_analysis:
            score = yesterday_analysis.get("productivity_score", 0)
            score_class = "low" if score < 6 else ("medium" if score < 8 else "")

            html += f"""
                <div class="section">
                    <h2>📊 Yesterday's Recap</h2>
                    <p><span class="score {score_class}">{score}/10</span> Productivity Score</p>
                    <p><strong>Hours Worked:</strong> {yesterday_analysis.get('hours_worked', 0):.1f} hrs
                       (Deep: {yesterday_analysis.get('deep_work_hours', 0):.1f} hrs)</p>
            """

            accomplishments = yesterday_analysis.get("accomplishments", [])
            if accomplishments:
                html += "<h3>✅ Accomplishments</h3>"
                for acc in accomplishments[:5]:
                    desc = acc.get("description", acc) if isinstance(acc, dict) else acc
                    html += f'<div class="accomplishment">{desc}</div>'

            blockers = yesterday_analysis.get("blockers", [])
            if blockers:
                html += "<h3>🚧 Blockers</h3><ul>"
                for blocker in blockers[:3]:
                    html += f"<li>{blocker}</li>"
                html += "</ul>"

            html += "</div>"

        # Today's Plan
        html += """
            <div class="section">
                <h2>📅 Today's Plan</h2>
                <h3>Tier 1 - Must Do</h3>
                <ul>
                    <li>THE ONE THING (see above)</li>
        """

        if para_analysis:
            urgent = para_analysis.get("summary", {}).get("urgent_projects", [])
            for project in urgent[:2]:
                html += f"<li>Progress on {project}</li>"

        html += """
                </ul>
                <h3>Tier 2 - Should Do</h3>
                <ul>
                    <li>Review and respond to critical emails</li>
                    <li>Update project documentation</li>
                </ul>
                <h3>Tier 3 - Nice to Have</h3>
                <ul>
                    <li>Knowledge base review</li>
                    <li>Long-term planning</li>
                </ul>
            </div>
        """

        # OKR Progress
        if okrs:
            html += '<div class="section"><h2>🎯 OKR Progress (Q1 2026)</h2>'

            objectives = okrs.get("objectives", [])
            for obj in objectives[:4]:
                title = obj.get("title", "Untitled")
                progress = obj.get("progress", 0)
                target = obj.get("target_progress", 25)

                html += f"""
                    <div style="margin: 15px 0;">
                        <strong>{title}</strong>
                        <div style="background: #ecf0f1; height: 20px; border-radius: 10px; margin: 5px 0;">
                            <div style="background: #3498db; width: {min(100, progress)}%; height: 100%; border-radius: 10px;"></div>
                        </div>
                        <span style="font-size: 12px; color: #7f8c8d;">{progress}% complete (Target: {target}%)</span>
                    </div>
                """

            html += "</div>"

        # PARA Updates
        if para_analysis:
            html += '<div class="section"><h2>📁 PARA Updates</h2>'

            summary = para_analysis.get("summary", {})
            total_changes = summary.get("total_changes", 0)
            active_projects = summary.get("active_projects", 0)

            html += f"""
                <p><strong>{total_changes}</strong> files changed since last scan</p>
                <p><strong>{active_projects}</strong> active projects</p>
            """

            project_activity = para_analysis.get("project_activity", {})
            if project_activity:
                html += "<h3>Active Projects</h3>"
                for name, data in list(project_activity.items())[:5]:
                    priority = data.get("priority", {}).get("priority_level", "Normal")
                    badge_class = priority.lower()
                    html += f'<div style="margin: 8px 0;"><span class="priority-badge {badge_class}">{priority}</span>{name}</div>'

            html += "</div>"

        # Energy Forecast
        if yesterday_analysis:
            patterns = yesterday_analysis.get("patterns_detected", {})
            peak_times = patterns.get("peak_energy_times", [])

            if peak_times:
                html += '<div class="section"><h2>⚡ Energy Forecast</h2>'
                html += '<p>Based on your patterns, peak energy times today:</p><ul>'

                for peak in peak_times[:3]:
                    hour = peak.get("hour", 0)
                    time_str = f"{hour:02d}:00"
                    html += f"<li>{time_str} (Energy: {peak.get('average_energy', 0)}/10)</li>"

                html += "</ul></div>"

        # Footer
        html += """
                <div class="footer">
                    Generated by Flourisha AI Brain | Phase 1<br>
                    Have a productive day! 🚀
                </div>
            </div>
        </body>
        </html>
        """

        return html

    async def send_email(self, html_content: str) -> bool:
        """
        Send HTML email via Gmail SMTP.

        Args:
            html_content: HTML email content

        Returns:
            True if sent successfully
        """
        try:
            if not self.gmail_password:
                logger.error("Gmail app password not configured")
                return False

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🌅 Morning Report - {datetime.now().strftime('%A, %B %d')}"
            msg['From'] = self.gmail_user
            msg['To'] = RECIPIENT_EMAIL

            # Attach HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send via SMTP
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(self.gmail_user, self.gmail_password)
                server.send_message(msg)

            logger.info(f"Morning report sent to {RECIPIENT_EMAIL}")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    async def send_alert_email(self, error_msg: str) -> None:
        """
        Send alert email if report generation fails.

        Args:
            error_msg: Error message to include
        """
        try:
            simple_html = f"""
            <html>
            <body>
                <h2>⚠️ Morning Report Generation Failed</h2>
                <p>The morning report could not be generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Error:</strong> {error_msg}</p>
                <p>Please check the AI Brain logs for details.</p>
            </body>
            </html>
            """

            msg = MIMEMultipart('alternative')
            msg['Subject'] = "⚠️ Morning Report Error"
            msg['From'] = self.gmail_user
            msg['To'] = RECIPIENT_EMAIL

            msg.attach(MIMEText(simple_html, 'html'))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(self.gmail_user, self.gmail_password)
                server.send_message(msg)

            logger.info("Alert email sent")

        except Exception as e:
            logger.error(f"Could not send alert email: {e}")

    async def generate_morning_report(self) -> bool:
        """
        Main orchestration function for morning report generation.

        Returns:
            True if successful
        """
        try:
            logger.info("Starting morning report generation...")

            # Load all data sources
            yesterday_analysis = await self.load_evening_analysis()
            para_analysis = await self.load_latest_para_analysis()
            okrs = await self.load_okrs()

            # Determine THE ONE THING
            one_thing = await self.determine_one_thing(
                okrs,
                para_analysis,
                yesterday_analysis
            )

            logger.info(f"THE ONE THING: {one_thing['task']}")

            # Generate HTML report
            html_content = await self.generate_html_report(
                one_thing,
                yesterday_analysis,
                para_analysis,
                okrs
            )

            # Send email
            success = await self.send_email(html_content)

            if success:
                logger.info("Morning report generation completed successfully")
            else:
                logger.error("Failed to send morning report email")

            return success

        except Exception as e:
            logger.error(f"Error generating morning report: {e}")
            await self.send_alert_email(str(e))
            return False


async def main():
    """Main entry point."""
    try:
        generator = MorningReportGenerator()
        success = await generator.generate_morning_report()

        if success:
            print(json.dumps({
                "success": True,
                "message": "Morning report sent successfully",
                "timestamp": datetime.now().isoformat()
            }, indent=2))
            sys.exit(0)
        else:
            print(json.dumps({
                "success": False,
                "message": "Failed to send morning report",
                "timestamp": datetime.now().isoformat()
            }, indent=2))
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(json.dumps({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
