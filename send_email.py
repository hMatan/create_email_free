import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import datetime
import sys

class EmailSender:
    def __init__(self):
        """Initialize email sender with environment variables"""
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Get credentials from environment variables or use defaults
        self.sender_email = os.environ.get('GMAIL_SENDER', 'your-jenkins-email@gmail.com')
        self.sender_password = os.environ.get('GMAIL_APP_PASSWORD', 'your-16-char-app-password')
        self.recipient_email = "matan@yahoo.com"
        
        print(f"📧 Email settings:")
        print(f"   From: {self.sender_email}")
        print(f"   To: {self.recipient_email}")
        print(f"   SMTP: {self.smtp_server}:{self.smtp_port}")
    
    def send_credentials_email(self, credentials_file_path):
        """Send the credentials file via email"""
        try:
            print("📧 Preparing to send credentials email...")
            
            # Check if credentials file exists
            if not os.path.exists(credentials_file_path):
                print(f"❌ Credentials file not found: {credentials_file_path}")
                return False
            
            # Read credentials content
            with open(credentials_file_path, 'r') as f:
                credentials_content = f.read()
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = f"EmbyIL Account Credentials - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Email body
            body = f"""Hi Matan,

Your EmbyIL account has been successfully created and activated automatically by Jenkins!

Here are your login credentials:

{credentials_content}

The credentials file is also attached to this email for your convenience.

This email was sent automatically by the Jenkins automation system.

Best regards,
Jenkins EmbyIL Automation
Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach the credentials file
            with open(credentials_file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= user.password.txt'
            )
            msg.attach(part)
            
            # Send email
            print("📤 Connecting to Gmail SMTP server...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            print("🔐 Authenticating with Gmail...")
            server.login(self.sender_email, self.sender_password)
            
            print("📨 Sending email...")
            text = msg.as_string()
            server.sendmail(self.sender_email, self.recipient_email, text)
            server.quit()
            
            print("✅ Email sent successfully!")
            print(f"📧 Sent to: {self.recipient_email}")
            print(f"📎 Attached: {credentials_file_path}")
            
            # Log the email sending
            log_info = {
                'timestamp': datetime.datetime.now().isoformat(),
                'recipient': self.recipient_email,
                'sender': self.sender_email,
                'file_sent': credentials_file_path,
                'status': 'success',
                'subject': f"EmbyIL Account Credentials - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            }
            
            import json
            with open('email_sent.json', 'w') as f:
                json.dump(log_info, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            print("💡 Common issues:")
            print("   - Gmail App Password not set correctly")
            print("   - 2-Factor Authentication not enabled on Gmail")
            print("   - SMTP blocked by firewall")
            
            # Log the error
            log_info = {
                'timestamp': datetime.datetime.now().isoformat(),
                'recipient': self.recipient_email,
                'sender': self.sender_email,
                'file_sent': credentials_file_path,
                'status': 'failed',
                'error': str(e)
            }
            
            import json
            with open('email_sent.json', 'w') as f:
                json.dump(log_info, f, indent=2)
            
            return False

def main():
    """Main function to send credentials email"""
    print("📧 Starting Email Sender for EmbyIL Credentials")
    print("=" * 60)
    
    try:
        # Check if credentials file exists
        credentials_file = 'user.password.txt'
        
        if not os.path.exists(credentials_file):
            print(f"❌ Credentials file not found: {credentials_file}")
            print("💡 Make sure Step 5 (Account Activation) completed successfully")
            sys.exit(1)
        
        print("📄 Credentials file found, content:")
        with open(credentials_file, 'r') as f:
            print(f.read())
        
        # Initialize email sender
        email_sender = EmailSender()
        
        # Send the email
        success = email_sender.send_credentials_email(credentials_file)
        
        if success:
            print("🎉 Credentials email sent successfully to matan@yahoo.com!")
            sys.exit(0)
        else:
            print("⚠️ Failed to send credentials email")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Email sender script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
