#!/usr/bin/env python3
"""
Module 06: Email - Notification Delivery
Sends email notifications via Gmail SMTP.
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class EmailResult:
    """Result of sending an email."""
    success: bool
    message: str
    recipients: List[str]

class EmailSender:
    """Sends email notifications via Gmail SMTP."""
    
    def __init__(self, smtp_email: str, smtp_password: str):
        self.smtp_email = smtp_email
        self.smtp_password = smtp_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_tender_alert(
        self, 
        to_email: str, 
        matched_tenders: List[dict],
        customer_name: str = "Customer"
    ) -> EmailResult:
        """Send tender alert email to customer."""
        
        if not matched_tenders:
            return EmailResult(success=False, message="No tenders to send", recipients=[])
        
        try:
            # Build email content
            subject = f"🔔 {len(matched_tenders)} nya upphandlingar som matchar din profil"
            
            html_body = self._build_html_email(matched_tenders, customer_name)
            text_body = self._build_text_email(matched_tenders, customer_name)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_email
            msg['To'] = to_email
            
            # Attach both plain and HTML versions
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)
            
            return EmailResult(
                success=True,
                message=f"Sent {len(matched_tenders)} tenders to {to_email}",
                recipients=[to_email]
            )
            
        except smtplib.SMTPAuthenticationError:
            return EmailResult(success=False, message="Authentication failed - check SMTP credentials", recipients=[])
        except Exception as e:
            return EmailResult(success=False, message=f"SMTP error: {str(e)}", recipients=[])
    
    def _build_html_email(self, tenders: List[dict], customer_name: str) -> str:
        """Build HTML email body with tender list."""
        
        tender_rows = ""
        for i, t in enumerate(tenders[:10], 1):  # Max 10 tenders per email
            title = t.get('tender_title', 'Unknown')[:80]
            url = t.get('tender_url', '')
            score = t.get('relevance_score', 0)
            score_pct = int(score * 100)
            reasons = t.get('match_reasons', [])
            reasons_str = ', '.join(reasons[:2]) if reasons else 'Relevans'
            
            tender_rows += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">
                    <strong>{i}.</strong>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">
                    <a href="{url}" style="color: #1a73e8; text-decoration: none;">
                        {title}
                    </a>
                    <br><small style="color: #666;">{reasons_str}</small>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">
                    <span style="background: #e8f5e9; color: #2e7d32; padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                        {score_pct}% match
                    </span>
                </td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1a73e8; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #f5f5f5; padding: 12px; text-align: left; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Nya upphandlingar</h1>
                    <p>Hej {customer_name}!</p>
                </div>
                <div class="content">
                    <p>Vi har hittat <strong>{len(tenders)}</strong> upphandlingar som matchar din profil:</p>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Upphandling</th>
                                <th>Match</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tender_rows}
                        </tbody>
                    </table>
                    
                    <p style="text-align: center; margin-top: 20px;">
                        <a href="https://stackgrade.github.io/tender-system" style="background: #1a73e8; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">
                            Visa alla på TendAlert
                        </a>
                    </p>
                </div>
                <div class="footer">
                    <p>Du får det här mejlet eftersom du prenumererar på TendAlert.</p>
                    <p>© 2026 TendAlert - Svårare att missa en upphandling</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _build_text_email(self, tenders: List[dict], customer_name: str) -> str:
        """Build plain text email body."""
        
        lines = [
            f"Nya upphandlingar - {len(tenders)} matchar din profil",
            "",
            f"Hej {customer_name}!",
            "",
            "Vi har hittat följande upphandlingar:",
            "",
        ]
        
        for i, t in enumerate(tenders[:10], 1):
            title = t.get('tender_title', 'Unknown')[:70]
            url = t.get('tender_url', '')
            score_pct = int(t.get('relevance_score', 0) * 100)
            lines.append(f"{i}. {title}")
            lines.append(f"   Match: {score_pct}%")
            lines.append(f"   Länk: {url}")
            lines.append("")
        
        lines.extend([
            "---",
            "TendAlert - Svårare att missa en upphandling",
            "https://stackgrade.github.io/tender-system"
        ])
        
        return "\n".join(lines)


def main():
    """Test email sending (requires SMTP credentials)."""
    
    # Load matched tenders
    try:
        with open("/home/larry/projects/tender-system/data/matched_tenders.json") as f:
            tenders = json.load(f)
    except:
        print("❌ No matched tenders found - run filter first")
        return None
    
    # Email settings from config
    from config import SMTP_EMAIL, SMTP_PASSWORD
    
    sender = EmailSender(SMTP_EMAIL, SMTP_PASSWORD)
    
    # Test send
    test_email = "test@example.com"  # Replace with actual email
    result = sender.send_tender_alert(
        to_email=test_email,
        matched_tenders=tenders,
        customer_name="Alex"
    )
    
    print(f"Email result: {result.message}")
    return result

if __name__ == "__main__":
    main()