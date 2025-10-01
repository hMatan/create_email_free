from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
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

    def close_any_overlays(self):
        """Close any modal overlays or popups that might be blocking clicks"""
        print("🔍 Checking for overlays/modals to close...")

        # Common overlay/modal close selectors
        close_selectors = [
            # Close buttons
            '[data-testid="close"]',
            '[aria-label="Close"]',
            '.close',
            '.modal-close',
            '.overlay-close',
            'button[aria-label="Close"]',
            'button.close',

            # X buttons
            'button:contains("×")',
            'button:contains("✕")',
            '[data-dismiss="modal"]',

            # Overlay backgrounds (clicking outside modal)
            '.modal-backdrop',
            '.overlay-backdrop',
            '.modal-overlay',
            '[data-state="open"]',

            # ESC key alternative - click outside
            'body'
        ]

        for selector in close_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        try:
                            element.click()
                            print(f"✅ Closed overlay using selector: {selector}")
                            time.sleep(1)
                            return True
                        except:
                            continue
            except:
                continue

        # Try pressing Escape key
        try:
            from selenium.webdriver.common.keys import Keys
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            print("✅ Sent ESC key to close overlay")
            time.sleep(1)
            return True
        except:
            pass

        print("ℹ️ No overlays found to close")
        return False

    def click_element_advanced(self, element, description="element"):
        """Advanced click method that handles overlays and various click issues"""
        print(f"🎯 Attempting advanced click on {description}...")

        methods = [
            # Method 1: Regular click
            lambda: element.click(),

            # Method 2: Close overlays first then click
            lambda: (self.close_any_overlays(), time.sleep(1), element.click()),

            # Method 3: JavaScript click
            lambda: self.driver.execute_script("arguments[0].click();", element),

            # Method 4: ActionChains click
            lambda: ActionChains(self.driver).move_to_element(element).click().perform(),

            # Method 5: Force click with JavaScript after removing overlays
            lambda: (
                self.driver.execute_script("""
                    // Remove overlays
                    var overlays = document.querySelectorAll('[class*="overlay"], [class*="modal"], [style*="z-index"], [class*="backdrop"]');
                    overlays.forEach(function(overlay) {
                        if (overlay.style.zIndex > 100 || overlay.classList.contains('fixed')) {
                            overlay.remove();
                        }
                    });
                    // Click the element
                    arguments[0].click();
                """, element)
            ),

            # Method 6: Scroll into view and click
            lambda: (
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element),
                time.sleep(1),
                element.click()
            ),

            # Method 7: Move to element and force click
            lambda: (
                ActionChains(self.driver).move_to_element(element).perform(),
                time.sleep(1),
                self.driver.execute_script("arguments[0].click();", element)
            )
        ]

        for i, method in enumerate(methods, 1):
            try:
                print(f"🔄 Trying click method {i} for {description}...")
                method()
                print(f"✅ Successfully clicked {description} using method {i}")
                return True
            except Exception as e:
                print(f"❌ Method {i} failed: {str(e)[:100]}...")
                time.sleep(2)
                continue

        print(f"❌ All click methods failed for {description}")
        return False

    def check_for_username_error(self):
        """Check if there's a username error on the page"""
        try:
            # Wait a moment for any error messages to appear
            time.sleep(2)

            error_selectors = [
                '[class*="error"]',
                '[class*="invalid"]',
                '.text-red-500',
                '.text-danger',
                '[role="alert"]',
                '.alert-danger',
                '.text-red-600',
                '[class*="text-red"]',
                '.invalid-feedback',
                '.error-message'
            ]

            for selector in error_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        error_text = element.text.strip()
                        if error_text and ('משתמש' in error_text or 'קיים' in error_text or 
                                         'exists' in error_text.lower() or 'already' in error_text.lower() or
                                         'taken' in error_text.lower() or 'בשימוש' in error_text):
                            print(f"⚠️ Username error detected: {error_text}")
                            return True

            # Also check page source for Hebrew error messages
            page_source = self.driver.page_source
            if 'שם משתמש כבר בשימוש' in page_source or 'השם משתמש כבר קיים' in page_source:
                print("⚠️ Username conflict detected in page source")
                return True

            return False
        except Exception as e:
            print(f"❌ Error checking for username error: {e}")
            return False

    def generate_sequential_username_with_retry(self):
        """
        Generate sequential username with conflict detection and retry
        """
        counter_file = 'username_counter.txt'
        max_attempts = 50  # Try up to 50 usernames

        for attempt in range(max_attempts):
            try:
                # Read current counter
                if os.path.exists(counter_file):
                    with open(counter_file, 'r') as f:
                        current_num = int(f.read().strip())
                else:
                    current_num = 350

                # Generate username
                username = f"tomtom{current_num}"

                # Increment for next time
                next_num = current_num + 1
                if next_num > 600:
                    next_num = 350

                # Save next counter
                with open(counter_file, 'w') as f:
                    f.write(str(next_num))

                print(f"🔢 Attempt {attempt + 1}: Generated username: {username} (next will be tomtom{next_num})")
                return username

            except Exception as e:
                print(f"❌ Error generating username: {e}")
                continue

        # If we've tried all usernames, use random
        import random
        fallback_num = random.randint(700, 999)  # Different range to avoid conflicts
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
        Find activation link from message details files - Simple version
        Returns activation link or None if not found
        """
        print("🔍 Looking for activation link in message files...")

        try:
            import glob
            import time

            # Find recent message files (last 30 minutes)
            current_time = time.time()
            recent_threshold = 1800  # 30 minutes

            message_files = glob.glob('message_details_*.json')
            recent_files = []

            for file_path in message_files:
                try:
                    file_time = os.path.getmtime(file_path)
                    if (current_time - file_time) < recent_threshold:
                        recent_files.append(file_path)
                        print(f"📄 Found recent file: {file_path}")
                    else:
                        print(f"⏰ Skipping old file: {file_path}")
                except Exception as e:
                    print(f"❌ Error checking file time for {file_path}: {e}")

            if not recent_files:
                print("❌ No recent message detail files found")
                return None

            print(f"📄 Processing {len(recent_files)} recent message files")

            # Check each recent file
            for message_file in recent_files:
                print(f"📖 Checking file: {message_file}...")

                try:
                    with open(message_file, 'r', encoding='utf-8') as f:
                        message_data = json.load(f)

                    # Look in different fields
                    fields_to_check = ['body_text', 'body_html', 'text', 'body', 'content', 'html']

                    for field in fields_to_check:
                        if field in message_data:
                            content = str(message_data[field])

                            # Simple string search - no complex regex
                            if 'confirmation-token' in content:
                                # Extract the URL manually
                                start_pos = content.find('https://client.embyiltv.io/confirmation-token/')
                                if start_pos != -1:
                                    # Find the end of the URL (space, newline, or bracket)
                                    end_chars = [' ', '\n', '\r', ']', ')', '}', '"', "'", '<']
                                    end_pos = len(content)

                                    for char in end_chars:
                                        char_pos = content.find(char, start_pos)
                                        if char_pos != -1 and char_pos < end_pos:
                                            end_pos = char_pos

                                    activation_link = content[start_pos:end_pos].strip()
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
                if self.click_element_advanced(back_button, "'חזרה להתחברות' button"):
                    print("✅ Clicked 'חזרה להתחברות' button")
                    time.sleep(5)  # Wait for login page to load
                else:
                    print("❌ Could not click 'חזרה להתחברות' button")
                    return False
            else:
                print("❌ Could not find 'חזרה להתחברות' button")
                return False

            # Take screenshot of login page
            self.driver.save_screenshot("activation_step2_login_page.png")
            print("📸 Screenshot saved: activation_step2_login_page.png")

            # STEP 2: Enter email and password for login
            print("📝 Step 2: Entering email and password for login...")
            print(f"📧 Email: {email}")
            print(f"🔐 Password: {password}")

            # Find email field (first field)
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="email" i]',
                'input[placeholder*="אימייל"]',
                'input:first-of-type',
                'form input:first-child'
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
                return False

            # Find password field (second field)  
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[placeholder*="password" i]',
                'input[placeholder*="סיסמה"]',
                'input:nth-of-type(2)',
                'form input:nth-child(2)'
            ]

            password_field = self.find_element_by_selectors(password_selectors)
            if password_field:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", password_field)
                time.sleep(1)
                password_field.clear()
                password_field.send_keys(password)
                print("✅ Password entered successfully")
            else:
                print("❌ Password field not found")
                return False

            # Take screenshot before clicking login
            self.driver.save_screenshot("activation_step2_login_filled.png")
            print("📸 Screenshot saved: activation_step2_login_filled.png")

            # STEP 3: Click "התחברות" (Login) button
            print("🔘 Step 3: Looking for 'התחברות' button...")

            login_button = None
            try:
                # Use XPath to find login button
                login_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'התחברות')] | //input[@value='התחברות']")
                ))
            except:
                print("❌ Could not find 'התחברות' button by text, trying generic selectors...")
                login_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button.btn-primary',
                    'button:last-of-type'
                ]
                login_button = self.find_element_by_selectors(login_selectors)

            if login_button:
                if self.click_element_advanced(login_button, "'התחברות' button"):
                    print("✅ Clicked 'התחברות' button")
                    time.sleep(5)  # Wait for next page to load
                else:
                    print("❌ Could not click 'התחברות' button")
                    return False
            else:
                print("❌ Could not find 'התחברות' button")
                return False

            # Take screenshot of setup page
            self.driver.save_screenshot("activation_step3_setup_page.png")
            print("📸 Screenshot saved: activation_step3_setup_page.png")

            # STEP 4: Enter username and new password with retry mechanism
            print("📝 Step 4: Setting up username and password with retry mechanism...")

            new_password = "Aa123456!"
            print(f"🔐 New Password: {new_password}")

            # Username retry loop
            max_username_attempts = 10
            for username_attempt in range(max_username_attempts):
                print(f"🔄 Username attempt {username_attempt + 1}/{max_username_attempts}")

                # Generate username
                username = self.generate_sequential_username_with_retry()
                print(f"👤 Trying Username: {username}")

                # Find username field (first field on setup page)
                username_selectors = [
                    'input[name="username"]',
                    'input[name="userName"]',
                    'input[placeholder*="username" i]',
                    'input[placeholder*="שם משתמש"]',
                    'input[type="text"]:first-of-type',
                    'form input:first-child'
                ]

                username_field = self.find_element_by_selectors(username_selectors)
                if not username_field:
                    print("❌ Username field not found")
                    return False

                # Clear and enter username
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", username_field)
                time.sleep(1)
                username_field.clear()
                username_field.send_keys(username)
                print(f"✅ Username entered: {username}")

                # Find new password field (second field on setup page)
                new_password_selectors = [
                    'input[type="password"]',
                    'input[name="password"]',
                    'input[name="newPassword"]',
                    'input[placeholder*="password" i]',
                    'input[placeholder*="סיסמה"]',
                    'input:nth-of-type(2)',
                    'form input:nth-child(2)'
                ]

                new_password_field = self.find_element_by_selectors(new_password_selectors)
                if new_password_field:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", new_password_field)
                    time.sleep(1)
                    new_password_field.clear()
                    new_password_field.send_keys(new_password)
                    print(f"✅ New password entered: {new_password}")
                else:
                    print("❌ New password field not found")
                    return False

                # Find password confirmation field (third field on setup page)
                password_confirm_selectors = [
                    'input[type="password"]:nth-of-type(2)',  # Second password field
                    'input[name="passwordConfirm"]',
                    'input[name="confirmPassword"]', 
                    'input[name="password_confirmation"]',
                    'input[placeholder*="confirm" i]',
                    'input[placeholder*="אישור" i]',
                    'input[placeholder*="חזור" i]',
                    'input:nth-of-type(3)',  # Third field overall
                    'form input:nth-child(3)'  # Third input in form
                ]

                password_confirm_field = self.find_element_by_selectors(password_confirm_selectors)
                if password_confirm_field:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", password_confirm_field)
                    time.sleep(1)
                    password_confirm_field.clear()
                    password_confirm_field.send_keys(new_password)  # Same password
                    print(f"✅ Password confirmation entered: {new_password}")
                else:
                    print("⚠️ Password confirmation field not found (might not be required)")

                # Take screenshot before submit attempt
                self.driver.save_screenshot(f"activation_step4_setup_filled_attempt_{username_attempt + 1}.png")
                print(f"📸 Screenshot saved: activation_step4_setup_filled_attempt_{username_attempt + 1}.png")

                # STEP 5: Click "אשר" (Confirm) button with advanced handling
                print(f"🔘 Step 5: Looking for 'אשר' button (attempt {username_attempt + 1})...")

                # Wait a bit more for any animations to complete
                time.sleep(3)

                confirm_button = None
                try:
                    # Use XPath to find confirm button
                    confirm_button = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(text(), 'אשר')] | //input[@value='אשר']")
                    ))
                except:
                    print("❌ Could not find 'אשר' button by text, trying generic selectors...")
                    confirm_selectors = [
                        'button[type="submit"]',
                        'input[type="submit"]',
                        'button.btn-primary',
                        'button:last-of-type',
                        'form button:last-child',
                        'button:contains("אשר")',
                        '[value="אשר"]'
                    ]
                    confirm_button = self.find_element_by_selectors(confirm_selectors)

                if not confirm_button:
                    print("❌ Could not find 'אשר' button")
                    return False

                print("🎯 Found confirm button, attempting advanced click...")
                if self.click_element_advanced(confirm_button, "'אשר' button"):
                    print("✅ Clicked 'אשר' button")
                    time.sleep(5)  # Wait for response

                    # Check for username error
                    if self.check_for_username_error():
                        print(f"⚠️ Username '{username}' is already taken, trying next username...")
                        # Take error screenshot
                        self.driver.save_screenshot(f"activation_username_error_attempt_{username_attempt + 1}.png")
                        print(f"📸 Error screenshot saved: activation_username_error_attempt_{username_attempt + 1}.png")
                        continue  # Try next username
                    else:
                        print(f"🎉 Username '{username}' accepted! Account creation successful!")
                        break  # Success! Exit the retry loop
                else:
                    print("❌ Could not click 'אשר' button even with advanced methods")
                    return False

            else:
                # This runs if the for loop completes without breaking (all attempts failed)
                print(f"❌ Failed to create account after {max_username_attempts} username attempts")
                return False

            # Wait for final processing
            time.sleep(5)

            # Take final screenshot
            self.driver.save_screenshot("activation_step5_completed.png")
            print("📸 Screenshot saved: activation_step5_completed.png")

            # Save activation details
            activation_info = {
                'timestamp': datetime.datetime.now().isoformat(),
                'activation_link': activation_link,
                'login_email': email,
                'login_password': password,
                'username': username,
                'account_password': new_password,
                'browser_used': self.browser_type,
                'success': True,
                'workflow': 'Click חזרה להתחברות → Login → Setup username/password → Click אשר',
                'note': f'Sequential username {username} after retry mechanism, account password {new_password}'
            }

            # Save with timestamp
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"activation_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(activation_info, f, indent=2, ensure_ascii=False)
            print(f"💾 Activation info saved to: {filename}")

            # Also save as activation_info.json for Jenkins
            with open('activation_info.json', 'w', encoding='utf-8') as f:
                json.dump(activation_info, f, indent=2, ensure_ascii=False)
            print("💾 Also saved as: activation_info.json")

            # Create user.password.txt with final credentials
            user_password_content = f"""EmbyIL Account Credentials
========================
Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Email: {email}
Username: {username}
Password: {new_password}
Login URL: https://client.embyiltv.io/login
Account Status: Activated
Workflow: Confirmation → Login → Setup → Confirmed
Username Retry: Used retry mechanism to find available username
"""

            with open('user.password.txt', 'w', encoding='utf-8') as f:
                f.write(user_password_content)
            print("💾 Final credentials saved to: user.password.txt")

            print("🎉 Account activation completed successfully!")
            print(f"📋 Final credentials:")
            print(f"   📧 Login Email: {email}")
            print(f"   👤 Username: {username}")
            print(f"   🔐 Account Password: {new_password}")
            print(f"   🌐 Browser Used: {self.browser_type}")
            print("📄 All details saved to user.password.txt")

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
