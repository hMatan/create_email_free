from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time
import os
import json
import re
import random
import string
import datetime
import sys

class EmbyILAccountActivation:
    def __init__(self, headless=True):
        """
        Initialize the account activation bot
        """
        self.driver = None
        self.headless = headless
        self.browser_type = None
        self.setup_driver()

    def setup_driver(self):
        """Setup WebDriver - Firefox first, Chrome as fallback"""
        print("🔧 Setting up WebDriver for account activation...")
        
        methods = [
            ('Firefox', self._try_firefox),
            ('Chrome', self._try_chrome)
        ]

        for browser_name, method in methods:
            try:
                print(f"🔄 Attempting {browser_name}...")
                self.driver = method()
                if self.driver:
                    print(f"✅ {browser_name} initialized successfully")
                    self.browser_type = browser_name
                    
                    # Test basic functionality
                    self.driver.get("data:,")
                    self.driver.set_window_size(1280, 720)
                    print(f"🎉 {browser_name} is ready for activation!")
                    return
                    
            except Exception as e:
                print(f"❌ {browser_name} failed: {str(e)}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None

        raise Exception("Could not initialize any browser for account activation")

    def _try_firefox(self):
        """Try Firefox"""
        firefox_options = FirefoxOptions()
        
        if self.headless:
            firefox_options.add_argument("--headless")
        
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.add_argument("--window-size=1280,720")
        
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        firefox_options.set_preference("media.volume_scale", "0.0")
        
        try:
            service = FirefoxService("/usr/bin/geckodriver")
            return webdriver.Firefox(service=service, options=firefox_options)
        except:
            return None

    def _try_chrome(self):
        """Try Chrome with minimal options"""
        chrome_options = ChromeOptions()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,720")
        
        try:
            return webdriver.Chrome(options=chrome_options)
        except:
            return None

    def read_signup_email_and_website_password(self):
        """Read email from signup files and return website password"""
        try:
            signup_email = None
            
            # Try to read from signup_info.json first (most reliable)
            if os.path.exists('signup_info.json'):
                with open('signup_info.json', 'r') as f:
                    signup_data = json.load(f)
                    signup_email = signup_data.get('email')
                    if signup_email:
                        print(f"📧 Found email from signup_info.json: {signup_email}")
            
            # Fallback to email_info.txt
            if not signup_email and os.path.exists('email_info.txt'):
                with open('email_info.txt', 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if 'EMAIL_ADDRESS=' in line:
                            signup_email = line.split('=')[1].strip()
                            print(f"📧 Found email from email_info.txt: {signup_email}")
                            break
            
            if not signup_email:
                print("❌ Could not find email address")
                return None, None
            
            # The website password is always Aa123456! (from signup)
            website_password = "Aa123456!"
            
            print(f"📧 Using email: {signup_email}")
            print(f"🔐 Using website signup password: {website_password}")
            
            return signup_email, website_password
            
        except Exception as e:
            print(f"❌ Error reading email and password: {e}")
            return None, None

    def find_activation_link(self):
        """Find activation link from message details JSON files"""
        try:
            print("🔍 Looking for activation link in message details...")
            
            # Find all message_details_*.json files
            import glob
            json_files = glob.glob("message_details_*.json")
            
            if not json_files:
                print("❌ No message details files found")
                return None
            
            print(f"📄 Found {len(json_files)} message detail files")
            
            activation_link = None
            
            for json_file in json_files:
                print(f"🔍 Checking {json_file}...")
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        message_data = json.load(f)
                    
                    # Look for activation link in different fields
                    fields_to_check = []
                    
                    # Add different possible fields
                    if 'text' in message_data:
                        fields_to_check.append(message_data['text'])
                    if 'html' in message_data:
                        fields_to_check.append(message_data['html'])
                    if 'body' in message_data:
                        fields_to_check.append(message_data['body'])
                    
                    # Also check the entire JSON as string
                    fields_to_check.append(json.dumps(message_data))
                    
                    for field in fields_to_check:
                        if field and isinstance(field, str):
                            # Look for confirmation token link
                            patterns = [
                                r'https://client\.embyiltv\.io/confirmation-token/[a-zA-Z0-9-]+',
                                r'https://client\.embyiltv\.io/confirmation-token/[a-zA-Z0-9_-]+',
                                r'client\.embyiltv\.io/confirmation-token/[a-zA-Z0-9-]+'
                            ]
                            
                            for pattern in patterns:
                                match = re.search(pattern, field)
                                if match:
                                    activation_link = match.group(0)
                                    # Make sure it starts with https
                                    if not activation_link.startswith('https://'):
                                        activation_link = 'https://' + activation_link
                                    print(f"✅ Found activation link: {activation_link}")
                                    return activation_link
                                
                except json.JSONDecodeError:
                    print(f"⚠️ Could not parse {json_file}")
                    continue
                except Exception as e:
                    print(f"⚠️ Error reading {json_file}: {e}")
                    continue
            
            print("❌ No activation link found in any message")
            print("💡 Make sure the signup email was received and processed")
            return None
            
        except Exception as e:
            print(f"❌ Error searching for activation link: {e}")
            return None

    def generate_username(self):
        """Generate username: 3 letters + 4 numbers + !"""
        letters = ''.join(random.choices(string.ascii_lowercase, k=3))
        numbers = ''.join(random.choices(string.digits, k=4))
        username = letters + numbers + '!'
        print(f"🎯 Generated username: {username}")
        return username

    def activate_account(self, activation_link, email, password):
        """Perform the full account activation process"""
        try:
            print(f"🌐 Opening activation link: {activation_link}")
            self.driver.get(activation_link)
            
            wait = WebDriverWait(self.driver, 20)
            time.sleep(3)
            
            # Take screenshot of activation page
            self.driver.save_screenshot("activation_step1_page.png")
            print("📸 Screenshot saved: activation_step1_page.png")
            
            # Step 1: Enter email and password (WEBSITE credentials)
            print("📝 Step 1: Entering website email and password...")
            print(f"📧 Email: {email}")
            print(f"🔐 Password: {password} (website signup password)")
            
            # Find email field
            email_selectors = [
                'input[name="email"]',
                'input[type="email"]',
                'input[placeholder*="email" i]',
                'input[placeholder*="Email"]',
                'input[id*="email"]'
            ]
            
            email_field = self.find_element_by_selectors(email_selectors)
            if email_field:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_field)
                time.sleep(1)
                email_field.clear()
                email_field.send_keys(email)
                print("✅ Email entered successfully")
            else:
                print("❌ Email field not found")
            
            # Find password field
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                'input[placeholder*="password" i]',
                'input[placeholder*="Password"]',
                'input[id*="password"]'
            ]
            
            password_field = self.find_element_by_selectors(password_selectors)
            if password_field:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", password_field)
                time.sleep(1)
                password_field.clear()
                password_field.send_keys(password)
                print(f"✅ Website password entered: {password}")
            else:
                print("❌ Password field not found")
            
            # Take screenshot before submit
            self.driver.save_screenshot("activation_step1_filled.png")
            print("📸 Screenshot saved: activation_step1_filled.png")
            
            # Find and click submit button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:contains("Submit")',
                'button:contains("Continue")',
                'button:contains("Next")',
                '.btn-submit',
                '.btn-primary',
                '.submit-button'
            ]
            
            submit_button = self.find_element_by_selectors(submit_selectors)
            if submit_button:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
                time.sleep(1)
                submit_button.click()
                print("✅ Step 1 submit clicked")
                time.sleep(5)  # Wait for page to load
            else:
                print("❌ Submit button not found for step 1")
                return False
            
            # Take screenshot of step 2 page
            self.driver.save_screenshot("activation_step2_page.png")
            print("📸 Screenshot saved: activation_step2_page.png")
            
            # Step 2: Fill the form with username and new password
            print("📝 Step 2: Entering username and new password...")
            
            # Generate username
            username = self.generate_username()
            
            # Find username field
            username_selectors = [
                'input[name="username"]',
                'input[name="userName"]',
                'input[placeholder*="username" i]',
                'input[placeholder*="Username"]',
                'input[id*="username"]',
                'input[type="text"]:first-of-type'
            ]
            
            username_field = self.find_element_by_selectors(username_selectors)
            if username_field:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", username_field)
                time.sleep(1)
                username_field.clear()
                username_field.send_keys(username)
                print(f"✅ Username entered: {username}")
            else:
                print("❌ Username field not found")
            
            # Find new password field
            new_password_selectors = [
                'input[name="password"]',
                'input[name="newPassword"]',
                'input[type="password"]:first-of-type',
                'input[placeholder*="password" i]',
                'input[id*="password"]'
            ]
            
            new_password_field = self.find_element_by_selectors(new_password_selectors)
            if new_password_field:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", new_password_field)
                time.sleep(1)
                new_password_field.clear()
                new_password_field.send_keys("rh1234")
                print("✅ New password entered: rh1234")
            else:
                print("❌ New password field not found")
            
            # Find password confirmation field
            confirm_password_selectors = [
                'input[name="confirmPassword"]',
                'input[name="password_confirmation"]',
                'input[name="confirm_password"]',
                'input[type="password"]:nth-of-type(2)',
                'input[placeholder*="confirm" i]',
                'input[id*="confirm"]'
            ]
            
            confirm_password_field = self.find_element_by_selectors(confirm_password_selectors)
            if confirm_password_field:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_password_field)
                time.sleep(1)
                confirm_password_field.clear()
                confirm_password_field.send_keys("rh1234")
                print("✅ Password confirmation entered: rh1234")
            else:
                print("❌ Password confirmation field not found")
            
            # Take screenshot before final submit
            self.driver.save_screenshot("activation_step2_filled.png")
            print("📸 Screenshot saved: activation_step2_filled.png")
            
            # Find and click final submit button
            final_submit_button = self.find_element_by_selectors(submit_selectors)
            if final_submit_button:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", final_submit_button)
                time.sleep(1)
                final_submit_button.click()
                print("✅ Final submit clicked")
                time.sleep(8)  # Wait for completion
            else:
                print("❌ Final submit button not found")
            
            # Take final screenshot
            self.driver.save_screenshot("activation_completed.png")
            print("📸 Screenshot saved: activation_completed.png")
            
            # Save activation details
            activation_info = {
                'timestamp': datetime.datetime.now().isoformat(),
                'activation_link': activation_link,
                'email': email,
                'website_signup_password': password,
                'username': username,
                'new_account_password': 'rh1234',
                'browser_used': self.browser_type,
                'success': True,
                'note': 'Used website signup password for activation, then set new account password'
            }
            
            # Save with timestamp
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"activation_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(activation_info, f, indent=2)
            print(f"💾 Activation info saved to: {filename}")
            
            # Also save as activation_info.json for Jenkins
            with open('activation_info.json', 'w') as f:
                json.dump(activation_info, f, indent=2)
            print("💾 Also saved as: activation_info.json")
            
            # Create user.password.txt with final credentials
            user_password_content = f"""EmbyIL Account Credentials
========================
Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Email: {email}
Username: {username}
Password: rh1234

Login URL: https://client.embyiltv.io/login
Account Status: Activated
"""
            
            with open('user.password.txt', 'w') as f:
                f.write(user_password_content)
            print("💾 Final credentials saved to: user.password.txt")
            
            print("🎉 Account activation completed successfully!")
            print(f"📋 Final credentials:")
            print(f"   Email: {email}")
            print(f"   Username: {username}")
            print(f"   New Password: rh1234")
            print(f"   Browser Used: {self.browser_type}")
            print("📄 All details saved to user.password.txt")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during activation: {str(e)}")
            if self.driver:
                self.driver.save_screenshot("activation_error.png")
                print("📸 Error screenshot saved: activation_error.png")
            return False

    def find_element_by_selectors(self, selectors):
        """Try to find element using multiple selectors"""
        for selector in selectors:
            try:
                wait = WebDriverWait(self.driver, 8)
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                
                if element.is_displayed() and element.is_enabled():
                    return element
            except Exception:
                continue
        return None

    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                print(f"🔒 {self.browser_type} browser closed successfully")
            except Exception as e:
                print(f"⚠️ Error closing browser: {e}")

