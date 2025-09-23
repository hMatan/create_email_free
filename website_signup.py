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
        """Setup Chrome WebDriver with Docker-optimized options"""
        chrome_options = Options()

        # Essential options for headless/server environments
        if self.headless:
            chrome_options.add_argument("--headless=new")

        # Critical options for Docker environments - מתוקן
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")  # חיוני לDocker
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security") 
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # הגדרות נוספות לחיזוק היציבות
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI,VizDisplayCompositor")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # זיכרון ומעבדים מוגבלים
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")
        chrome_options.add_argument("--single-process")  # מפחית שימוש בזיכרון
        
        # רישום מפורט לטיפול בשגיאות
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_argument("--v=1")

        # Try multiple methods to initialize the driver
        methods = [
            self._try_selenium_manager,
            self._try_webdriver_manager,  
            self._try_system_chromedriver,
            self._try_manual_chromedriver_path
        ]

        for method in methods:
            try:
                self.driver = method(chrome_options)
                if self.driver:
                    print(f"✅ Successfully initialized WebDriver using {method.__name__}")
                    # בדיקה שהדרייבר עובד
                    self.driver.get("data:,")  # טעינת דף ריק לבדיקה
                    print("✅ WebDriver test successful - ready to proceed")
                    return
            except Exception as e:
                print(f"❌ Failed with {method.__name__}: {str(e)}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                continue

        raise Exception("All WebDriver initialization methods failed. Please check Docker memory limits and Chrome installation.")

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
            
            print
