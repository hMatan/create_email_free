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
import getpass

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

    def setup_driver(self):
        """Setup Chrome WebDriver with multiple fallback options"""
        chrome_options = Options()

        # Essential options for headless/server environments
        if self.headless:
            chrome_options.add_argument("--headless")

        # Critical options for Linux/Synology environments
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")

        # Try multiple methods to initialize the driver
        methods = [
            self._try_webdriver_manager,
            self._try_system_chromedriver,
            self._try_manual_chromedriver_path,
            self._try_selenium_manager
        ]

        for method in methods:
            try:
                self.driver = method(chrome_options)
                if self.driver:
                    print(f"Successfully initialized WebDriver using {method.__name__}")
                    return
            except Exception as e:
                print(f"Failed with {method.__name__}: {str(e)}")
                continue

        raise Exception("All WebDriver initialization methods failed. Please install Chrome and ChromeDriver manually.")

    def _try_webdriver_manager(self, options):
        """Try using webdriver-manager"""
        if self.install_webdriver_manager():
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        return None

    def _try_system_chromedriver(self, options):
        """Try using system-installed chromedriver"""
        # Common chromedriver locations on Linux
        possible_paths = [
            "/usr/bin/chromedriver",
            "/usr/local/bin/chromedriver",
            "/opt/chromedriver",
            "chromedriver"  # if in PATH
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
        # Check current directory for chromedriver
        current_dir = os.getcwd()
        chromedriver_path = os.path.join(current_dir, "chromedriver")

        if os.path.exists(chromedriver_path):
            # Make sure it's executable
            os.chmod(chromedriver_path, 0o755)
            service = Service(chromedriver_path)
            return webdriver.Chrome(service=service, options=options)
        return None

    def _try_selenium_manager(self, options):
        """Try using Selenium's built-in manager (Selenium 4.6+)"""
        # This should work with newer Selenium versions
        return webdriver.Chrome(options=options)

    def download_chromedriver(self):
        """Download chromedriver manually if needed"""
        import urllib.request
        import zipfile
        import platform

        system = platform.system().lower()
        arch = platform.machine()

        if system == "linux":
            if "64" in arch:
                url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip"
            else:
                url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux32.zip"
        else:
            print(f"Unsupported system: {system}")
            return False

        try:
            print("Downloading chromedriver...")
            urllib.request.urlretrieve(url, "chromedriver.zip")

            with zipfile.ZipFile("chromedriver.zip", 'r') as zip_ref:
                zip_ref.extract("chromedriver")

            os.chmod("chromedriver", 0o755)
            os.remove("chromedriver.zip")
            print("ChromeDriver downloaded successfully")
            return True
        except Exception as e:
            print(f"Failed to download chromedriver: {str(e)}")
            return False

    def fill_registration_form(self, first_name, last_name, email, password, password_confirm):
        """
        Fill the registration form with provided details
        
        Args:
            first_name (str): First name
            last_name (str): Last name  
            email (str): Email address
            password (str): Password
            password_confirm (str): Password confirmation
        """
        try:
            # Navigate to the registration page
            print("🌐 Navigating to registration page...")
            self.driver.get("https://client.embyiltv.io/sign-up")

            # Wait for the page to load
            wait = WebDriverWait(self.driver, 15)
            time.sleep(3)

            # Take screenshot before filling (for debugging)
            self.driver.save_screenshot("before_filling.png")
            print("📸 Screenshot saved: before_filling.png")

            # Common field selectors to try
            field_selectors = {
                'first_name': [
                    'input[name="firstName"]',
                    'input[name="first_name"]', 
                    'input[id*="first"]',
                    'input[placeholder*="שם פרטי"]',
                    'input[placeholder*="First Name"]',
                    'input[placeholder*="First"]',
                    'input[type="text"]:nth-of-type(1)'
                ],
                'last_name': [
                    'input[name="lastName"]',
                    'input[name="last_name"]',
                    'input[id*="last"]', 
                    'input[placeholder*="שם משפחה"]',
                    'input[placeholder*="Last Name"]',
                    'input[placeholder*="Last"]',
                    'input[type="text"]:nth-of-type(2)'
                ],
                'email': [
                    'input[name="email"]',
                    'input[type="email"]',
                    'input[id*="email"]',
                    'input[placeholder*="אימייל"]',
                    'input[placeholder*="Email"]',
                    'input[placeholder*="mail"]'
                ],
                'password': [
                    'input[name="password"]',
                    'input[type="password"]',
                    'input[id*="password"]',
                    'input[placeholder*="סיסמה"]',
                    'input[placeholder*="Password"]'
                ],
                'password_confirm': [
                    'input[name="password1"]',
                    'input[name="confirmPassword"]',
                    'input[name="password_confirmation"]',
                    'input[name="confirm_password"]',
                    'input[id*="password1"]',
                    'input[id*="confirm"]',
                    'input[placeholder*="אישור סיסמה"]',
                    'input[placeholder*="Confirm Password"]',
                    'input[placeholder*="Repeat Password"]',
                    'input[type="password"]:nth-of-type(2)'
                ]
            }

            # Fill first name
            print("📝 Filling first name...")
            first_name_field = self.find_element_by_selectors(field_selectors['first_name'])
            if first_name_field:
                first_name_field.clear()
                first_name_field.send_keys(first_name)
                print("✅ First name filled successfully")
            else:
                print("❌ First name field not found")

            # Fill last name  
            print("📝 Filling last name...")
            last_name_field = self.find_element_by_selectors(field_selectors['last_name'])
            if last_name_field:
                last_name_field.clear()
                last_name_field.send_keys(last_name)
                print("✅ Last name filled successfully")
            else:
                print("❌ Last name field not found")

            # Fill email
            print("📝 Filling email...")
            email_field = self.find_element_by_selectors(field_selectors['email'])
            if email_field:
                email_field.clear()
                email_field.send_keys(email)
                print("✅ Email filled successfully")
            else:
                print("❌ Email field not found")

            # Fill password
            print("📝 Filling password...")
            password_field = self.find_element_by_selectors(field_selectors['password'])
            if password_field:
                password_field.clear()
                password_field.send_keys(password)
                print("✅ Password filled successfully")
            else:
                print("❌ Password field not found")

            # Fill password confirmation
            print("📝 Filling password confirmation...")
            password_confirm_field = self.find_element_by_selectors(field_selectors['password_confirm'])
            if password_confirm_field:
                password_confirm_field.clear()
                password_confirm_field.send_keys(password_confirm)
                print("✅ Password confirmation filled successfully")
            else:
                print("❌ Password confirmation field not found")

            # Check for any error messages before submitting
            print("🔍 Checking for pre-submit errors...")
            error_selectors = [
                '.error',
                '.error-message', 
                '[class*="error"]',
                '.alert-danger',
                '.validation-error',
                '.field-error',
                '.invalid-feedback',
                '.form-error'
            ]
            
            for selector in error_selectors:
                try:
                    errors = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if errors:
                        for error in errors:
                            if error.is_displayed() and error.text.strip():
                                print(f"⚠️ Pre-submit error found: {error.text}")
                except:
                    continue

            # Take screenshot before clicking submit
            self.driver.save_screenshot("before_submit.png")
            print("📸 Screenshot saved: before_submit.png")

            # Enhanced button finding and clicking
            print("🔘 Looking for submit button...")

            # First, let's see what buttons are available
            print("🔍 Scanning all buttons on page...")
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            all_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit'], input[type='button']")

            print(f"Found {len(all_buttons)} buttons and {len(all_inputs)} input buttons")

            for i, element in enumerate(all_buttons + all_inputs):
                try:
                    if element.is_displayed():
                        text = element.text or element.get_attribute('value') or 'No text'
                        classes = element.get_attribute('class') or ''
                        data_slot = element.get_attribute('data-slot') or ''
                        print(f"   Button {i+1}: '{text}' | class='{classes}' | data-slot='{data_slot}'")
                except:
                    pass

            # Enhanced button selectors
            xpath_selectors = [
                # XPath for Hebrew text
                "//button[contains(text(), 'הרשמה')]",
                "//input[@value='הרשמה']",
                "//button[contains(text(), 'רישום')]",
                "//input[@value='רישום']",
                "//button[contains(text(), 'Sign Up')]",
                "//button[contains(text(), 'Register')]",
                "//button[contains(text(), 'Submit')]"
            ]

            css_selectors = [
                '[data-slot="button"]',
                'button[data-slot="button"]', 
                'input[data-slot="button"]',
                'button[type="submit"]',
                'input[type="submit"]',
                '.submit-button',
                '.register-button',
                '.signup-button',
                '.btn-submit',
                '.btn-primary'
            ]

            submit_button = None

            # Try XPath selectors for Hebrew text
            for selector in xpath_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            submit_button = element
                            print(f"✅ Found submit button with XPath: {selector}")
                            break
                    if submit_button:
                        break
                except:
                    continue

            # Try CSS selectors if XPath failed
            if not submit_button:
                for selector in css_selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if element.is_displayed():
                            submit_button = element
                            print(f"✅ Found submit button with CSS: {selector}")
                            break
                    except:
                        continue

            # If still not found, try brute force on all buttons
            if not submit_button:
                print("⚡ Brute force searching for submit button...")
                all_clickable = self.driver.find_elements(By.CSS_SELECTOR, "button, input[type='submit'], input[type='button']")
                
                for element in all_clickable:
                    try:
                        if element.is_displayed():
                            text = (element.text or element.get_attribute('value') or '').strip()
                            data_slot = element.get_attribute('data-slot') or ''
                            
                            if ('הרשמה' in text or 'רישום' in text or 
                                'submit' in text.lower() or 'register' in text.lower() or
                                data_slot == 'button'):
                                submit_button = element
                                print(f"✅ Found button by brute force: '{text}'")
                                break
                    except:
                        continue

            # Click the button
            if submit_button:
                try:
                    print("🎯 Attempting to click submit button...")
                    
                    # Scroll to button
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
                    time.sleep(1)
                    
                    # Wait for it to be clickable
                    wait.until(EC.element_to_be_clickable(submit_button))
                    
                    # Try multiple click methods
                    click_methods = [
                        lambda: submit_button.click(),
                        lambda: self.driver.execute_script("arguments[0].click();", submit_button),
                        lambda: self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", submit_button)
                    ]
                    
                    clicked_successfully = False
                    for i, click_method in enumerate(click_methods):
                        try:
                            click_method()
                            print(f"✅ Successfully clicked submit button using method {i+1}")
                            clicked_successfully = True
                            break
                        except Exception as e:
                            print(f"❌ Click method {i+1} failed: {e}")
                            if i < len(click_methods) - 1:
                                time.sleep(1)
                    
                    if clicked_successfully:
                        # Wait and check for response
                        print("⏳ Waiting for response...")
                        time.sleep(5)
                        
                        # Check for success messages
                        success_selectors = [
                            '.success',
                            '.success-message',
                            '[class*="success"]',
                            '.alert-success',
                            '.confirmation',
                            '.thank-you',
                            '.registration-success'
                        ]
                        
                        success_found = False
                        for selector in success_selectors:
                            try:
                                success_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                if success_elements:
                                    for element in success_elements:
                                        if element.is_displayed() and element.text.strip():
                                            print(f"✅ Success message: {element.text}")
                                            success_found = True
                            except:
                                continue
                        
                        # Check for error messages after submit
                        print("🔍 Checking for post-submit errors...")
                        for selector in error_selectors:
                            try:
                                errors = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                if errors:
                                    for error in errors:
                                        if error.is_displayed() and error.text.strip():
                                            print(f"❌ Post-submit error: {error.text}")
                            except:
                                continue

                        # Take screenshot after submit
                        self.driver.save_screenshot("after_submit.png")
                        print("📸 Screenshot saved: after_submit.png")
                        
                        print(f"🌐 Current URL after submit: {self.driver.current_url}")
                        
                        # Check if URL changed (might indicate successful submission)
                        current_url = self.driver.current_url
                        if "sign-up" not in current_url:
                            print("✅ URL changed - likely successful registration!")
                            success_found = True
                            
                        if not success_found:
                            print("⚠️ No clear success message found. Check screenshots for visual confirmation.")
                            print("💡 The registration might still be successful - check your email!")
                        
                        print("📧 Important: Check your email (including spam folder) for verification!")
                        print("⏰ Verification emails can take up to 15 minutes to arrive.")
                    
                except Exception as e:
                    print(f"❌ Failed to click submit button: {e}")
            else:
                print("❌ No submit button found!")
                print("📄 Taking screenshot for debugging...")
                self.driver.save_screenshot("no_button_found.png")
                
            time.sleep(10)  # Wait longer to see results
                
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}")
            if self.driver:
                print("Current URL:", self.driver.current_url)
                self.driver.save_screenshot("error_screenshot.png")
                print("📸 Error screenshot saved: error_screenshot.png")

    def find_element_by_selectors(self, selectors):
        """
        Try to find element using multiple selectors
        
        Args:
            selectors (list): List of CSS selectors to try
            
        Returns:
            WebElement or None: Found element or None if not found
        """
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except:
                continue
        return None

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