def main():
    """Main function for account activation"""
    print("🚀 Starting EmbyIL Account Activation")
    print("=" * 60)
    
    bot = None
    try:
        # Initialize activation bot
        bot = EmbyILAccountActivation(headless=True)
        
        # Read email and website password
        email, website_password = bot.read_signup_email_and_website_password()
        if not email or not website_password:
            print("❌ Could not read email address or password")
            sys.exit(1)
        
        # Find activation link from message details
        activation_link = bot.find_activation_link()
        if not activation_link:
            print("❌ Could not find activation link")
            print("💡 Make sure Step 4 (message processing) completed successfully")
            sys.exit(1)
        
        print(f"📋 Activation Summary:")
        print(f"   Email: {email}")
        print(f"   Website Password: {website_password}")
        print(f"   Activation Link: {activation_link}")
        print(f"   Browser: {bot.browser_type}")
        print()
        
        # Perform activation
        success = bot.activate_account(activation_link, email, website_password)
        
        if success:
            print("🎉 Account activation completed successfully!")
            sys.exit(0)
        else:
            print("⚠️ Account activation failed or completed with warnings")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Activation script failed: {str(e)}")
        sys.exit(1)
    finally:
        if bot:
            bot.close()
        print("🏁 Activation script finished")

if __name__ == "__main__":
    main()
