"""
Emailer Module
Sends email reminders via Gmail SMTP
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional


class Emailer:
    def __init__(self, 
                 sender_email: Optional[str] = None,
                 sender_password: Optional[str] = None,
                 smtp_server: str = "smtp.gmail.com",
                 smtp_port: int = 587):
        """
        Initialize Emailer with Gmail SMTP credentials
        
        Args:
            sender_email: Gmail address (or from env GMAIL_ADDRESS)
            sender_password: Gmail app password (or from env GMAIL_PASSWORD)
            smtp_server: SMTP server address
            smtp_port: SMTP port
        """
        self.sender_email = sender_email or os.getenv('GMAIL_ADDRESS')
        self.sender_password = sender_password or os.getenv('GMAIL_PASSWORD')
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.enabled = bool(self.sender_email and self.sender_password)
        
        if not self.enabled:
            print("Warning: Email credentials not configured. Email notifications disabled.")
    
    def send_email(self, 
                   recipient: str,
                   subject: str,
                   body: str,
                   html: bool = True) -> bool:
        """
        Send an email
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            body: Email body content
            html: If True, body is HTML; otherwise plain text
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            print(f"[EMAIL] Would send to {recipient}: {subject}")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Attach body
            mime_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_task_reminder(self, 
                          recipient: str,
                          task: Dict,
                          note_context: str = "") -> bool:
        """
        Send a task reminder email
        
        Args:
            recipient: Recipient email address
            task: Task dictionary
            note_context: Original note context
        
        Returns:
            True if successful, False otherwise
        """
        subject = f"⏰ Task Reminder: {task['title']}"
        
        # Create HTML email
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background-color: #4CAF50; color: white; padding: 20px; }}
                    .content {{ padding: 20px; }}
                    .task-box {{ 
                        border-left: 4px solid {task.get('color', 'orange')};
                        padding: 15px;
                        margin: 20px 0;
                        background-color: #f9f9f9;
                    }}
                    .priority-high {{ color: #d32f2f; font-weight: bold; }}
                    .priority-medium {{ color: #f57c00; font-weight: bold; }}
                    .priority-low {{ color: #388e3c; font-weight: bold; }}
                    .footer {{ font-size: 12px; color: #666; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>📝 ActionNote Task Reminder</h2>
                </div>
                <div class="content">
                    <p>You have a task that needs attention:</p>
                    
                    <div class="task-box">
                        <h3>{task['title']}</h3>
                        <p><strong>Priority:</strong> 
                            <span class="priority-{task['priority'].lower()}">{task['priority']}</span>
                        </p>
                        <p><strong>Status:</strong> {task['status']}</p>
                        <p><strong>Deadline:</strong> {task.get('deadline', 'Not set')}</p>
                        <p><strong>Last Updated:</strong> {task.get('last_update', 'Unknown')}</p>
                    </div>
                    
                    {f'<div style="margin: 20px 0;"><strong>Original Note:</strong><p>{note_context}</p></div>' if note_context else ''}
                    
                    <p>Don't forget to update the task status in your ActionNote dashboard!</p>
                    
                    <div class="footer">
                        <p>This is an automated reminder from ActionNote.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(recipient, subject, html_body, html=True)
    
    def send_daily_summary(self, 
                          recipient: str,
                          tasks: List[Dict]) -> bool:
        """
        Send a daily summary of all pending tasks
        
        Args:
            recipient: Recipient email address
            tasks: List of tasks
        
        Returns:
            True if successful, False otherwise
        """
        if not tasks:
            return False
        
        subject = f"📊 Daily Task Summary - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Group tasks by priority
        high_tasks = [t for t in tasks if t['priority'] == 'High']
        medium_tasks = [t for t in tasks if t['priority'] == 'Medium']
        low_tasks = [t for t in tasks if t['priority'] == 'Low']
        
        def task_list_html(task_list):
            if not task_list:
                return "<p>None</p>"
            html = "<ul>"
            for task in task_list:
                html += f"<li><strong>{task['title']}</strong> - {task['status']}</li>"
            html += "</ul>"
            return html
        
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background-color: #2196F3; color: white; padding: 20px; }}
                    .content {{ padding: 20px; }}
                    .section {{ margin: 20px 0; }}
                    .high {{ color: #d32f2f; }}
                    .medium {{ color: #f57c00; }}
                    .low {{ color: #388e3c; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>📊 Daily Task Summary</h2>
                    <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
                </div>
                <div class="content">
                    <p>Total Tasks: {len(tasks)}</p>
                    
                    <div class="section">
                        <h3 class="high">🔴 High Priority ({len(high_tasks)})</h3>
                        {task_list_html(high_tasks)}
                    </div>
                    
                    <div class="section">
                        <h3 class="medium">🟠 Medium Priority ({len(medium_tasks)})</h3>
                        {task_list_html(medium_tasks)}
                    </div>
                    
                    <div class="section">
                        <h3 class="low">🟢 Low Priority ({len(low_tasks)})</h3>
                        {task_list_html(low_tasks)}
                    </div>
                </div>
            </body>
        </html>
        """
        
        return self.send_email(recipient, subject, html_body, html=True)
