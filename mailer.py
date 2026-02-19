"""
mailer.py - EduSense email utility
Set env vars EDUSENSE_EMAIL and EDUSENSE_PASS (Gmail app password) to enable.
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SENDER_EMAIL = os.environ.get("EDUSENSE_EMAIL", "")
SENDER_PASS  = os.environ.get("EDUSENSE_PASS",  "")


def send_registration_email(student):
    """Send HTML registration confirmation. Returns (bool, str)."""
    recipient = student.get("email", "")
    if not recipient:
        return False, "No email provided."
    if not SENDER_EMAIL or not SENDER_PASS:
        return True, "DEV_MODE"

    cgpa      = student.get("cgpa", "N/A")
    grade     = student.get("grade", "N/A")
    pass_fail = student.get("pass_fail", "N/A")
    pf_color  = "#30D158" if pass_fail == "Pass" else "#FF453A"

    html = f"""
<!DOCTYPE html><html><body style="font-family:Arial,sans-serif;background:#050A14;
color:#E8F4FD;padding:2rem;margin:0">
<div style="max-width:560px;margin:auto;background:#0C1526;border-radius:16px;
padding:2rem;border:1px solid rgba(0,245,255,0.15)">
  <h2 style="color:#00F5FF;margin:0 0 .25rem">Welcome to EduSense 🎓</h2>
  <p style="color:#6B7FA3;font-size:.8rem;margin:0 0 1.5rem;
     letter-spacing:2px;text-transform:uppercase">
     Student Performance Intelligence System</p>
  <p>Hi <strong style="color:#E8F4FD">{student["name"]}</strong>,</p>
  <p>You have been successfully registered. Here is your profile summary:</p>
  <table style="width:100%;border-collapse:collapse;margin:1rem 0">
    <tr><td style="padding:6px 0;color:#6B7FA3;font-size:.85rem">Student ID</td>
        <td style="color:#00F5FF;font-weight:bold">#{student["student_id"]}</td></tr>
    <tr><td style="padding:6px 0;color:#6B7FA3;font-size:.85rem">Domain</td>
        <td>{student["domain"]}</td></tr>
    <tr><td style="padding:6px 0;color:#6B7FA3;font-size:.85rem">Branch</td>
        <td>{student["branch"]}</td></tr>
    <tr><td style="padding:6px 0;color:#6B7FA3;font-size:.85rem">CGPA</td>
        <td style="color:#30D158;font-weight:bold">{cgpa} / 10</td></tr>
    <tr><td style="padding:6px 0;color:#6B7FA3;font-size:.85rem">Grade</td>
        <td style="font-weight:bold">{grade}</td></tr>
    <tr><td style="padding:6px 0;color:#6B7FA3;font-size:.85rem">Status</td>
        <td style="color:{pf_color};font-weight:bold">{pass_fail}</td></tr>
  </table>
  <p style="color:#6B7FA3;font-size:.75rem;margin-top:1.5rem">
    This is an automated message from EduSense. Please do not reply.</p>
</div></body></html>"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"EduSense Registration — Welcome, {student['name']}!"
        msg["From"]    = SENDER_EMAIL
        msg["To"]      = recipient
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as srv:
            srv.login(SENDER_EMAIL, SENDER_PASS)
            srv.sendmail(SENDER_EMAIL, recipient, msg.as_string())
        return True, "Email sent!"
    except Exception as exc:
        return False, str(exc)