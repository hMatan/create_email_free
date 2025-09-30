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
import subprocess
import sys
import json
import datetime
import tempfile

class EmbyILRegistration:
    def __init__(self, headless=True):
        """
        Initialize the web automation bot for EmbyIL registration
        
        Args:
            headless (bool): Run browser in headless mode (without GUI)
        """
        self.driver = None
        self.headless = headless
        self.browser_type = None
        self.setup_driver()

    def check_system_resources(self):
        """Check system resources and available browsers"""
        try:
            print("🔍 Checking system resources and browsers...")
            
            # בדיקת /dev/shm
            result = subprocess.run(['df', '-h', '/dev/shm'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("💾 Shared memory (/dev/shm):")
                print(result.stdout)
            
            # בדיקת זיכרון כללי
            result = subprocess.run(['free', '-h'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("🧠 System memory:")
                print(result.stdout)
                
            # בדיקת דפדפנים זמינים
            browsers = []
            
            # Chrome
            result = subprocess.run(['google-chrome', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"🌐 Chrome: {result.stdout.strip()}")
                browsers.append("Chrome")
            
            # Firefox
            result = subprocess.run(['firefox-esr', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"🦊 Firefox: {result.stdout.strip()}")
                browsers.append("Firefox")
                
            print(f"📋 Available browsers: {', '.join(browsers)}")
                
        except Exception as e:
            print(f"⚠️ Could not check system resources: {e}")

    def setup_driver(self):
        """Setup WebDriver with Firefox as primary choice, Chrome as fallback"""
        print("🔧 Setting up WebDriver - Firefox first, Chrome as fallback...")
        
        # Try Firefox first (more stable in Docker)
        methods = [
            ('Firefox', self._try_firefox),
            ('Chrome with minimal options', self._try_chrome_minimal),
            ('Chrome with full options', self._try_chrome_full)
        ]

        for browser_name, method in methods:
            for attempt in range(2):  # 2 attempts per method
                try:
                    print(f"🔄 Attempting {browser_name} (attempt {attempt + 1}/2)...")
                    
                    self.driver = method()
                    if self.driver:
                        print(f"✅ Driver created with {browser_name}")
                        self.browser_type = browser_name
                        
                        # Simple test
                        try:
                            print("🧪 Testing basic functionality...")
                            self.driver.get("data:,")
                            print("✅ Basic test passed")
                            self.driver.set_window_size(1280, 720)
                            print("✅ Window size set")
                            print(f"🎉 {browser_name} is working correctly!")
                            return
                        except Exception as e:
                            print(f"❌ Basic test failed: {e}")
                            self.driver.quit()
                            self.driver = None
                            
                except Exception as e:
                    print(f"❌ {browser_name} attempt {attempt + 1} failed: {str(e)}")
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                        self.driver = None
                    
                    if attempt < 1:  # Not the last attempt
                        print("⏳ Waiting 3 seconds before retry...")
                        time.sleep(3)

        raise Exception("All browser initialization methods failed. Neither Firefox nor Chrome are working in this Docker environment.")

    def _try_firefox(self):
        """Try Firefox with optimized Docker settings"""
        firefox_options = FirefoxOptions()
        
        if self.headless:
            firefox_options.add_argument("--headless")
        
        # Firefox Docker optimizations
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.add_argument("--disable-gpu")
        firefox_options.add_argument("--window-size=1280,720")
        
        # Firefox specific preferences
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
        firefox_options.set_preference("media.volume_scale", "0.0")  # Mute audio
        firefox_options.set_preference("dom.webnotifications.enabled", False)
        firefox_options.set_preference("dom.push.enabled", False)
        
        # Create Firefox profile directory
        profile_dir = tempfile.mkdtemp(prefix="firefox_", suffix="_profile")
        firefox_options.set_preference("profile", profile_dir)
        
        print(f"📁 Firefox profile directory: {profile_dir}")
        
        try:
            service = FirefoxService("/usr/bin/geckodriver")
            return webdriver.Firefox(service=service, options=firefox_options)
        except Exception as e:
            print(f"Firefox initialization failed: {e}")
            return None

    def _try_chrome_minimal(self):
        """Try Chrome with absolutely minimal options"""
        chrome_options = ChromeOptions()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        # Only the most essential options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,720")
        
        try:
            return webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Minimal Chrome failed: {e}")
            return None

    def _try_chrome_full(self):
        """Try Chrome with full optimization (last resort)"""
        chrome_options = ChromeOptions()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")

        # Full Chrome optimization
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--window-size=1280,720")
        
        user_data_dir = tempfile.mkdtemp(prefix="chrome_", suffix="_profile")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        try:
            return webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Full Chrome failed: {e}")
            return None

    def read_email_from_file(self):
        """Read email address from email_info.txt file"""
        try:
            if os.path.exists('email_info.txt'):
                with open('email_info.txt', 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if 'EMAIL_ADDRESS=' in line:
                            email = line.split('=')[1].strip()
                            print(f"📧 Using email from file: {email}")
                            return email
            print("❌ Could not read email from email_info.txt")
            return None
        except Exception as e:
            print(f"❌ Error reading email file: {e}")
            return None

    def generate_random_credentials(self, email):
        """Generate random credentials for signup with fixed password"""
        import random
        
        # Generate random names
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa']
        last_names = ['Smith', 'Johnson', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor']
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Fixed password as requested
        password = 'Aa123456!'
        
        return first_name, last_name, password

    def save_signup_info(self, first_name, last_name, email, password, success=False):
        """Save signup information to JSON file"""
        signup_info = {
            'timestamp': datetime.datetime.now().isoformat(),
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password,
            'success': success,
            'browser_used': self.browser_type or 'Unknown',
            'url': 'https://client.embyiltv.io/sign-up',
            'note': 'Fixed password Aa123456! used for all registrations'
        }
        
        filename = f"signup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(signup_info, f, indent=2)
            print(f"💾 Signup info saved to: {filename}")
            
            # Also save as signup_info.json (for Jenkins pipeline compatibility)
            with open('signup_info.json', 'w') as f:
                json.dump(signup_info, f, indent=2)
            print("💾 Also saved as: signup_info.json")
            
        except Exception as e:
            print(f"❌ Failed to save signup info: {e}")

    def fill_registration_form(self, first_name, last_name, email, password, password_confirm):
        """Fill the registration form with provided details"""
        success = False
        
        try:
            print(f"🌐 Navigating to registration page using {self.browser_type}...")
            self.driver.get("https://client.embyiltv.io/sign-up")

            wait = WebDriverWait(self.driver, 20)
            time.sleep(5)

            # Take screenshot before filling
            self.driver.save_screenshot("signup_before_filling.png")
            print("📸 Screenshot saved: signup_before_filling.png")

            # Simplified field selectors
            field_selectors = {
                'first_name': [
                    'input[name="firstName"]',
                    'input[name="first_name"]',
                    'input[placeholder*="First"]',
                    'input[type="text"]:first-of-type'
                ],
                'last_name': [
                    'input[name="lastName"]',
                    'input[name="last_name"]',
                    'input[placeholder*="Last"]',
                    'input[type="text"]:nth-of-type(2)'
                ],
                'email': [
                    'input[name="email"]',
                    'input[type="email"]',
                    'input[placeholder*="Email"]'
                ],
                'password': [
                    'input[name="password"]',
                    'input[type="password"]',
                    'input[placeholder*="Password"]'
                ],
                'password_confirm': [
                    'input[name="confirmPassword"]',
                    'input[name="password_confirmation"]',
                    'input[type="password"]:nth-of-type(2)'
                ]
            }

            # Fill fields
            fields_filled = 0
            field_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': password,
                'password_confirm': password_confirm
            }
            
            for field_name, selectors in field_selectors.items():
                element = self.find_element_by_selectors(selectors)
                if element:
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(1)
                        element.clear()
                        time.sleep(0.5)
                        element.send_keys(field_data[field_name])
                        time.sleep(1)
                        print(f"✅ {field_name.replace('_', ' ').title()} filled successfully")
                        fields_filled += 1
                    except Exception as e:
                        print(f"❌ Failed to fill {field_name}: {e}")
                else:
                    print(f"❌ {field_name.replace('_', ' ').title()} field not found")

            print(f"📊 Fields filled: {fields_filled}/5")

            # Take screenshot before submit
            self.driver.save_screenshot("signup_before_submit.png")
            print("📸 Screenshot saved: signup_before_submit.png")

            # Find and click submit button
            print("🔘 Looking for submit button...")
            time.sleep(3)
            
            button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                '.submit-button',
                '.btn-submit',
                '.btn-primary'
            ]

            submit_button = self.find_element_by_selectors(button_selectors)

            if submit_button:
                try:
                    print("🎯 Attempting to click submit button...")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
                    time.sleep(2)
                    
                    wait.until(EC.element_to_be_clickable(submit_button))
                    time.sleep(1)
                    
                    # Try clicking
                    submit_button.click()
                    print("✅ Successfully clicked submit button")
                    
                    # Wait for response
                    print("⏳ Waiting for response...")
                    time.sleep(8)
                    
                    # Take screenshot after submit
                    self.driver.save_screenshot("signup_after_submit.png")
                    print("📸 Screenshot saved: signup_after_submit.png")
                    
                    success = True
                    print("✅ Registration submitted successfully!")
                    print("📧 Check email for verification link!")
                    
                except Exception as e:
                    print(f"❌ Failed to click submit button: {e}")
            else:
                print("❌ No submit button found!")
                self.driver.save_screenshot("signup_no_button_found.png")
                
            time.sleep(5)
                
        except Exception as e:
            print(f"❌ An error occurred during signup: {str(e)}")
            if self.driver:
                self.driver.save_screenshot("signup_error_screenshot.png")
        
        # Save signup information
        self.save_signup_info(first_name, last_name, email, password, success)
        return success

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
def register_account(self):
    """
    Main method to register an account - wrapper for the existing functionality
    Returns True if successful, False otherwise
    """
    print("🚀 Starting account registration process...")
    
    try:
        # Read email from file (created by previous step)
        email = self.read_email_from_file()
        if not email:
            print("❌ Could not read email address from file")
            return False
        
        # Generate random credentials with fixed password
        first_name, last_name, password = self.generate_random_credentials(email)
        
        print(f"📧 Email: {email}")
        print(f"👤 Name: {first_name} {last_name}")
        print(f"🔐 Password: {password}")
        print(f"🌐 Browser: {self.browser_type}")
        
        # Perform registration
        success = self.fill_registration_form(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            password_confirm=password
        )
        
        if success:
            print("🎉 Account registration completed successfully!")
            return True
        else:
            print("❌ Account registration failed")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup(self):
    """
    Cleanup method for proper resource management
    """
    print("🧹 Cleaning up resources...")
    self.close()

def main():
    """Main function for Jenkins integration"""
    print("🚀 Starting EmbyIL Registration Bot for Jenkins")
    print("=" * 60)
    
    bot = None
    try:
        # Initialize bot in headless mode for Jenkins
        bot = EmbyILRegistration(headless=True)
        
        # בדיקת משאבים
        bot.check_system_resources()
        
        # Read email from file (created by Jenkins pipeline)
        email = bot.read_email_from_file()
        if not email:
            print("❌ Could not read email address from file")
            sys.exit(1)
        
        # Generate random credentials with fixed password
        first_name, last_name, password = bot.generate_random_credentials(email)
        
        print(f"📧 Email: {email}")
        print(f"👤 Name: {first_name} {last_name}")
        print(f"🔐 Password: {password}")
        print(f"🌐 Browser: {bot.browser_type}")
        print()
        
        # Perform registration
        success = bot.fill_registration_form(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            password_confirm=password
        )
        
        if success:
            print("🎉 Registration completed successfully!")
            print(f"💡 Login credentials - Email: {email}, Password: {password}")
            sys.exit(0)
        else:
            print("⚠️ Registration completed with warnings")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        sys.exit(1)
    finally:
        if bot:
            bot.close()
        print("🏁 Script finished")

if __name__ == "__main__":
    main()
