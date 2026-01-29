import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from typing import List, Dict

class Notifier:
    def __init__(self, template_dir: str = "templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL", self.smtp_user)
        # Support multiple receivers comma separated
        receivers = os.getenv("RECEIVER_EMAIL", "")
        self.receiver_emails = [email.strip() for email in receivers.split(",") if email.strip()]

    def render_report(self, projects: List[Dict]) -> str:
        """
        Renders the HTML report using Jinja2 template.
        """
        template = self.env.get_template("email_template.html")
        date_str = datetime.now().strftime("%Y-%m-%d %A")
        return template.render(projects=projects, date=date_str)

    def send_email(self, html_content: str):
        """
        Sends the HTML report via SMTP.
        """
        if not self.smtp_user or not self.smtp_password or not self.receiver_emails:
            print("SMTP credentials or receiver email not set. Skipping email send.")
            # For local testing, maybe save to file?
            with open("latest_report.html", "w") as f:
                f.write(html_content)
            print("Saved report to latest_report.html")
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"GitHub Trending AI Daily - {datetime.now().strftime('%Y-%m-%d')}"
        msg["From"] = self.sender_email
        msg["To"] = ", ".join(self.receiver_emails)

        part = MIMEText(html_content, "html")
        msg.attach(part)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender_email, self.receiver_emails, msg.as_string())
            print(f"Email sent successfully to {len(self.receiver_emails)} recipients.")
        except Exception as e:
            print(f"Error sending email: {e}")
            print("Attempting to save report locally due to email failure...")
            try:
                with open("latest_report.html", "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("Successfully saved report to 'latest_report.html'")
            except Exception as write_error:
                print(f"Failed to save local report: {write_error}")

if __name__ == "__main__":
    # Test execution
    from dotenv import load_dotenv
    load_dotenv()
    
    mock_projects = [
        {
            "name": "Test Project",
            "url": "https://github.com/test/test",
            "stars": 1200,
            "stars_today": 150,
            "language": "Python",
            "analysis": {
                "one_sentence_summary": "这是一个测试项目。",
                "core_features": ["功能一", "功能二", "功能三"],
                "tech_stack": ["Python", "Django"],
                "use_case": "测试",
                "score": 5
            }
        }
    ]
    
    notifier = Notifier()
    html = notifier.render_report(mock_projects)
    notifier.send_email(html)