# Installation helper function
def install_chrome_and_chromedriver():
    """Helper function to install Chrome and ChromeDriver on Linux"""
    print("To fix the ChromeDriver issue, run these commands on your Synology/Linux system:")
    print()
    print("1. Install Google Chrome:")
    print("   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -")
    print("   echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list")
    print("   sudo apt update")
    print("   sudo apt install google-chrome-stable")
    print()
    print("2. Install ChromeDriver:")
    print("   wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip")
    print("   unzip chromedriver_linux64.zip")
    print("   sudo mv chromedriver /usr/local/bin/")
    print("   sudo chmod +x /usr/local/bin/chromedriver")
    print()
    print("3. Install webdriver-manager (alternative):")
    print("   pip3 install webdriver-manager")

def get_user_input():
    """Get registration details from user input"""
    print("=" * 60)
    print("🚀 EmbyIL Registration Bot - Enhanced Version with Button Fix")
    print("=" * 60)
    print()
    
    # Get user input
    first_name = input("Enter your first name (שם פרטי): ").strip()
    while not first_name:
        first_name = input("❌ First name cannot be empty. Please enter your first name: ").strip()
    
    last_name = input("Enter your last name (שם משפחה): ").strip()
    while not last_name:
        last_name = input("❌ Last name cannot be empty. Please enter your last name: ").strip()
    
    email = input("Enter your email address (אימייל): ").strip()
    while not email or '@' not in email or '.' not in email:
        email = input("❌ Please enter a valid email address: ").strip()
    
    # Use getpass for password to hide input
    password = getpass.getpass("Enter your password (סיסמה): ")
    while not password or len(password) < 6:
        password = getpass.getpass("❌ Password must be at least 6 characters. Please enter your password: ")
    
    password_confirm = getpass.getpass("Confirm your password (אישור סיסמה): ")
    while password_confirm != password:
        print("❌ Passwords do not match!")
        password_confirm = getpass.getpass("Please confirm your password again: ")
    
    # Ask for headless mode
    print()
    headless_choice = input("Run in headless mode? (no browser window) [Y/n]: ").strip().lower()
    headless = headless_choice != 'n'
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': password,
        'password_confirm': password_confirm,
        'headless': headless
    }

