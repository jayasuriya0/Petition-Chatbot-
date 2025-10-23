"""
Email templates and utilities for the Petition Management System
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
import random
import string
from datetime import datetime, timedelta, UTC
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

# Email queue and thread pool for async processing
email_queue = queue.Queue()
email_executor = ThreadPoolExecutor(max_workers=3)

# Email configuration
SMTP_SERVER = getattr(Config, 'SMTP_SERVER', 'smtp.outlook.com')
SMTP_PORT = getattr(Config, 'SMTP_PORT', 587)
SMTP_USERNAME = getattr(Config, 'SMTP_USERNAME', '')
SMTP_PASSWORD = getattr(Config, 'SMTP_PASSWORD', '')
FROM_EMAIL = getattr(Config, 'FROM_EMAIL', 'noreply@petitionsystem.com')

print(f"📧 Email Configuration:")
print(f"   SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
print(f"   From Email: {FROM_EMAIL}")
print(f"   SMTP Username: {SMTP_USERNAME}")
print(f"   Email Worker Thread Started: Active")

def send_email_worker():
    """Background worker that processes email queue"""
    print(f"🚀 Email worker thread started and waiting for emails...")
    while True:
        try:
            email_data = email_queue.get(timeout=1)
            if email_data is None:  # Shutdown signal
                break
            
            to_email = email_data['to_email']
            subject = email_data['subject']
            body = email_data['body']
            
            print(f"📤 Processing email to: {to_email}")
            print(f"   Subject: {subject}")
            
            try:
                msg = MIMEMultipart()
                msg['From'] = FROM_EMAIL
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'html'))
                
                # Use timeout to prevent hanging
                print(f"   Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
                server.starttls()
                print(f"   Authenticating as {SMTP_USERNAME}...")
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                print(f"   Sending message...")
                server.send_message(msg)
                server.quit()
                
                print(f"✅ Email sent successfully to {to_email}")
            except smtplib.SMTPException as smtp_error:
                print(f"❌ SMTP error sending to {to_email}: {str(smtp_error)}")
            except Exception as e:
                print(f"❌ Failed to send email to {to_email}: {str(e)}")
            finally:
                email_queue.task_done()
        except queue.Empty:
            continue

# Start email worker thread
email_worker_thread = threading.Thread(target=send_email_worker, daemon=True)
email_worker_thread.start()

def queue_email(to_email, subject, body):
    """Add email to queue for async sending"""
    email_queue.put({
        'to_email': to_email,
        'subject': subject,
        'body': body
    })
    print(f"📧 Email queued for: {to_email}")

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def get_otp_email_template(user_name, otp):
    """
    Returns a beautiful HTML email template for OTP verification
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify Your Email</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border-radius: 8px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #4361ee 0%, #7209b7 100%); padding: 40px 30px; text-align: center;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">
                                    <span style="font-size: 36px;">🔒</span><br>
                                    Email Verification
                                </h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                <h2 style="color: #333333; margin: 0 0 20px 0; font-size: 24px;">
                                    Hello {user_name}! 👋
                                </h2>
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    Thank you for registering with the Petition Management System. To complete your registration and start making a difference in your community, please verify your email address.
                                </p>
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                    Use the following One-Time Password (OTP) to verify your account:
                                </p>
                                
                                <!-- OTP Box -->
                                <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 0 0 30px 0;">
                                    <tr>
                                        <td align="center">
                                            <div style="background: linear-gradient(135deg, #4361ee 0%, #7209b7 100%); padding: 20px 40px; border-radius: 8px; display: inline-block;">
                                                <span style="color: #ffffff; font-size: 36px; font-weight: bold; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                                    {otp}
                                                </span>
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                                
                                <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 0 0 30px 0; border-radius: 4px;">
                                    <p style="color: #856404; margin: 0; font-size: 14px;">
                                        ⚠️ <strong>Important:</strong> This OTP will expire in 10 minutes. Please do not share this code with anyone.
                                    </p>
                                </div>
                                
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0;">
                                    If you didn't create an account with us, please ignore this email or contact our support team.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Features Section -->
                        <tr>
                            <td style="padding: 0 30px 30px 30px;">
                                <h3 style="color: #333333; font-size: 18px; margin: 0 0 20px 0;">
                                    What you can do after verification:
                                </h3>
                                <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                    <tr>
                                        <td style="padding: 10px 0;">
                                            <span style="color: #4cc9f0; font-size: 20px; margin-right: 10px;">✓</span>
                                            <span style="color: #666666; font-size: 14px;">Submit and track petitions</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px 0;">
                                            <span style="color: #4cc9f0; font-size: 20px; margin-right: 10px;">✓</span>
                                            <span style="color: #666666; font-size: 14px;">Get real-time updates on petition status</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px 0;">
                                            <span style="color: #4cc9f0; font-size: 20px; margin-right: 10px;">✓</span>
                                            <span style="color: #666666; font-size: 14px;">Connect with local departments</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 10px 0;">
                                            <span style="color: #4cc9f0; font-size: 20px; margin-right: 10px;">✓</span>
                                            <span style="color: #666666; font-size: 14px;">Make a difference in your community</span>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #dee2e6;">
                                <p style="color: #6c757d; font-size: 14px; margin: 0 0 10px 0;">
                                    <strong>Petition Management System</strong>
                                </p>
                                <p style="color: #6c757d; font-size: 12px; margin: 0 0 15px 0;">
                                    Empowering communities through civic engagement
                                </p>
                                <p style="color: #6c757d; font-size: 11px; margin: 15px 0 0 0;">
                                    © 2025 Petition Management System. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def get_welcome_email_template(user_name):
    """
    Returns a welcome email template after successful verification
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome!</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border-radius: 8px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #4361ee 0%, #7209b7 100%); padding: 40px 30px; text-align: center;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">
                                    <span style="font-size: 36px;">🎉</span><br>
                                    Welcome to Our Community!
                                </h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                <h2 style="color: #333333; margin: 0 0 20px 0; font-size: 24px;">
                                    Congratulations {user_name}! 🎊
                                </h2>
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    Your email has been successfully verified! You're now part of a community that's making real change happen.
                                </p>
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                    Ready to get started? Here's what you can do now:
                                </p>
                                
                                <div style="background-color: #e7f3ff; padding: 20px; border-radius: 8px; margin: 0 0 30px 0;">
                                    <p style="color: #004085; margin: 0; font-size: 14px; line-height: 1.6;">
                                        💡 <strong>Pro Tip:</strong> Start by exploring active petitions in your area or submit your first petition to address issues that matter to you!
                                    </p>
                                </div>
                                
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    We're excited to have you on board!
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #dee2e6;">
                                <p style="color: #6c757d; font-size: 14px; margin: 0 0 10px 0;">
                                    <strong>Petition Management System</strong>
                                </p>
                                <p style="color: #6c757d; font-size: 12px; margin: 0;">
                                    © 2025 Petition Management System. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def send_email(to_email, subject, html_body):
    """Queue email for async sending (non-blocking)"""
    queue_email(to_email, subject, html_body)
    return True  # Return immediately, email will be sent in background

def send_otp_email(to_email, otp, user_name):
    """Send OTP email to user (async)"""
    subject = "🔒 Verify Your Email - Petition Management System"
    html_body = get_otp_email_template(user_name, otp)
    return send_email(to_email, subject, html_body)

def send_welcome_email(to_email, user_name):
    """Send welcome email after successful verification (async)"""
    subject = "🎉 Welcome to Petition Management System!"
    html_body = get_welcome_email_template(user_name)
    return send_email(to_email, subject, html_body)

def get_otp_expiry():
    """Get OTP expiry time (10 minutes from now)"""
    return datetime.now(UTC) + timedelta(minutes=10)

def get_petition_submission_email_template(user_name, ticket_id, title):
    """
    Returns HTML email template for petition submission confirmation
    """
    current_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Petition Submitted</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border-radius: 8px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #4361ee 0%, #7209b7 100%); padding: 40px 30px; text-align: center;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">
                                    <span style="font-size: 36px;">📝</span><br>
                                    Petition Submitted Successfully
                                </h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                <h2 style="color: #333333; margin: 0 0 20px 0; font-size: 24px;">
                                    Dear {user_name},
                                </h2>
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                    Your petition has been submitted successfully and is now being reviewed by the concerned department.
                                </p>
                                
                                <!-- Petition Details Box -->
                                <div style="background: linear-gradient(135deg, #e7f3ff 0%, #f0e7ff 100%); padding: 25px; border-radius: 8px; margin: 0 0 30px 0; border-left: 4px solid #4361ee;">
                                    <p style="color: #333333; margin: 0 0 12px 0; font-size: 14px;">
                                        <strong style="color: #4361ee;">Petition Title:</strong><br>
                                        <span style="font-size: 16px; color: #212529;">{title}</span>
                                    </p>
                                    <p style="color: #333333; margin: 0 0 12px 0; font-size: 14px;">
                                        <strong style="color: #4361ee;">Ticket ID:</strong><br>
                                        <span style="font-size: 18px; color: #212529; font-weight: 600; font-family: 'Courier New', monospace;">{ticket_id}</span>
                                    </p>
                                    <p style="color: #333333; margin: 0; font-size: 14px;">
                                        <strong style="color: #4361ee;">Submission Date:</strong><br>
                                        <span style="color: #212529;">{current_time}</span>
                                    </p>
                                </div>
                                
                                <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; margin: 0 0 30px 0; border-left: 4px solid #f8961e;">
                                    <p style="color: #856404; margin: 0; font-size: 14px; line-height: 1.6;">
                                        📌 <strong>Important:</strong> Save your Ticket ID ({ticket_id}) to track your petition status at any time.
                                    </p>
                                </div>
                                
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    You will receive email notifications whenever your petition status is updated.
                                </p>
                                
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0;">
                                    Thank you for using the Petition Management System!
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #dee2e6;">
                                <p style="color: #6c757d; font-size: 14px; margin: 0 0 10px 0;">
                                    <strong>Petition Management System</strong>
                                </p>
                                <p style="color: #6c757d; font-size: 12px; margin: 0;">
                                    © 2025 Petition Management System. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def get_petition_status_update_email_template(user_name, ticket_id, title, old_status, new_status):
    """
    Returns HTML email template for petition status update notification
    """
    current_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    status_info = {
        'pending': {
            'label': 'Pending Review',
            'color': '#f8961e',
            'bg_color': '#fff3cd',
            'icon': '⏳'
        },
        'in_progress': {
            'label': 'In Progress',
            'color': '#0096c7',
            'bg_color': '#d1ecf1',
            'icon': '🔄'
        },
        'resolved': {
            'label': 'Resolved',
            'color': '#059669',
            'bg_color': '#d4edda',
            'icon': '✅'
        },
        'rejected': {
            'label': 'Rejected',
            'color': '#f72585',
            'bg_color': '#f8d7da',
            'icon': '❌'
        }
    }
    
    old_info = status_info.get(old_status, {'label': old_status, 'color': '#6c757d', 'bg_color': '#e2e3e5', 'icon': '📋'})
    new_info = status_info.get(new_status, {'label': new_status, 'color': '#6c757d', 'bg_color': '#e2e3e5', 'icon': '📋'})
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Petition Status Updated</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
        <table role="presentation" style="width: 100%; border-collapse: collapse;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border-radius: 8px; overflow: hidden;">
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #4361ee 0%, #7209b7 100%); padding: 40px 30px; text-align: center;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">
                                    <span style="font-size: 36px;">🔔</span><br>
                                    Petition Status Updated
                                </h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px;">
                                <h2 style="color: #333333; margin: 0 0 20px 0; font-size: 24px;">
                                    Dear {user_name},
                                </h2>
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                    Great news! The status of your petition has been updated by the department.
                                </p>
                                
                                <!-- Petition Details Box -->
                                <div style="background: linear-gradient(135deg, #e7f3ff 0%, #f0e7ff 100%); padding: 25px; border-radius: 8px; margin: 0 0 30px 0; border-left: 4px solid #4361ee;">
                                    <p style="color: #333333; margin: 0 0 12px 0; font-size: 14px;">
                                        <strong style="color: #4361ee;">Petition Title:</strong><br>
                                        <span style="font-size: 16px; color: #212529;">{title}</span>
                                    </p>
                                    <p style="color: #333333; margin: 0 0 12px 0; font-size: 14px;">
                                        <strong style="color: #4361ee;">Ticket ID:</strong><br>
                                        <span style="font-size: 18px; color: #212529; font-weight: 600; font-family: 'Courier New', monospace;">{ticket_id}</span>
                                    </p>
                                    <p style="color: #333333; margin: 0; font-size: 14px;">
                                        <strong style="color: #4361ee;">Update Date:</strong><br>
                                        <span style="color: #212529;">{current_time}</span>
                                    </p>
                                </div>
                                
                                <!-- Status Change Box -->
                                <div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin: 0 0 30px 0;">
                                    <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                        <tr>
                                            <td style="width: 45%; text-align: center; padding: 15px;">
                                                <div style="background-color: {old_info['bg_color']}; padding: 15px; border-radius: 6px; border: 2px solid {old_info['color']};">
                                                    <p style="margin: 0; font-size: 12px; color: #666666;">Previous Status</p>
                                                    <p style="margin: 10px 0 0 0; font-size: 20px; color: {old_info['color']}; font-weight: 600;">
                                                        {old_info['icon']} {old_info['label']}
                                                    </p>
                                                </div>
                                            </td>
                                            <td style="width: 10%; text-align: center; font-size: 24px; color: #4361ee;">
                                                →
                                            </td>
                                            <td style="width: 45%; text-align: center; padding: 15px;">
                                                <div style="background-color: {new_info['bg_color']}; padding: 15px; border-radius: 6px; border: 2px solid {new_info['color']};">
                                                    <p style="margin: 0; font-size: 12px; color: #666666;">New Status</p>
                                                    <p style="margin: 10px 0 0 0; font-size: 20px; color: {new_info['color']}; font-weight: 600;">
                                                        {new_info['icon']} {new_info['label']}
                                                    </p>
                                                </div>
                                            </td>
                                        </tr>
                                    </table>
                                </div>
                                
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                    You can track your petition anytime using your Ticket ID on our website.
                                </p>
                                
                                <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0;">
                                    Thank you for using the Petition Management System!
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #dee2e6;">
                                <p style="color: #6c757d; font-size: 14px; margin: 0 0 10px 0;">
                                    <strong>Petition Management System</strong>
                                </p>
                                <p style="color: #6c757d; font-size: 12px; margin: 0;">
                                    © 2025 Petition Management System. All rights reserved.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

def send_petition_submission_email(user_email, user_name, ticket_id, title):
    """Send petition submission confirmation email (async)"""
    subject = f"📝 Petition Submitted Successfully - Ticket ID: {ticket_id}"
    html_body = get_petition_submission_email_template(user_name, ticket_id, title)
    return send_email(user_email, subject, html_body)

def send_petition_status_update_email(user_email, user_name, ticket_id, title, old_status, new_status):
    """Send petition status update notification email (async)"""
    subject = f"🔔 Petition Status Updated - Ticket ID: {ticket_id}"
    html_body = get_petition_status_update_email_template(user_name, ticket_id, title, old_status, new_status)
    return send_email(user_email, subject, html_body)
