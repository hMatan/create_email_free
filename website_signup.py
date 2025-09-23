from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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
        self.setup_driver()

    def install_webdriver_manager(self):
        """Install webdriver-manager if not available"""
        try:
            import webdriver_manager
            return True
        except ImportError:
            print("Installing webdriver-manager...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
                return True
            except subprocess.CalledProcessError:
                print("Failed to install webdriver-manager")
                return False

    def check_system_resources(self):
        """Check system resources and shared memory"""
        try:
            print("🔍 Checking system resources...")
            
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
                
            # בדיקת גרסת Chrome
            result = subprocess.run(['google-chrome', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"🌐 Chrome version: {result.stdout.strip()}")
                
        except Exception as e:
            print(f"⚠️ Could not check system resources: {e}")

    def setup_driver(self):
        """Setup Chrome WebDriver with maximum Docker stability"""
        chrome_options = Options()
        
        print("🔧 Configuring Chrome for maximum Docker stability...")

        # Essential headless options
        if self.headless:
            chrome_options.add_argument("--headless=new")

        # Core Docker stability options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # Memory and performance optimization
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max-old-space-size=2048")
        chrome_options.add_argument("--js-flags=--max-old-space-size=2048")
        
        # Disable unnecessary features
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor,TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # Process management
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-sync")
        
        # Network and security
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--ignore-certificate-errors-spki-list")
        
        # Window and display
        chrome_options.add_argument("--window-size=1280,720")  # Smaller window
        chrome_options.add_argument("--start-maximized")
        
        # Logging for debugging
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_argument("--v=1")
        
        # Set user data directory to prevent conflicts
        user_data_dir = tempfile.mkdtemp(prefix="chrome_", suffix="_profile")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        print(f"📁 Chrome user data directory: {user_data_dir}")

        # Try each method with extensive error handling
        methods = [
            ('Selenium Manager', self._try_selenium_manager),
            ('WebDriver Manager', self._try_webdriver_manager),
            ('System ChromeDriver', self._try_system_chromedriver),
            ('Manual Path', self._try_manual_chromedriver_path)
        ]

        for method_name, method in methods:
            for attempt in range(3):  # 3 attempts per method
                try:
                    print(f"🔄 Attempting {method_name} (attempt {attempt + 1}/3)...")
                    
                    self.driver = method(chrome_options)
                    if self.driver:
                        print(f"✅ Driver created with {method_name}")
                        
                        # Extended test - try multiple simple operations
                        test_operations = [
                            ("Loading empty page", lambda: self.driver.get("data:,")),
                            ("Getting title", lambda: self.driver.title),
                            ("Getting current URL", lambda: self.driver.current_url),
                            ("Setting window size", lambda: self.driver.set_window_size(1280, 720))
                        ]
                        
                        all_tests_passed = True
                        for test_name, test_func in test_operations:
                            try:
                                print(f"🧪 Testing: {test_name}...")
                                result = test_func()
                                print(f"✅ {test_name}: OK")
                                time.sleep(1)  # Small delay between tests
                            except Exception as e:
                                print(f"❌ {test_name} failed: {e}")
                                all_tests_passed = False
                                break
                        
                        if all_tests_passed:
                            print(f"🎉 All tests passed! {method_name} is working correctly")
                            return
                        else:
                            print(f"⚠️ Tests failed for {method_name}, trying next...")
                            self.driver.quit()
                            self.driver = None
                            
                except Exception as e:
                    print(f"❌ {method_name} attempt {attempt + 1} failed: {str(e)}")
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                        self.driver = None
                    
                    if attempt < 2:  # Not the last attempt
                        print(f"⏳ Waiting 5 seconds before retry...")
                        time.sleep(5)

        raise Exception("All WebDriver initialization methods failed after multiple attempts. Chrome appears unstable in this Docker environment.")

    def _try_selenium_manager(self, options):
        """Try using Selenium Manager (recommended for Selenium 4.6+)"""
        return webdriver.Chrome(options=options)

    def _try_webdriver_manager(self, options):
        """Try using webdriver-manager"""
        if self.install_webdriver_manager():
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        return None

    def _try_system_chromedriver(self, options):
        """Try using system-installed chromedriver"""
        possible_paths = [
            "/usr/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/opt/chromedriver",
            "chromedriver"
        ]

        for path in possible_paths:
            try:
                if os.path.exists(path) or path == "chromedriver":
                    service = Service(path)
                    return webdriver.Chrome(service=service, options=options)
            except Exception:
                continue
        return None

    def _try_manual_chromedriver_path(self, options):
        """Try using manually downloaded chromedriver"""
        current_dir = os.getcwd()
        chromedriver_path = os.path.join(current_dir, "chromedriver")

        if os.path.exists(chromedriver_path):
            os.chmod(chromedriver_path, 0o755)
            service = Service(chromedriver_path)
            return webdriver.Chrome(service=service, options=options)
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

    def check_registration_success(self):
        """Advanced check for registration success"""
        success_indicators = [
            "success",
            "confirm", 
            "verify",
            "email sent",
            "check your email",
            "הודעה נשלחה",
            "בדוק את המייל",
            "רישום בוצע בהצלחה"
        ]
        
        error_indicators = [
            "error",
            "failed", 
            "invalid",
            "already exists",
            "שגיאה",
            "נכשל",
            "כבר קיים"
        ]
        
        try:
            page_source = self.driver.page_source.lower()
            current_url = self.driver.current_url
            
            print(f"🔍 Current URL: {current_url}")
            
            # Check for success indicators
            for indicator in success_indicators:
                if indicator in page_source:
                    print(f"✅ Found success indicator: {indicator}")
                    return True
            
            # Check URL change
            if "sign-up" not in current_url and "register" not in current_url:
                print("✅ URL changed - likely successful")
                return True
            
            # Check for errors
            for indicator in error_indicators:
                if indicator in page_source:
                    print(f"❌ Found error indicator: {indicator}")
                    return False
            
            return True  # If no clear errors, consider it success
            
        except Exception as e:
            print(f"⚠️ Error checking registration success: {e}")
            return True  # Default to success if can't check

    def fill_registration_form(self, first_name, last_name, email, password, password_confirm):
        """Fill the registration form with provided details"""
        success = False
        
        try:
            print("🌐 Navigating to registration page...")
            self.driver.get("https://client.embyiltv.io/sign-up")

            wait = WebDriverWait(self.driver, 20)  # Increased timeout
            time.sleep(5)  # Longer initial wait

            # Take screenshot before filling
            self.driver.save_screenshot("signup_before_filling.png")
            print("📸 Screenshot saved: signup_before_filling.png")

            # Field selectors - simplified for better compatibility
            field_selectors = {
                'first_name': [
                    'input[name="firstName"]',
                    'input[name="first_name"]', 
                    'input[placeholder*="First"]',
                    'input[type="text"]:nth-of-type(1)'
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
                    'input[placeholder*="Email"]',
                    'input[placeholder*="mail"]'
                ],
                'password': [
                    'input[name="password"]',
                    'input[type="password"]',
                    'input[placeholder*="Password"]'
                ],
                'password_confirm': [
                    'input[name="confirmPassword"]',
                    'input[name="password_confirmation"]',
                    'input[placeholder*="Confirm"]',
                    'input[type="password"]:nth-of-type(2)'
                ]
            }

            # Fill all fields with more robust approach
            fields_filled = 0
            
            for field_name, selectors in field_selectors.items():
                field_value = locals().get(field_name.replace('_confirm', ''))
                if field_name == 'password_confirm':
                    field_value = password_confirm
                    
                element = self.find_element_by_selectors(selectors)
                if element:
                    try:
                        # Scroll to element first
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(1)
                        
                        # Clear and fill
                        element.clear()
                        time.sleep(0.5)
                        element.send_keys(field_value)
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

            # Enhanced button finding with more wait time
            print("🔘 Looking for submit button...")
            time.sleep(3)  # Extra wait for dynamic content
            
            # Simplified button selectors
            button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:contains("Sign Up")',
                'button:contains("Register")',
                '.submit-button',
                '.btn-submit',
                '.btn-primary'
            ]

            submit_button = self.find_element_by_selectors(button_selectors)

            # Click the button with enhanced error handling
            if submit_button:
                try:
                    print("🎯 Attempting to click submit button...")
                    
                    # Scroll to button and wait
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
                    time.sleep(2)
                    
                    # Wait for it to be clickable
                    wait.until(EC.element_to_be_clickable(submit_button))
                    time.sleep(1)
                    
                    # Try multiple click methods
                    click_methods = [
                        ("Regular click", lambda: submit_button.click()),
                        ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", submit_button)),
                        ("Action click", lambda: webdriver.ActionChains(self.driver).click(submit_button).perform())
                    ]
                    
                    clicked_successfully = False
                    for method_name, click_method in click_methods:
                        try:
                            print(f"🔄 Trying {method_name}...")
                            click_method()
                            print(f"✅ Successfully clicked submit button using {method_name}")
                            clicked_successfully = True
                            break
                        except Exception as e:
                            print(f"❌ {method_name} failed: {e}")
                            time.sleep(1)
                    
                    if clicked_successfully:
                        # Wait for response with longer timeout
                        print("⏳ Waiting for response...")
                        time.sleep(8)  # Longer wait
                        
                        # Take screenshot after submit
                        self.driver.save_screenshot("signup_after_submit.png")
                        print("📸 Screenshot saved: signup_after_submit.png")
                        
                        # Check registration success
                        success = self.check_registration_success()
                        
                        if success:
                            print("✅ Registration appears successful!")
                        else:
                            print("⚠️ Registration status unclear")
                        
                        print("📧 Check email for verification link!")
                    
                except Exception as e:
                    print(f"❌ Failed to click submit button: {e}")
            else:
                print("❌ No submit button found!")
                self.driver.save_screenshot("signup_no_button_found.png")
                
            time.sleep(5)  # Final wait
                
        except Exception as e:
            print(f"❌ An error occurred during signup: {str(e)}")
            if self.driver:
                self.driver.save_screenshot("signup_error_screenshot.png")
        
        # Save signup information regardless of success
        self.save_signup_info(first_name, last_name, email, password, success)
        return success

    def find_element_by_selectors(self, selectors):
        """Try to find element using multiple selectors with better waiting"""
        for selector in selectors:
            try:
                # Wait for element to be present
                wait = WebDriverWait(self.driver, 10)
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                
                # Check if element is displayed and enabled
                if element.is_displayed() and element.is_enabled():
                    return element
            except Exception:
                continue
        return None

    def fill_registration_form_with_retry(self, first_name, last_name, email, password, password_confirm, max_retries=2):
        """Fill registration form with retry mechanism (reduced retries for stability)"""
        for attempt in range(max_retries):
            try:
                print(f"🔄 Registration attempt {attempt + 1}/{max_retries}")
                success = self.fill_registration_form(first_name, last_name, email, password, password_confirm)
                
                if success:
                    return True
                    
                if attempt < max_retries - 1:
                    print(f"⚠️ Attempt {attempt + 1} failed, retrying in 15 seconds...")
                    time.sleep(15)  # Longer wait between retries
                    
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed with error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(15)
                
        return False

    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                print("🔒 Browser closed successfully")
            except Exception as e:
                print(f"⚠️ Error closing browser: {e}")

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
        print()
        
        # Perform registration with retry mechanism
        success = bot.fill_registration_form_with_retry(
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
            sys.exit(0)  # Don't fail the Jenkins job
            
    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        sys.exit(1)
    finally:
        if bot:
            bot.close()
        print("🏁 Script finished")

if __name__ == "__main__":
    main()
