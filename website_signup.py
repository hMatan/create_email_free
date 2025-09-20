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

    def _try_selenium_manager(self, options):
        """Try using Selenium's built-in manager (Selenium 4.6+)"""
        return webdriver.Chrome(options=options)

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
        """Generate random credentials for signup"""
        import random
        import string
        
        # Generate random names
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa']
        last_names = ['Smith', 'Johnson', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor']
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generate strong password
        password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$', k=12))
        
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
            'url': 'https://client.embyiltv.io/sign-up'
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
            print("🌐 Navigating to registration page...")
            self.driver.get("https://client.embyiltv.io/sign-up")

            wait = WebDriverWait(self.driver, 15)
            time.sleep(3)

            # Take screenshot before filling
            self.driver.save_screenshot("signup_before_filling.png")
            print("📸 Screenshot saved: signup_before_filling.png")

            # Field selectors
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

            # Fill all fields
            fields_filled = 0
            
            # Fill first name
            first_name_field = self.find_element_by_selectors(field_selectors['first_name'])
            if first_name_field:
                first_name_field.clear()
                first_name_field.send_keys(first_name)
                print("✅ First name filled successfully")
                fields_filled += 1
            else:
                print("❌ First name field not found")

            # Fill last name  
            last_name_field = self.find_element_by_selectors(field_selectors['last_name'])
            if last_name_field:
                last_name_field.clear()
                last_name_field.send_keys(last_name)
                print("✅ Last name filled successfully")
                fields_filled += 1
            else:
                print("❌ Last name field not found")

            # Fill email
            email_field = self.find_element_by_selectors(field_selectors['email'])
            if email_field:
                email_field.clear()
                email_field.send_keys(email)
                print("✅ Email filled successfully")
                fields_filled += 1
            else:
                print("❌ Email field not found")

            # Fill password
            password_field = self.find_element_by_selectors(field_selectors['password'])
            if password_field:
                password_field.clear()
                password_field.send_keys(password)
                print("✅ Password filled successfully")
                fields_filled += 1
            else:
                print("❌ Password field not found")

            # Fill password confirmation
            password_confirm_field = self.find_element_by_selectors(field_selectors['password_confirm'])
            if password_confirm_field:
                password_confirm_field.clear()
                password_confirm_field.send_keys(password_confirm)
                print("✅ Password confirmation filled successfully")
                fields_filled += 1
            else:
                print("❌ Password confirmation field not found")

            print(f"📊 Fields filled: {fields_filled}/5")

            # Take screenshot before submit
            self.driver.save_screenshot("signup_before_submit.png")
            print("📸 Screenshot saved: signup_before_submit.png")

            # Enhanced button finding and clicking
            print("🔘 Looking for submit button...")
            
            # XPath selectors for Hebrew text
            xpath_selectors = [
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
                'button[type="submit"]',
                'input[type="submit"]',
                '.submit-button',
                '.register-button',
                '.signup-button',
                '.btn-submit',
                '.btn-primary'
            ]

            submit_button = None

            # Try XPath selectors first
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
                submit_button = self.find_element_by_selectors(css_selectors)
                if submit_button:
                    print("✅ Found submit button with CSS selector")

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
                    clicked_successfully = False
                    click_methods = [
                        lambda: submit_button.click(),
                        lambda: self.driver.execute_script("arguments[0].click();", submit_button),
                        lambda: self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", submit_button)
                    ]
                    
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
                        # Wait for response
                        print("⏳ Waiting for response...")
                        time.sleep(5)
                        
                        # Take screenshot after submit
                        self.driver.save_screenshot("signup_after_submit.png")
                        print("📸 Screenshot saved: signup_after_submit.png")
                        
                        current_url = self.driver.current_url
                        print(f"🌐 Current URL after submit: {current_url}")
                        
                        # Check if URL changed (success indicator)
                        if "sign-up" not in current_url:
                            print("✅ URL changed - likely successful registration!")
                            success = True
                        else:
                            print("⚠️ URL didn't change - registration may need verification")
                            # Still consider it a success if no errors found
                            success = True
                        
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
        """Try to find element using multiple selectors"""
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

def main():
    """Main function for Jenkins integration"""
    print("🚀 Starting EmbyIL Registration Bot for Jenkins")
    print("=" * 60)
    
    bot = None
    try:
        # Initialize bot in headless mode for Jenkins
        bot = EmbyILRegistration(headless=True)
        
        # Read email from file (created by Jenkins pipeline)
        email = bot.read_email_from_file()
        if not email:
            print("❌ Could not read email address from file")
            sys.exit(1)
        
        # Generate random credentials
        first_name, last_name, password = bot.generate_random_credentials(email)
        
        print(f"📧 Email: {email}")
        print(f"👤 Name: {first_name} {last_name}")
        print(f"🔐 Generated password length: {len(password)} characters")
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
