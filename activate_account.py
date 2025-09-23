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

    def read_signup_email_from_file(self):
        """Read email address from signup_info.json"""
        try:
            if os.path.exists('signup_info.json'):
                with open('signup_info.json', 'r') as f:
                    signup_data = json.load(f)
                    email = signup_data.get('email')
                    if email:
                        print(f"📧 Found signup email: {email}")
                        return email
            
            # Fallback to email_info.txt
            if os.path.exists('email_info.txt'):
                with open('email_info.txt', 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if 'EMAIL_ADDRESS=' in line:
                            email = line.split('=')[1].strip()
                            print(f"📧 Found email from email_info.txt: {email}")
                            return email
                            
            print("❌ Could not find email address")
            return None
            
        except Exception as e:
            print(f"❌ Error reading email: {e}")
            return None

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
            
            activation_link = None
            
            for json_file in json_files:
                print(f"📄 Checking {json_file}...")
                try:
                    with open(json_file, 'r') as f:
                        message_data = json.load(f)
                    
                    # Look for activation link in different fields
                    fields_to_check = [
                        message_data.get('text', ''),
                        message_data.get('html', ''),
                        json.dumps(message_data)  # Check entire JSON as string
                    ]
                    
                    for field in fields_to_check:
                        if field:
                            # Look for confirmation token link
                            match = re.search(r'https://client\.embyiltv\.io/confirmation-token/[a-zA-Z0-9-]+', field)
                            if match:
                                activation_link = match.group(0)
                                print(f"✅ Found activation link: {activation_link}")
                                return activation_link
                                
                except json.JSONDecodeError:
                    print(f"⚠️ Could not parse {json_file}")
                    continue
                except Exception as e:
                    print(f"⚠️ Error reading {json_file}: {e}")
                    continue
            
            print("❌ No activation link found in any message")
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

    def activate_account(self, activation_link, email):
        """Perform the full account activation process"""
        try:
            print(f"🌐 Opening activation link: {activation_link}")
            self.driver.get(activation_link)
            
            wait = WebDriverWait(self.driver, 20)
            time.sleep(3)
            
            # Take screenshot of activation page
            self.driver.save_screenshot("activation_step1_page.png")
            print("📸 Screenshot saved: activation_step1_page.png")
            
            # Step 1: Enter email and password
            print("📝 Step 1: Entering email and password...")
            
            # Find email field
            email_selectors = [
                'input[name="email"]',
                'input[type="email"]',
                'input[placeholder*="email" i]',
                'input[placeholder*="Email"]'
            ]
            
            email_field = self.find_element_by_selectors(email_selectors)
            if email_field:
                email_field.clear()
                email_field.send_keys(email)
                print("✅ Email entered")
            else:
                print("❌ Email field not found")
            
            # Find password field
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                'input[placeholder*="password" i]',
                'input[placeholder*="Password"]'
            ]
            
            password_field = self.find_element_by_selectors(password_selectors)
            if password_field:
                password_field.clear()
                password_field.send_keys("Aa123456!")
                print("✅ Password entered")
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
                '.btn-primary'
            ]
            
            submit_button = self.find_element_by_selectors(submit_selectors)
            if submit_button:
                submit_button.click()
                print("✅ Step 1 submit clicked")
                time.sleep(5)  # Wait for page to load
            else:
                print("❌ Submit button not found")
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
                'input[type="text"]:first-of-type'
            ]
            
            username_field = self.find_element_by_selectors(username_selectors)
            if username_field:
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
                'input[placeholder*="password" i]'
            ]
            
            new_password_field = self.find_element_by_selectors(new_password_selectors)
            if new_password_field:
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
                'input[placeholder*="confirm" i]'
            ]
            
            confirm_password_field = self.find_element_by_selectors(confirm_password_selectors)
            if confirm_password_field:
                confirm_password_field.clear()
                confirm_password_field.send_keys("rh1234")
                print("✅ Password confirmation entered")
            else:
                print("❌ Password confirmation field not found")
            
            # Take screenshot before final submit
            self.driver.save_screenshot("activation_step2_filled.png")
            print("📸 Screenshot saved: activation_step2_filled.png")
            
            # Find and click final submit button
            final_submit_button = self.find_element_by_selectors(submit_selectors)
            if final_submit_button:
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
                'original_password': 'Aa123456!',
                'username': username,
                'new_password': 'rh1234',
                'browser_used': self.browser_type,
                'success': True
            }
            
            with open('activation_info.json', 'w') as f:
                json.dump(activation_info, f, indent=2)
            print("💾 Activation info saved to: activation_info.json")
            
            print("🎉 Account activation completed successfully!")
            print(f"📋 Final credentials:")
            print(f"   Email: {email}")
            print(f"   Username: {username}")
            print(f"   Password: rh1234")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during activation: {str(e)}")
            if self.driver:
                self.driver.save_screenshot("activation_error.png")
            return False

    def find_element_by_selectors(self, selectors):
        """Try to find element using multiple selectors"""
        for selector in selectors:
            try:
                wait = WebDriverWait(self.driver, 5)
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
        
        # Read email from signup info
        email = bot.read_signup_email_from_file()
        if not email:
            print("❌ Could not read email address")
            sys.exit(1)
        
        # Find activation link from message details
        activation_link = bot.find_activation_link()
        if not activation_link:
            print("❌ Could not find activation link")
            sys.exit(1)
        
        # Perform activation
        success = bot.activate_account(activation_link, email)
        
        if success:
            print("🎉 Account activation completed successfully!")
            sys.exit(0)
        else:
            print("⚠️ Account activation completed with warnings")
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
