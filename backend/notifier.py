import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List
from internship import Internship
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Notifier:
    """
    Handles proactive notifications for the user.
    """
    def __init__(self, email: str, telegram_token: str = None, telegram_chat_id: str = None):
        self.email = email
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.drafts_dir = os.path.join(os.path.dirname(__file__), "drafts")
        if not os.path.exists(self.drafts_dir):
            os.makedirs(self.drafts_dir)

        # SMTP Config
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_user = os.getenv("EMAIL_USER")
        self.smtp_pass = os.getenv("EMAIL_PASS")

    def draft_internship_summary(self, internships: List[Internship]):
        """
        Creates a formatted email summary and sends it.
        """
        if not internships:
            print("No high-match internships to notify about.")
            return

        # Prepare email content
        subject = f"Agent Reply: Internship Opportunities Found! ({datetime.now().strftime('%Y-%m-%d')})"
        body = "Hello,\n\nI've found some internship opportunities based on your recent request:\n\n"
        
        for job in internships:
            body += f"--- {job.role_title} at {job.company_name} ---\n"
            body += f"Match: {job.match_score}%\n"
            body += f"Location: {job.location}\n"
            body += f"Why it fits: {job.match_reasoning}\n"
            body += f"Direct Apply: {job.application_link}\n\n"

        body += "Happy Job Hunting!\nYour Internship Discovery Agent"

        # 1. Draft to local file (legacy support/backup)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"internship_summary_{timestamp}.txt"
        filepath = os.path.join(self.drafts_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"To: {self.email}\n")
            f.write(f"Subject: {subject}\n\n")
            f.write(body)
        print(f"Notification drafted to: {filepath}")

        # 2. Send via Email if configured
        if self.smtp_user and self.smtp_pass:
            self.send_email(self.email, subject, body)
        else:
            print("Warning: Email credentials not set in .env. Skipping real email.")

        # 3. Auto-send telegram if configured
        if self.telegram_token and self.telegram_chat_id:
            self.send_telegram_summary(internships)
            
        return filepath

    def send_email(self, recipient: str, subject: str, body: str):
        """Sends a real email using SMTP."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
            server.quit()
            print(f"Email sent successfully to {recipient}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def send_telegram_summary(self, internships: List[Internship]):
        """Sends the summary directly to Telegram."""
        if not self.telegram_token or not self.telegram_chat_id:
            return

        message = "<b>🚀 New Internship Opportunities Found!</b>\n\n"
        for job in internships:
            message += f"<b>{job.role_title}</b> at {job.company_name}\n"
            message += f"🎯 Match: {job.match_score}%\n"
            message += f"📍 Location: {job.location}\n"
            message += f"🔗 <a href='{job.application_link}'>Apply Here</a>\n\n"

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print("Telegram notification sent successfully!")
            else:
                print(f"Failed to send Telegram: {response.text}")
        except Exception as e:
            print(f"Error sending Telegram: {e}")
