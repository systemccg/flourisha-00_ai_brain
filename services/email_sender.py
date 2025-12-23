"""
Email Sender Service
Gmail SMTP integration for sending morning reports and notifications
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv('/root/.claude/.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailSenderService:
    """
    Email sender service using Gmail SMTP
    Implements singleton pattern for connection reuse
    """

    _instance: Optional['EmailSenderService'] = None
    _initialized: bool = False

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize email sender"""
        if not self._initialized:
            self.gmail_user = os.getenv('GMAIL_USER', 'gwasmuth@gmail.com')
            self.gmail_password = os.getenv('GMAIL_APP_PASSWORD')

            if not self.gmail_password:
                logger.warning("GMAIL_APP_PASSWORD not set - email sending will fail")

            self.smtp_server = 'smtp.gmail.com'
            self.smtp_port = 587

            self._initialized = True
            logger.info(f"Email sender initialized for {self.gmail_user}")

    def send_html_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> bool:
        """
        Send HTML email via Gmail SMTP

        Args:
            to: Recipient email address
            subject: Email subject line
            html_body: HTML formatted email body
            cc: Optional CC email address
            bcc: Optional BCC email address

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            if not self.gmail_password:
                logger.error("Cannot send email: GMAIL_APP_PASSWORD not configured")
                return False

            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = self.gmail_user
            message['To'] = to
            message['Subject'] = subject

            if cc:
                message['Cc'] = cc
            if bcc:
                message['Bcc'] = bcc

            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)

            # Connect to Gmail SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Upgrade to secure connection
                server.login(self.gmail_user, self.gmail_password)

                # Send email
                recipients = [to]
                if cc:
                    recipients.append(cc)
                if bcc:
                    recipients.append(bcc)

                server.sendmail(self.gmail_user, recipients, message.as_string())

            logger.info(f"Email sent successfully to {to}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def send_morning_report(self, report_dict: Dict[str, Any]) -> bool:
        """
        Send formatted morning report email

        Args:
            report_dict: Morning report data with structure:
                {
                    'date': str,
                    'one_thing': {
                        'project': str,
                        'task': str,
                        'why': str,
                        'okr_contribution': str
                    },
                    'okr_summary': {...},
                    'focus_areas': [...],
                    'calendar': {...},
                    'productivity_score': float
                }

        Returns:
            bool: True if sent successfully
        """
        try:
            # Extract data
            date_str = report_dict.get('date', datetime.now().strftime('%Y-%m-%d'))
            one_thing = report_dict.get('one_thing', {})
            okr_summary = report_dict.get('okr_summary', {})
            focus_areas = report_dict.get('focus_areas', [])
            calendar = report_dict.get('calendar', {})
            productivity_score = report_dict.get('productivity_score', 0)

            # Format date nicely
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%A, %B %d, %Y')
            except:
                formatted_date = date_str

            # Generate HTML
            html_body = self._generate_morning_report_html(
                date=formatted_date,
                one_thing=one_thing,
                okr_summary=okr_summary,
                focus_areas=focus_areas,
                calendar=calendar,
                productivity_score=productivity_score
            )

            # Send email
            subject = f"Good morning, Greg! ☀️ {formatted_date}"
            return self.send_html_email(
                to=self.gmail_user,  # Send to self
                subject=subject,
                html_body=html_body
            )

        except Exception as e:
            logger.error(f"Error sending morning report: {e}")
            return False

    def _generate_morning_report_html(
        self,
        date: str,
        one_thing: Dict,
        okr_summary: Dict,
        focus_areas: list,
        calendar: Dict,
        productivity_score: float
    ) -> str:
        """Generate HTML for morning report email"""

        # Extract one thing details
        ot_project = one_thing.get('project', 'Not set')
        ot_task = one_thing.get('task', 'Not set')
        ot_why = one_thing.get('why', '')
        ot_okr = one_thing.get('okr_contribution', '')

        # Build HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            color: #2c3e50;
            font-size: 28px;
        }}
        .header .date {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .one-thing {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .one-thing h2 {{
            margin-top: 0;
            font-size: 22px;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 10px;
        }}
        .one-thing .project {{
            font-size: 20px;
            font-weight: bold;
            margin: 15px 0;
        }}
        .one-thing .task {{
            font-size: 16px;
            background: rgba(255,255,255,0.2);
            padding: 12px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        .one-thing .why {{
            font-style: italic;
            opacity: 0.9;
            margin-top: 10px;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section h3 {{
            color: #2c3e50;
            border-left: 4px solid #4CAF50;
            padding-left: 12px;
            margin-bottom: 15px;
        }}
        .okr-item {{
            background: #f8f9fa;
            padding: 12px;
            margin: 8px 0;
            border-radius: 4px;
            border-left: 3px solid #4CAF50;
        }}
        .progress-bar {{
            background: #e0e0e0;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 8px;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #4CAF50 0%, #45a049 100%);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}
        .focus-item {{
            padding: 10px;
            margin: 8px 0;
            background: #fff9e6;
            border-left: 3px solid #ffc107;
            border-radius: 4px;
        }}
        .calendar-event {{
            padding: 10px;
            margin: 8px 0;
            background: #e3f2fd;
            border-left: 3px solid #2196F3;
            border-radius: 4px;
        }}
        .score {{
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            color: #4CAF50;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Good Morning, Greg! ☀️</h1>
            <div class="date">{date}</div>
        </div>

        <div class="one-thing">
            <h2>🎯 THE ONE THING</h2>
            <div class="project">📁 {ot_project}</div>
            <div class="task">✅ {ot_task}</div>
            <div class="why">💡 {ot_why}</div>
            {f'<div style="margin-top: 15px; opacity: 0.8;">🎯 OKR Impact: {ot_okr}</div>' if ot_okr else ''}
        </div>

        <div class="section">
            <h3>📊 OKR Progress</h3>
"""

        # Add OKR items
        avg_progress = okr_summary.get('average_progress', 0)
        on_track = okr_summary.get('on_track', 0)
        total_objs = okr_summary.get('total_objectives', 4)

        html += f"""
            <div class="okr-item">
                <div>Overall Progress: {avg_progress:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {avg_progress}%;">{avg_progress:.0f}%</div>
                </div>
            </div>
            <div class="okr-item">
                On Track: {on_track}/{total_objs} objectives
            </div>
"""

        html += """
        </div>

        <div class="section">
            <h3>🔥 Focus Areas Today</h3>
"""

        # Add focus areas
        if focus_areas:
            for item in focus_areas[:3]:
                if isinstance(item, dict):
                    title = item.get('kr_title', item.get('title', 'Focus item'))
                else:
                    title = str(item)
                html += f'<div class="focus-item">{title}</div>\n'
        else:
            html += '<div class="focus-item">Maintain current momentum</div>\n'

        html += """
        </div>
"""

        # Add calendar if present
        if calendar and calendar.get('events'):
            html += """
        <div class="section">
            <h3>📅 Today's Calendar</h3>
"""
            for event in calendar['events'][:5]:
                event_title = event.get('title', 'Event')
                event_time = event.get('time', '')
                html += f'<div class="calendar-event"><strong>{event_time}</strong> {event_title}</div>\n'

            html += """
        </div>
"""

        # Add productivity score if present
        if productivity_score > 0:
            html += f"""
        <div class="section">
            <h3>⭐ Yesterday's Productivity</h3>
            <div class="score">{productivity_score:.1f}/10</div>
        </div>
"""

        html += """
        <div class="footer">
            Generated by Flourisha AI Brain 🤖<br>
            Have a productive day!
        </div>
    </div>
</body>
</html>
"""

        return html


# Singleton instance
email_sender = EmailSenderService()
