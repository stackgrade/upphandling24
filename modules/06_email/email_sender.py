#!/usr/bin/env python3
"""
Module 06: Email Sender - PRODUCTION
Sends tender alert emails via Gmail SMTP.
Includes DEMO mode when credentials are not configured.
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class EmailResult:
    """Result of sending an email."""
    success: bool
    message: str
    recipients: List[str]
    demo_mode: bool = False

class EmailSender:
    """Sends email notifications via Gmail SMTP."""
    
    def __init__(self, smtp_email: Optional[str] = None, smtp_password: Optional[str] = None):
        self.smtp_email = smtp_email
        self.smtp_password = smtp_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.is_demo = not (smtp_email and smtp_password)
        
        if self.is_demo:
            print("📧 EmailSender: DEMO MODE (no SMTP credentials)")
    
    def send_tender_alert(
        self, 
        to_email: str, 
        matched_tenders: List[dict],
        customer_name: str = "Kund"
    ) -> EmailResult:
        """Send tender alert email to customer."""
        
        if not matched_tenders:
            return EmailResult(success=False, message="Inga tendrar att skicka", recipients=[])
        
        # DEMO MODE - save email to file instead of sending
        if self.is_demo:
            return self._demo_send(to_email, matched_tenders, customer_name)
        
        # REAL MODE - send via SMTP
        try:
            subject = f"🔔 {len(matched_tenders)} nya upphandlingar som matchar din profil"
            
            html_body = self._build_html_email(matched_tenders, customer_name)
            text_body = self._build_text_email(matched_tenders, customer_name)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_email
            msg['To'] = to_email
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)
            
            return EmailResult(
                success=True,
                message=f"Skickat {len(matched_tenders)} tendrar till {to_email}",
                recipients=[to_email]
            )
            
        except smtplib.SMTPAuthenticationError:
            return EmailResult(success=False, message="Authentication failed - kolla SMTP credentials", recipients=[])
        except Exception as e:
            return EmailResult(success=False, message=f"SMTP error: {str(e)}", recipients=[])
    
    def _demo_send(self, to_email: str, tenders: List[dict], name: str) -> EmailResult:
        """DEMO MODE: Save email as HTML file instead of sending."""
        
        html = self._build_html_email(tenders, name)
        
        # Save to demo folder
        demo_dir = "/home/larry/projects/tender-system/data/demo_emails"
        import os
        os.makedirs(demo_dir, exist_ok=True)
        
        filename = f"{demo_dir}/alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name.replace(' ', '_')}.html"
        with open(filename, 'w') as f:
            f.write(html)
        
        print(f"📧 DEMO EMAIL SPARAD: {filename}")
        print(f"   → {len(tenders)} tendrar för {name}")
        print(f"   → Visar hur emailen kommer se ut")
        
        return EmailResult(
            success=True,
            message=f"DEMO: Email saved ({len(tenders)} tendrar för {name})",
            recipients=[to_email],
            demo_mode=True
        )
    
    def _build_html_email(self, tenders: List[dict], customer_name: str) -> str:
        """Build HTML email body."""
        
        tender_rows = ""
        for i, t in enumerate(tenders[:10], 1):
            title = t.get('tender_title', 'Unknown')[:80]
            url = t.get('tender_url', '#')
            score = t.get('relevance_score', 0.5)
            score_pct = int(score * 100)
            reasons = t.get('match_reasons', [])
            reasons_str = ', '.join(reasons[:2]) if reasons else 'Relevans'
            
            # Color based on score
            if score >= 0.7:
                color = "#2e7d32"  # Green
                bg = "#e8f5e9"
            elif score >= 0.5:
                color = "#f57c00"  # Orange
                bg = "#fff3e0"
            else:
                color = "#666"  # Gray
                bg = "#f5f5f5"
            
            tender_rows += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">{i}</td>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">
                    <a href="{url}" style="color: #1a73e8; text-decoration: none;">{title}</a>
                    <br><small style="color: #666;">{reasons_str}</small>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: center;">
                    <span style="background: {bg}; color: {color}; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                        {score_pct}%
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
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1a73e8, #0d47a1); color: white; padding: 30px 20px; text-align: center; border-radius: 12px 12px 0 0; }}
        .header h1 {{ margin: 0; font-size: 24px; }} 
        .header p {{ margin: 10px 0 0; opacity: 0.9; }}
        .content {{ background: #f9f9f9; padding: 20px; }}
        .intro {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th {{ background: #f5f5f5; padding: 12px; text-align: left; font-size: 12px; text-transform: uppercase; color: #666; }}
        th:last-child {{ text-align: center; }}
        .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; }}
        .cta {{ text-align: center; margin-top: 20px; }}
        .cta a {{ background: #1a73e8; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; }}
        .badge {{ background: #1a73e8; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; text-transform: uppercase; }}
    </style>
</head>
<body>
    <div class="header">
        <span class="badge">TendAlert</span>
        <h1>Nya upphandlingar</h1>
        <p>Hej {customer_name}! Vi har hittat {len(tenders)} upphandlingar som matchar din profil.</p>
    </div>
    <div class="content">
        <div class="intro">
            <p style="margin: 0;"><strong>Din sammanfattning:</strong> {len(tenders)} matchande upphandlingar varav {sum(1 for t in tenders if t.get('relevance_score', 0) >= 0.7)} är starka träffar.</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Upphandling</th>
                    <th style="text-align: center;">Match</th>
                </tr>
            </thead>
            <tbody>
                {tender_rows}
            </tbody>
        </table>
        <div class="cta">
            <a href="https://stackgrade.github.io/tender-system">Visa alla på TendAlert →</a>
        </div>
    </div>
    <div class="footer">
        <p>Du får det här mejlet för att du prenumererar på TendAlert.</p>
        <p>© 2026 TendAlert — Svårare att missa en upphandling</p>
    </div>
</body>
</html>
        """
        return html
    
    def _build_text_email(self, tenders: List[dict], customer_name: str) -> str:
        """Build plain text email."""
        
        lines = [
            f"🔔 Nya upphandlingar - {len(tenders)} matchar din profil",
            "",
            f"Hej {customer_name}!",
            "",
            f"Vi har hittat {len(tenders)} upphandlingar som kan vara relevanta för dig:",
            "",
        ]
        
        for i, t in enumerate(tenders[:10], 1):
            title = t.get('tender_title', 'Unknown')[:70]
            url = t.get('tender_url', '')
            score_pct = int(t.get('relevance_score', 0.5) * 100)
            lines.append(f"{i}. {title}")
            lines.append(f"   Match: {score_pct}% | {url}")
            lines.append("")
        
        lines.extend([
            "---",
            "TendAlert - Svårare att missa en upphandling",
            "https://stackgrade.github.io/tender-system"
        ])
        
        return "\n".join(lines)


def main():
    """Test email sending."""
    
    # Load matched tenders
    try:
        with open("/home/larry/projects/tender-system/data/matched_tenders.json") as f:
            tenders = json.load(f)
    except:
        print("❌ No matched tenders - run scraper and filter first")
        return
    
    print(f"📧 Testing email with {len(tenders)} matched tenders...")
    
    # Try with credentials from config
    try:
        from sys import path
        path.insert(0, "/home/larry/projects/tender-system")
        from config import SMTP_EMAIL, SMTP_PASSWORD
        sender = EmailSender(SMTP_EMAIL, SMTP_PASSWORD)
    except:
        # Use demo mode
        sender = EmailSender()
    
    result = sender.send_tender_alert(
        to_email="alex@exempel.se",
        matched_tenders=tenders,
        customer_name="Alex"
    )
    
    print(f"\nResultat: {result.message}")
    if result.demo_mode:
        print("💡 För att skicka riktiga mejl, lägg till SMTP credentials i config.py")


if __name__ == "__main__":
    main()