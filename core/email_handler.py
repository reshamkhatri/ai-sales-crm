import imaplib
import email
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from core import crm, ai_brain
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_IMAP_SERVER, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT

def check_new_emails():
    """Poll Gmail IMAP for new emails, AI analyzes, drafts reply."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return {"error": "Email credentials not configured"}
    
    try:
        mail = imaplib.IMAP4_SSL(EMAIL_IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")
        
        # Search for unread emails from today
        today = datetime.now().strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(UNSEEN SINCE "{today}")')
        
        results = []
        for msg_id in messages[0].split():
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            from_addr = msg["From"]
            subject = msg["Subject"]
            body = ""
            
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
            
            # Extract email from From header
            email_match = re.search(r'<([^>]+)>', from_addr)
            sender_email = email_match.group(1) if email_match else from_addr
            sender_name = from_addr.split("<")[0].strip() if "<" in from_addr else "Unknown"
            
            # Process via unified inbox
            from core import unified_inbox
            res = unified_inbox.handle_incoming_message(
                lead_identifier=sender_email,
                message_text=f"Subject: {subject}\n\n{body[:1000]}",
                platform="email",
                extra_data={"email": sender_email, "name": sender_name, "notes": f"Subject: {subject}"}
            )
            lead_id = res["lead_id"]
            reply_draft = res["reply"]
            analysis = res["analysis"]
            
            # Optionally auto-send (set to False if you want to review first)
            AUTO_SEND_EMAIL = False
            if AUTO_SEND_EMAIL:
                send_email(sender_email, f"Re: {subject}", reply_draft)
            
            # Log AI reply draft and re-score
            unified_inbox.log_ai_reply(lead_id, "email", reply_draft, analysis)
            
            results.append({
                "lead_id": lead_id,
                "email": sender_email,
                "subject": subject,
                "draft_reply": reply_draft,
                "auto_sent": AUTO_SEND_EMAIL,
                "analysis": analysis
            })
        
        mail.close()
        mail.logout()
        return results
    
    except Exception as e:
        return {"error": str(e)}

def send_email(to_email, subject, body):
    """Send an email via SMTP (Gmail)"""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return {"error": "Email credentials not configured"}
    
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return {"success": True, "to": to_email}
    except Exception as e:
        return {"error": str(e)}

def send_proposal_email(lead_id, proposal_text):
    """Send a proposal email to a lead"""
    lead = crm.get_lead(lead_id)
    if not lead or not lead.get("email"):
        return {"error": "Lead has no email"}
    
    subject = f"Web Design Proposal for {lead.get('business_name', 'Your Business')}"
    return send_email(lead["email"], subject, proposal_text)
