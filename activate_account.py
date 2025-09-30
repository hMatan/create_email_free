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
                    print(f"🎉 {browser_name} is ready for activation!")
                    return
            except Exception as e:
                print(f"❌ {browser_name} failed: {e}")
                continue

        raise Exception("❌ No browsers available for activation")

    def _try_firefox(self):
        """Try Firefox setup"""
        firefox_options = FirefoxOptions()
        if self.headless:
            firefox_options.add_argument("--headless")

        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.add_argument("--disable-gpu")
        firefox_options.add_argument("--window-size=1280,720")

        try:
            service = FirefoxService("/usr/bin/geckodriver")
            return webdriver.Firefox(service=service, options=firefox_options)
        except Exception as e:
            print(f"Firefox setup failed: {e}")
            return None

    def _try_chrome(self):
        """Try Chrome setup"""
        chrome_options = ChromeOptions()
        if self.headless:
            chrome_options.add_argument("--headless=new")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,720")

        try:
            return webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Chrome setup failed: {e}")
            return None

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

    def generate_username(self):
        """Generate a random username"""
        prefixes = ['user', 'player', 'viewer', 'guest', 'member']
        prefix = random.choice(prefixes)
        numbers = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{numbers}"

    def read_signup_email_and_website_password(self):
        """
        Read email and website password from signup files
        Returns (email, password) or (None, None) if failed
        """
        print("📂 Reading signup information...")

        # Try signup_info.json first (Jenkins compatible)
        if os.path.exists('signup_info.json'):
            try:
                with open('signup_info.json', 'r') as f:
                    signup_data = json.load(f)
                    email = signup_data.get('email')
                    password = signup_data.get('password')

                    if email and password:
                        print(f"✅ Found signup info: {email}")
                        return email, password
            except Exception as e:
                print(f"❌ Error reading signup_info.json: {e}")

        # Fallback: try to find any signup_*.json files
        try:
            import glob
            signup_files = glob.glob('signup_*.json')
            if signup_files:
                # Use the most recent one
                signup_files.sort()
                latest_file = signup_files[-1]

                with open(latest_file, 'r') as f:
                    signup_data = json.load(f)
                    email = signup_data.get('email')
                    password = signup_data.get('password')

                    if email and password:
                        print(f"✅ Found signup info in {latest_file}: {email}")
                        return email, password
        except Exception as e:
            print(f"❌ Error reading signup files: {e}")

        print("❌ Could not find signup email and password")
        return None, None

    def find_activation_link(self):
        """
        Find activation link from message details files
        Returns activation link or None if not found
        """
        print("🔍 Looking for activation link in message files...")

        try:
            import glob
            message_files = glob.glob('message_details_*.json')

            if not message_files:
                print("❌ No message detail files found")
                return None

            print(f"📄 Found {len(message_files)} message files")

            for message_file in message_files:
                print(f"📖 Checking {message_file}...")

                try:
                    with open(message_file, 'r', encoding='utf-8') as f:
                        message_data = json.load(f)

                    # Look for activation link in different possible fields
                    text_fields = ['text', 'body_text', 'content', 'body_html']

                    for field in text_fields:
                        if field in message_data:
                            content = message_data[field]

                            # Look for activation links
                            link_patterns = [
                                r'https?://[^\s]*activate[^\s]*',
                                r'https?://[^\s]*activation[^\s]*',
                                r'https?://[^\s]*confirm[^\s]*',
                                r'https?://[^\s]*verify[^\s]*',
                                r'https?://client\.embyiltv\.io[^\s]*'
                            ]

                            for pattern in link_patterns:
                                matches = re.findall(pattern, str(content), re.IGNORECASE)
                                if matches:
                                    activation_link = matches[0].strip()
                                    print(f"✅ Found activation link: {activation_link}")
                                    return activation_link

                except Exception as e:
                    print(f"❌ Error reading {message_file}: {e}")
                    continue

            print("❌ No activation link found in any message file")
            return None

        except Exception as e:
            print(f"❌ Error searching for activation link: {e}")
            return None

    def activate_account(self):
        """
        Jenkins-compatible wrapper for account activation
        Automatically reads all required info from files and performs activation
        Returns True if successful, False otherwise
        """
        print("🔐 Starting automated account activation for Jenkins...")

        try:
            # Step 1: Read email and website password
            print("📖 Reading email and password from files...")
            email, website_password = self.read_signup_email_and_website_password()
            if not email or not website_password:
                print("❌ Could not read email address or password")
                return False

            # Step 2: Find activation link from message details
            print("🔍 Looking for activation link...")
            activation_link = self.find_activation_link()
            if not activation_link:
                print("❌ Could not find activation link")
                print("💡 Make sure Step 4 (message processing) completed successfully")
                return False

            print(f"📋 Activation Summary:")
            print(f"   📧 Email: {email}")
            print(f"   🔐 Website Password: {website_password}")
            print(f"   🔗 Activation Link: {activation_link}")
            print(f"   🌐 Browser: {self.browser_type}")

            # Step 3: Perform the actual activation
            print("🚀 Starting activation process...")
            success = self._perform_activation(activation_link, email, website_password)

            if success:
                print("🎉 Account activation completed successfully!")
                return True
            else:
                print("❌ Account activation failed")
                return False

        except Exception as e:
            print(f"❌ Activation error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _perform_activation(self, activation_link, email, password):
        """
        Perform the actual activation process
        This is the main activation logic
        """
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
                time.sleep(5) # Wait for page to load
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
                time.sleep(8) # Wait for completion
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
            print(f"   📧 Email: {email}")
            print(f"   👤 Username: {username}")
            print(f"   🔐 New Password: rh1234")
            print(f"   🌐 Browser Used: {self.browser_type}")
            print("📄 All details saved to user.password.txt")

            return True

        except Exception as e:
            print(f"❌ Error during activation: {str(e)}")
            if self.driver:
                self.driver.save_screenshot("activation_error.png")
                print("📸 Error screenshot saved: activation_error.png")
            return False

    def cleanup(self):
        """
        Cleanup method for proper resource management
        """
        print("🧹 Cleaning up activation resources...")
        self.close()

    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                print(f"🔒 {self.browser_type} browser closed successfully")
            except Exception as e:
                print(f"⚠️ Error closing browser: {e}")

def main():
    """Main function for standalone testing"""
    print("🚀 Starting EmbyIL Account Activation")
    print("=" * 60)

    bot = None
    try:
        # Initialize activation bot
        bot = EmbyILAccountActivation(headless=True)

        # Perform activation automatically
        success = bot.activate_account()

        if success:
            print("🎉 Activation completed successfully!")
            sys.exit(0)
        else:
            print("❌ Activation failed")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        sys.exit(1)
    finally:
        if bot:
            bot.cleanup()
        print("🏁 Script finished")

if __name__ == "__main__":
    main()
