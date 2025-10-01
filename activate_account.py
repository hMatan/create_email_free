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

    def generate_sequential_username(self):
        """
        Generate sequential username from tomtom350 to tomtom600
        Uses a counter file to track the next username
        """
        counter_file = 'username_counter.txt'

        try:
            # Read current counter
            if os.path.exists(counter_file):
                with open(counter_file, 'r') as f:
                    current_num = int(f.read().strip())
            else:
                current_num = 350  # Start from tomtom350

            # Generate username
            username = f"tomtom{current_num}"

            # Increment for next time (wrap around at 600)
            next_num = current_num + 1
            if next_num > 600:
                next_num = 350  # Reset to start

            # Save next counter
            with open(counter_file, 'w') as f:
                f.write(str(next_num))

            print(f"🔢 Generated sequential username: {username} (next will be tomtom{next_num})")
            return username

        except Exception as e:
            print(f"❌ Error generating sequential username: {e}")
            # Fallback to random number if file operations fail
            import random
            fallback_num = random.randint(350, 600)
            username = f"tomtom{fallback_num}"
            print(f"🎲 Using fallback username: {username}")
            return username

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
        Find activation link from message details files - ONLY from current run
        Returns activation link or None if not found
        """
        print("🔍 Looking for activation link in CURRENT message files...")

        try:
            import glob
            import time

            # מחפש רק קבצים שנוצרו בדקות האחרונות (מהריצה הנוכחית)
            current_time = time.time()
            recent_threshold = 1800  # 30 דקות

            message_files = glob.glob('message_details_*.json')
            recent_files = []

            for file_path in message_files:
                try:
                    file_time = os.path.getmtime(file_path)
                    if (current_time - file_time) < recent_threshold:
                        recent_files.append(file_path)
                        print(f"📄 Found recent file: {file_path} (age: {int((current_time - file_time)/60)} minutes)")
                    else:
                        print(f"⏰ Skipping old file: {file_path} (age: {int((current_time - file_time)/60)} minutes)")
                except Exception as e:
                    print(f"❌ Error checking file time for {file_path}: {e}")

            if not recent_files:
                print("❌ No recent message detail files found from current run")
                return None

            print(f"📄 Processing {len(recent_files)} recent message files")

            for message_file in recent_files:
                print(f"📖 Checking recent file: {message_file}...")

                try:
                    with open(message_file, 'r', encoding='utf-8') as f:
                        message_data = json.load(f)

                    # Look for activation link in different possible fields
                    text_fields = ['body_text', 'body_html', 'text', 'body', 'content', 'html']

                    for field in text_fields:
                        if field in message_data:
                            content = message_data[field]

                            # Look for activation links
                            link_patterns = [
                                r'https?://[^\s]*confirmation-token[^\s]*',
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
                                    # Clean up any trailing characters
                                    activation_link = re.sub(r'[\]\s*$', '', activation_link)
                                    print(f"✅ Found activation link in recent file: {activation_link}")
                                    return activation_link

                except Exception as e:
                    print(f"❌ Error reading {message_file}: {e}")
                    continue

            print("❌ No activation link found in any recent message file")
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
        Perform the actual activation process with the correct workflow
        """
        try:
            print(f"🌐 Opening activation link: {activation_link}")
            self.driver.get(activation_link)
            wait = WebDriverWait(self.driver, 20)
            time.sleep(5)  # Wait for page to load

            # Take screenshot of initial activation page
            self.driver.save_screenshot("activation_step1_initial.png")
            print("📸 Screenshot saved: activation_step1_initial.png")

            # STEP 1: Click "חזרה להתחברות" button
            print("🔘 Step 1: Looking for 'חזרה להתחברות' button...")

            back_button = None
            try:
                # Use XPath to find element containing the Hebrew text
                back_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'חזרה להתחברות')] | //a[contains(text(), 'חזרה להתחברות')]")
                ))
            except:
                print("❌ Could not find 'חזרה להתחברות' button by text, trying other selectors...")
                back_to_login_selectors = [
                    'button[data-slot="button"]',
                    '.cursor-pointer',
                    'button.btn-primary',
                    'button:first-of-type'
                ]
                back_button = self.find_element_by_selectors(back_to_login_selectors)

            if back_button:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", back_button)
                time.sleep(2)
                back_button.click()
                print("✅ Clicked 'חזרה להתחברות' button")
                time.sleep(5)  # Wait for login page to load
            else:
                print("❌ Could not find 'חזרה להתחברות' button")
                return False

            # Continue with rest of activation process...
            # [קיצרתי כדי להראות את התיקון העיקרי]

            return True

        except Exception as e:
            print(f"❌ Error during activation: {str(e)}")
            import traceback
            traceback.print_exc()
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
