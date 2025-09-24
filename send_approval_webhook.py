import requests
import json
import sys
import os
from datetime import datetime

class DiscordApprovalWebhook:
    def __init__(self, webhook_url):
        """Initialize Discord webhook sender"""
        self.webhook_url = webhook_url
        if not self.webhook_url.startswith('https://discord.com/api/webhooks/'):
            raise ValueError("Invalid Discord webhook URL")
    
    def send_approval_request(self, build_number, build_url, email_info="Not available"):
        """Send approval request via Discord webhook"""
        
        try:
            # Extract email address from email_info
            email_address = "Not found"
            if "EMAIL_ADDRESS=" in email_info:
                for line in email_info.split('\n'):
                    if 'EMAIL_ADDRESS=' in line:
                        email_address = line.split('=')[1].strip()
                        break
            
            print(f"📤 Sending Discord approval request...")
            print(f"🔗 Discord Webhook: ...{self.webhook_url[-20:]}")
            
            # Create beautiful Discord embed
            payload = {
                "username": "Jenkins Pipeline Bot",
                "avatar_url": "https://www.jenkins.io/images/logos/jenkins/jenkins.png",
                "embeds": [
                    {
                        "title": "🚀 EmbyIL Account Creation Pipeline",
                        "description": f"**Build #{build_number}** requires your approval to proceed",
                        "color": 0x00ff00,  # Green color
                        "fields": [
                            {
                                "name": "📧 Generated Temporary Email", 
                                "value": f"``````",
                                "inline": False
                            },
                            {
                                "name": "🎯 What will happen next:",
                                "value": "🌐 **Website Signup** - Automatic registration\n📬 **Message Processing** - Check for emails\n🎯 **Account Activation** - Complete setup\n📨 **Email Delivery** - Send credentials to matan@yahoo.com",
                                "inline": False
                            },
                            {
                                "name": "⏰ Time Limit",
                                "value": "30 minutes",
                                "inline": True
                            },
                            {
                                "name": "🏗️ Build Info",
                                "value": f"Build: #{build_number}\nJob: EmbyIL Pipeline",
                                "inline": True
                            }
                        ],
                        "footer": {
                            "text": "Jenkins Automation System",
                            "icon_url": "https://www.jenkins.io/images/logos/jenkins/jenkins.png"
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                        "thumbnail": {
                            "url": "https://cdn-icons-png.flaticon.com/512/2099/2099147.png"  # Automation icon
                        }
                    },
                    {
                        "title": "👆 Click Here to Approve",
                        "description": f"**[🔗 APPROVE PIPELINE]({build_url}input/)**\n\n*Or copy this link:*\n`{build_url}input/`",
                        "color": 0xff6b35,  # Orange color
                        "footer": {
                            "text": "Click the link above to approve the pipeline"
                        }
                    }
                ]
            }
            
            # Send the webhook
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                print("✅ Discord approval webhook sent successfully!")
                print(f"📱 Check your Discord server for the approval message")
                return True
            else:
                print(f"❌ Discord webhook failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send Discord webhook: {str(e)}")
            return False

    def send_completion_notification(self, build_number, build_url, success=True, credentials_info=""):
        """Send completion notification after pipeline finishes"""
        
        try:
            if success:
                color = 0x00ff00  # Green
                title = "✅ EmbyIL Pipeline Completed Successfully!"
                description = f"Build #{build_number} has finished successfully"
                thumbnail_url = "https://cdn-icons-png.flaticon.com/512/190/190411.png"  # Success icon
            else:
                color = 0xff0000  # Red
                title = "❌ EmbyIL Pipeline Failed"
                description = f"Build #{build_number} encountered an error"
                thumbnail_url = "https://cdn-icons-png.flaticon.com/512/564/564619.png"  # Error icon
            
            payload = {
                "username": "Jenkins Pipeline Bot",
                "avatar_url": "https://www.jenkins.io/images/logos/jenkins/jenkins.png",
                "embeds": [
                    {
                        "title": title,
                        "description": description,
                        "color": color,
                        "fields": [
                            {
                                "name": "🏗️ Build Info",
                                "value": f"Build: #{build_number}\nJob: EmbyIL Pipeline",
                                "inline": True
                            },
                            {
                                "name": "🔗 Build Details", 
                                "value": f"[View Build]({build_url})",
                                "inline": True
                            }
                        ],
                        "footer": {
                            "text": "Jenkins Automation System"
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                        "thumbnail": {
                            "url": thumbnail_url
                        }
                    }
                ]
            }
            
            if success and credentials_info:
                payload["embeds"][0]["fields"].insert(0, {
                    "name": "👤 Final Credentials Created",
                    "value": f"``````",
                    "inline": False
                })
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code in [200, 204]:
                print("✅ Discord completion notification sent!")
                return True
            else:
                print(f"❌ Discord completion notification failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send completion notification: {str(e)}")
            return False

def main():
    """Main function for Jenkins integration"""
    print("📤 Starting Discord Approval Webhook")
    print("=" * 50)
    
    # Get parameters from environment variables
    webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    build_number = os.environ.get('BUILD_NUMBER', 'Unknown')
    build_url = os.environ.get('BUILD_URL', 'http://localhost:8080/')
    notification_type = os.environ.get('NOTIFICATION_TYPE', 'approval')
    
    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL environment variable not set!")
        print("💡 Set it in Jenkins pipeline environment")
        sys.exit(1)
    
    # Read email info if available
    email_info = "Not available"
    if os.path.exists('email_info.txt'):
        try:
            with open('email_info.txt', 'r') as f:
                email_info = f.read().strip()
                print(f"📧 Found email info: {len(email_info)} characters")
        except Exception as e:
            print(f"⚠️ Could not read email info: {e}")
    
    # Initialize Discord webhook
    discord_webhook = DiscordApprovalWebhook(webhook_url)
    
    if notification_type == 'approval':
        # Send approval request
        success = discord_webhook.send_approval_request(build_number, build_url, email_info)
    elif notification_type == 'completion':
        # Read credentials if available
        credentials_info = ""
        if os.path.exists('user.password.txt'):
            try:
                with open('user.password.txt', 'r') as f:
                    credentials_info = f.read().strip()
            except Exception as e:
                print(f"⚠️ Could not read credentials: {e}")
        
        success = discord_webhook.send_completion_notification(
            build_number, 
            build_url, 
            success=True, 
            credentials_info=credentials_info
        )
    else:
        print(f"❌ Unknown notification type: {notification_type}")
        sys.exit(1)
    
    if success:
        print("🎉 Discord notification sent successfully!")
        sys.exit(0)
    else:
        print("⚠️ Discord notification failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
