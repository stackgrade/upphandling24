# Module 06: Email - Notification Delivery

## Purpose
Send email notifications to customers when matching tenders are found.
Uses Gmail SMTP (100 emails/day free).

## Input
- Customer email and profile
- List of matched tenders from Module 05

## Output
- Email sent with tender summaries and links

## Technical Approach
- Python smtplib for Gmail SMTP
- HTML email template
- Daily digest or instant notifications (configurable)
- Track delivery status

## Files
- email_sender.py - Main email logic
- templates.py - HTML email templates
- config.yaml - SMTP settings

## Status
⏳ In Progress