# Example usage
if __name__ == "__main__":
    try:
        # Get user input
        user_data = get_user_input()
        
        print()
        print("🔄 Starting registration process...")
        print(f"📧 Email: {user_data['email']}")
        print(f"👤 Name: {user_data['first_name']} {user_data['last_name']}")
        print(f"🖥️  Headless mode: {'Yes' if user_data['headless'] else 'No'}")
        print()
        
        # Create an instance of the registration bot
        bot = EmbyILRegistration(headless=user_data['headless'])
        
        # Fill the form with user details
        bot.fill_registration_form(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            password=user_data['password'],
            password_confirm=user_data['password_confirm']
        )
        
        print()
        print("🎉 Registration process completed!")
        print()
        print("📋 Next Steps:")
        print("1. 📧 Check your email inbox (including spam/junk folder)")
        print("2. 🔍 Look for an email from EmbyIL or embyiltv.io")
        print("3. ⏰ Wait up to 15 minutes for the email to arrive")
        print("4. 📱 Click the verification link in the email")
        print("5. 🔑 Your account will be activated after verification")
        print()
        print("💡 If you don't receive the email:")
        print("   - Check all email folders (spam, promotions, etc.)")
        print("   - Verify the email address is correct")
        print("   - Try registering with a different email provider")
        print("   - Contact EmbyIL support if the issue persists")
        print()
        print("⏳ Keeping browser open for 15 seconds...")
        time.sleep(15)
        
    except KeyboardInterrupt:
        print("\n❌ Process interrupted by user")
    except Exception as e:
        print(f"❌ Script failed: {str(e)}")
        print("\n🔧 Trying to help with installation...")
        install_chrome_and_chromedriver()
        
        # Try to download chromedriver
        try:
            temp_bot = EmbyILRegistration.__new__(EmbyILRegistration)
            if temp_bot.download_chromedriver():
                print("✅ ChromeDriver downloaded. Please run the script again.")
        except:
            pass
    finally:
        # Always close the browser
        try:
            if 'bot' in locals():
                bot.close()
        except:
            pass
        print("🏁 Script finished")
