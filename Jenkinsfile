pipeline {
    agent any
    
    // Schedule the pipeline to run every 3 days
    triggers {
        cron('H H */3 * *')  // Runs every 3 days
    }
    
    environment {
        // Define workspace paths
        PYTHON_PATH = '/usr/bin/python3'
        WORKSPACE_DIR = "${WORKSPACE}"
        
        // Email configuration (if you want notifications)
        EMAIL_RECIPIENTS = 'your-email@example.com'  // Change this
        
        // Temp email configuration
        TEMP_EMAIL_FILE = 'email_info.txt'
        MESSAGE_IDS_FILE = 'message_ids.txt'
        SIGNUP_FILE = 'signup_info.json'
        ACTIVATION_FILE = 'activation_info.json'
        USER_CREDENTIALS_FILE = 'user.password.txt'
        
        // Archive paths for artifacts
        ARTIFACTS_PATTERN = '*.txt,*.json,message_details_*.json,signup_*.json,activation_*.json,user.password.txt'
    }
    
    options {
        // Keep builds for 30 days or max 50 builds
        buildDiscarder(logRotator(daysToKeepStr: '30', numToKeepStr: '50'))
        
        // Set build timeout to 45 minutes (increased for activation step)
        timeout(time: 45, unit: 'MINUTES')
        
        // Disable concurrent builds
        disableConcurrentBuilds()
        
        // Add timestamps to console output
        timestamps()
    }
    
    stages {
        stage('Setup Environment') {
            steps {
                script {
                    echo "🚀 Starting Complete Email & Signup & Activation Pipeline"
                    echo "📅 Build Date: ${new Date()}"
                    echo "🔢 Build Number: ${BUILD_NUMBER}"
                    echo "📂 Workspace: ${WORKSPACE_DIR}"
                    echo "🐳 Running in Jenkins Docker container"
                }
                
                // Clean up old files from previous runs
                sh '''
                    echo "🧹 Cleaning up old files (older than 2 hours)..."
                    
                    # Delete old summary files
                    find . -name "complete_pipeline_summary_*.txt" -mmin +120 -delete || true
                    find . -name "build_*_summary_*.txt" -mmin +120 -delete || true
                    
                    # Delete old signup files
                    find . -name "signup_*.json" -mmin +120 -delete || true
                    find . -name "signup_*.png" -mmin +120 -delete || true
                    
                    # Delete old activation files
                    find . -name "activation_*.json" -mmin +120 -delete || true
                    find . -name "activation_*.png" -mmin +120 -delete || true
                    
                    # Delete old credentials files
                    find . -name "user.password.txt" -mmin +120 -delete || true
                    
                    # Delete old message details files
                    find . -name "message_details_*.json" -mmin +120 -delete || true
                    
                    # Delete old screenshots
                    find . -name "*.png" -mmin +120 -delete || true
                    
                    # Delete old log files
                    find . -name "*.log" -mmin +120 -delete || true
                    
                    echo "✅ Old files cleaned"
                    echo "📁 Current files:"
                    ls -la *.txt *.json *.png 2>/dev/null || echo "No artifacts yet - starting fresh"
                '''
            }
        }
        
        stage('Check Python Scripts') {
            steps {
                script {
                    echo "📋 Checking if Python scripts exist..."
                }
                
                sh '''
                    if [ ! -f "create_email.py" ]; then
                        echo "❌ create_email.py not found!"
                        exit 1
                    fi
                    
                    if [ ! -f "check_messages.py" ]; then
                        echo "❌ check_messages.py not found!"
                        exit 1
                    fi
                    
                    if [ ! -f "get_message_details.py" ]; then
                        echo "❌ get_message_details.py not found!"
                        exit 1
                    fi
                    
                    if [ ! -f "website_signup.py" ]; then
                        echo "❌ website_signup.py not found!"
                        exit 1
                    fi
                    
                    if [ ! -f "activate_account.py" ]; then
                        echo "❌ activate_account.py not found!"
                        exit 1
                    fi
                    
                    echo "✅ All Python scripts found"
                    echo "🐍 Python version: $(${PYTHON_PATH} --version 2>&1 || echo 'Python not found')"
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                script {
                    echo "📦 Installing Python dependencies inside Docker container..."
                }
                
                sh '''
                    echo "🔧 Installing Python packages directly (no sudo needed in container)..."
                    
                    # Update PATH to include user-installed packages
                    export PATH="$HOME/.local/bin:$PATH"
                    export PYTHONPATH="$HOME/.local/lib/python3.11/site-packages:$PYTHONPATH"
                    
                    # Method 1: Try using existing pip3
                    if command -v pip3 >/dev/null 2>&1; then
                        echo "✅ Found pip3, installing packages..."
                        PIP_CMD="pip3"
                    elif ${PYTHON_PATH} -m pip --version >/dev/null 2>&1; then
                        echo "✅ Found python -m pip, installing packages..."
                        PIP_CMD="${PYTHON_PATH} -m pip"
                    else
                        # Method 2: Install pip first
                        echo "📥 Installing pip using ensurepip..."
                        ${PYTHON_PATH} -m ensurepip --upgrade --user || echo "⚠️ ensurepip failed"
                        
                        # Method 3: Download get-pip.py
                        if ! ${PYTHON_PATH} -m pip --version >/dev/null 2>&1; then
                            echo "📥 Downloading get-pip.py..."
                            curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py || wget -q https://bootstrap.pypa.io/get-pip.py || echo "⚠️ Could not download get-pip"
                            
                            if [ -f get-pip.py ]; then
                                ${PYTHON_PATH} get-pip.py --user || echo "⚠️ get-pip failed"
                                rm -f get-pip.py
                            fi
                        fi
                        
                        # Determine final pip command
                        if command -v pip3 >/dev/null 2>&1; then
                            PIP_CMD="pip3"
                        elif ${PYTHON_PATH} -m pip --version >/dev/null 2>&1; then
                            PIP_CMD="${PYTHON_PATH} -m pip"
                        else
                            echo "❌ Could not install pip"
                            PIP_CMD="echo 'No pip available'"
                        fi
                    fi
                    
                    # Install packages if pip is available
                    if [ "$PIP_CMD" != "echo 'No pip available'" ]; then
                        echo "📦 Installing packages with: $PIP_CMD"
                        
                        # Try --user flag first, then without
                        echo "📈 Upgrading pip..."
                        $PIP_CMD install --upgrade pip --user 2>/dev/null || $PIP_CMD install --upgrade pip 2>/dev/null || echo "⚠️ pip upgrade failed"
                        
                        echo "📦 Installing selenium..."
                        $PIP_CMD install selenium --user 2>/dev/null || $PIP_CMD install selenium 2>/dev/null || echo "⚠️ selenium install failed"
                        
                        echo "📦 Installing webdriver-manager..."
                        $PIP_CMD install webdriver-manager --user 2>/dev/null || $PIP_CMD install webdriver-manager 2>/dev/null || echo "⚠️ webdriver-manager install failed"
                        
                        echo "📦 Installing additional packages..."
                        $PIP_CMD install requests urllib3 --user 2>/dev/null || $PIP_CMD install requests urllib3 2>/dev/null || echo "⚠️ additional packages install failed"
                        
                    else
                        echo "❌ No pip available for package installation"
                    fi
                    
                    # Update PATH to include user-installed packages
                    export PATH="$HOME/.local/bin:$PATH"
                    
                    # Verify installation
                    echo "🔍 Verifying installations..."
                    
                    ${PYTHON_PATH} -c "
import sys
import os

# Add user site-packages to path
import site
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

selenium_ok = False
webdriver_ok = False
requests_ok = False

try:
    import selenium
    print(f'✅ Selenium {selenium.__version__} available')
    selenium_ok = True
except ImportError as e:
    print(f'❌ Selenium not available: {e}')

try:
    import webdriver_manager
    print('✅ webdriver-manager available')
    webdriver_ok = True
except ImportError as e:
    print(f'❌ webdriver-manager not available: {e}')

try:
    import requests
    print('✅ requests available')
    requests_ok = True
except ImportError as e:
    print(f'❌ requests not available: {e}')

if selenium_ok and webdriver_ok:
    print('🎉 All required packages installed successfully!')
else:
    print('⚠️ Some packages missing, but continuing...')
    
print(f'Python executable: {sys.executable}')
print(f'Python path: {sys.path}')
"
                    
                    # Verify browsers
                    echo "🔍 Checking available browsers:"
                    if command -v google-chrome >/dev/null 2>&1; then
                        echo "✅ Chrome: $(google-chrome --version 2>/dev/null || echo 'installed')"
                    else
                        echo "⚠️ Chrome not found in PATH"
                    fi
                    
                    if command -v firefox-esr >/dev/null 2>&1; then
                        echo "✅ Firefox: $(firefox-esr --version 2>/dev/null || echo 'installed')"
                    else
                        echo "⚠️ Firefox not found in PATH"
                    fi
                    
                    # Check shared memory size
                    echo "💾 Checking shared memory:"
                    df -h /dev/shm 2>/dev/null || echo "⚠️ Could not check /dev/shm"
                    
                    echo "✅ Dependencies installation completed"
                '''
            }
        }
        
        stage('Step 1: Create/Verify Temp Email') {
            steps {
                script {
                    echo "📧 Step 1: Creating or verifying temporary email..."
                }
                
                sh '''
                    # Check if email_info.txt exists and is recent (less than 8 minutes old)
                    if [ -f "${TEMP_EMAIL_FILE}" ] && [ $(find "${TEMP_EMAIL_FILE}" -mmin -8 | wc -l) -gt 0 ]; then
                        echo "✅ Using existing temporary email (still valid)"
                        cat "${TEMP_EMAIL_FILE}"
                    else
                        echo "🆕 Creating new temporary email..."
                        ${PYTHON_PATH} create_email.py
                        
                        if [ $? -eq 0 ]; then
                            echo "✅ Temporary email created successfully"
                        else
                            echo "❌ Failed to create temporary email"
                            exit 1
                        fi
                    fi
                '''
            }
            
            post {
                success {
                    archiveArtifacts artifacts: "${TEMP_EMAIL_FILE}", allowEmptyArchive: true
                }
            }
        }
        
        // 🛑 MANUAL APPROVAL STAGE - Pipeline pauses here
        stage('⏸️ Manual Approval') {
            steps {
                script {
                    echo "⏳ Waiting for manual approval to proceed..."
                    echo "📧 Email created - ready for complete automation process"
                    echo "🌐 The email will be used for automatic website signup in Step 2"
                    echo "🎯 After signup, messages will be processed and account activated automatically"
                    
                    // Display email info for user reference
                    if (fileExists("${env.TEMP_EMAIL_FILE}")) {
                        def emailInfo = readFile("${env.TEMP_EMAIL_FILE}")
                        echo "📋 Current Email Info:"
                        echo "${emailInfo}"
                        
                        // Extract and display email address
                        try {
                            def emailAddress = sh(
                                script: "grep 'EMAIL_ADDRESS=' ${env.TEMP_EMAIL_FILE} | cut -d'=' -f2 || echo 'Not found'",
                                returnStdout: true
                            ).trim()
                            
                            if (emailAddress && emailAddress != 'Not found') {
                                echo "📧 ➤ Temporary email: ${emailAddress}"
                                echo "🌐 ➤ This will be used for website signup in Step 2"
                                echo "💌 ➤ After signup, the system will check for messages"
                                echo "🎯 ➤ If activation email is found, account will be activated automatically"
                                echo "📄 ➤ Final credentials will be saved to user.password.txt"
                            }
                        } catch (Exception e) {
                            echo "⚠️ Could not extract email address, check email_info.txt"
                        }
                    }
                }
                
                // 🛑 This is where the pipeline PAUSES and waits for user input
                script {
                    def userInput = input(
                        message: '📧 Ready to proceed with complete automation?\n\n🌐 Step 2: Website signup\n📬 Steps 3&4: Check and process messages\n🎯 Step 5: Account activation\n📄 Final: Create user.password.txt\n\nClick OK to continue.',
                        ok: 'OK - Proceed with all steps',
                        parameters: [
                            choice(
                                name: 'APPROVAL_ACTION',
                                choices: ['FULL_PROCESS', 'SIGNUP_ONLY', 'SKIP_SIGNUP'],
                                description: 'FULL_PROCESS: All steps including activation | SIGNUP_ONLY: Steps 2 only | SKIP_SIGNUP: Steps 3,4,5 only'
                            )
                        ]
                    )
                    
                    // Store the user input for later use
                    env.APPROVAL_ACTION = userInput
                    
                    echo "✅ Manual approval received!"
                    echo "🎛️ Selected action: ${env.APPROVAL_ACTION}"
                    
                    if (env.APPROVAL_ACTION == 'FULL_PROCESS') {
                        echo "🚀 All steps will be executed: signup + message processing + activation + credentials file"
                    } else if (env.APPROVAL_ACTION == 'SIGNUP_ONLY') {
                        echo "🌐 Only website signup will be performed"
                    } else {
                        echo "📬 Only message processing and activation will be performed (no signup)"
                    }
                }
            }
        }
        
        // 🌐 STEP 2: Website Signup
        stage('Step 2: Website Signup') {
            when {
                // Run if user chose full process or signup only
                expression {
                    return env.APPROVAL_ACTION in ['FULL_PROCESS', 'SIGNUP_ONLY']
                }
            }
            
            steps {
                script {
                    echo "🌐 Step 2: Automated website signup..."
                    echo "✅ User approved website signup process"
                }
                
                sh '''
                    echo "🤖 Running automated website signup..."
                    
                    # Update PATH to include user-installed packages
                    export PATH="$HOME/.local/bin:$PATH"
                    export PYTHONPATH="$HOME/.local/lib/python3.11/site-packages:$PYTHONPATH"
                    
                    # Final dependency check
                    echo "🔍 Final dependency check with updated PATH..."
                    ${PYTHON_PATH} -c "
import sys
import site

# Add user site-packages to path
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)

selenium_available = False
try:
    import selenium
    from selenium import webdriver
    print(f'✅ Selenium {selenium.__version__} ready')
    selenium_available = True
except ImportError as e:
    print(f'❌ Selenium not available: {e}')

try:
    import webdriver_manager
    print('✅ webdriver-manager ready')
except ImportError as e:
    print(f'❌ webdriver-manager not available: {e}')

if not selenium_available:
    print('⚠️ Selenium not available - website signup will fail')
    print('💡 Check package installation logs above')
    # Don't exit here, let the signup script handle the error
"
                    
                    # Verify we have the email file
                    if [ ! -f "${TEMP_EMAIL_FILE}" ]; then
                        echo "❌ No email file found for signup"
                        exit 1
                    fi
                    
                    # Extract email address for display
                    EMAIL_ADDR=$(grep 'EMAIL_ADDRESS=' "${TEMP_EMAIL_FILE}" | cut -d'=' -f2 || echo 'Unknown')
                    echo "📧 Using email for signup: $EMAIL_ADDR"
                    
                    # Check shared memory before running browsers
                    echo "💾 Shared memory status before browser startup:"
                    df -h /dev/shm 2>/dev/null || echo "⚠️ Could not check /dev/shm"
                    
                    # Run the signup automation with extended timeout and proper PATH
                    echo "🚀 Starting website signup automation..."
                    export PATH="$HOME/.local/bin:$PATH"
                    export PYTHONPATH="$HOME/.local/lib/python3.11/site-packages:$PYTHONPATH"
                    
                    timeout 600s ${PYTHON_PATH} website_signup.py || {
                        SIGNUP_RESULT=$?
                        echo "⚠️ Website signup returned exit code: $SIGNUP_RESULT"
                        
                        if [ $SIGNUP_RESULT -eq 124 ]; then
                            echo "⏰ Website signup timed out (10 minutes)"
                        elif [ $SIGNUP_RESULT -eq 1 ]; then
                            echo "🔧 Website signup failed - check browser logs"
                        fi
                        
                        echo "💡 Check logs and screenshots for details"
                    }
                    
                    # Display signup info if file was created
                    if [ -f "signup_info.json" ]; then
                        echo "📋 Signup Details:"
                        cat signup_info.json | ${PYTHON_PATH} -m json.tool 2>/dev/null || cat signup_info.json
                    fi
                    
                    # List all created files for debugging
                    echo "📁 Files created during signup:"
                    ls -la signup_*.png signup_*.json 2>/dev/null || echo "No signup files created"
                    
                    echo "✅ Website signup phase completed (check results above)"
                '''
            }
            
            post {
                always {
                    // Archive signup files and any screenshots
                    archiveArtifacts artifacts: "signup_*.json,signup_*.png", allowEmptyArchive: true
                }
            }
        }
        
        // STEP 3: Check for New Messages
        stage('Step 3: Check for New Messages') {
            when {
                // Run if user chose full process or skip signup
                expression {
                    return env.APPROVAL_ACTION in ['FULL_PROCESS', 'SKIP_SIGNUP']
                }
            }
            
            steps {
                script {
                    echo "🔍 Step 3: Checking for new messages..."
                    echo "✅ Manual approval received - proceeding with message check"
                }
                
                sh '''
                    echo "📬 Running message checker..."
                    # Use timeout to prevent hanging and provide non-interactive input
                    timeout 300s ${PYTHON_PATH} -c "
from check_messages import read_email_info, get_email_messages
email_id, email_address = read_email_info()
if email_id and email_address:
    print(f'📧 Checking messages for: {email_address}')
    messages = get_email_messages(email_id)
    if messages:
        print(f'✅ Found {len(messages)} new messages')
    else:
        print('📭 No new messages found')
else:
    print('❌ Could not read email information')
    exit(1)
"
                    
                    if [ $? -eq 0 ]; then
                        echo "✅ Message check completed successfully"
                    else
                        echo "⚠️ Message check completed with warnings"
                    fi
                '''
            }
            
            post {
                success {
                    archiveArtifacts artifacts: "${MESSAGE_IDS_FILE}", allowEmptyArchive: true
                }
            }
        }
        
        // STEP 4: Get Message Details
        stage('Step 4: Get Message Details') {
            when {
                allOf {
                    // Only run this stage if message_ids.txt exists and is not empty
                    expression {
                        return fileExists('message_ids.txt') && 
                               sh(script: "[ -s message_ids.txt ]", returnStatus: true) == 0
                    }
                    // Also check if user chose to get message details
                    expression {
                        return env.APPROVAL_ACTION in ['FULL_PROCESS', 'SKIP_SIGNUP']
                    }
                }
            }
            
            steps {
                script {
                    echo "📖 Step 4: Getting detailed message information..."
                    echo "✅ User approved proceeding with detailed message processing"
                }
                
                sh '''
                    echo "🔍 Processing stored message IDs..."
                    # Use timeout and provide automated input for the script
                    timeout 600s ${PYTHON_PATH} -c "
from get_message_details import read_email_info, read_message_ids, get_all_messages, filter_messages_by_ids, display_message_details, save_message_details
# Read necessary information
email_id = read_email_info()
target_message_ids = read_message_ids()
if not email_id:
    print('❌ Could not read email information')
    exit(1)
if not target_message_ids:
    print('📭 No stored message IDs found')
    exit(0)
print(f'🚀 Processing {len(target_message_ids)} stored message IDs...')
# Get all messages and filter
all_messages = get_all_messages(email_id)
if all_messages is None:
    print('❌ Failed to fetch messages')
    exit(1)
filtered_messages = filter_messages_by_ids(all_messages, target_message_ids)
if not filtered_messages:
    print('📭 No matching messages found')
    exit(0)
print(f'📧 Processing {len(filtered_messages)} matching messages...')
# Process each message automatically (save all to JSON)
for i, message in enumerate(filtered_messages, 1):
    message_id = message.get('id', f'unknown_{i}')
    print(f'\\n--- Processing Message {i}/{len(filtered_messages)} ---')
    display_message_details(message, i)
    
    # Auto-save all message details
    save_message_details(message_id, message)
    
print(f'✅ Processed all {len(filtered_messages)} messages')
"
                    
                    if [ $? -eq 0 ]; then
                        echo "✅ Message details processing completed successfully"
                    else
                        echo "⚠️ Message details processing completed with warnings"
                    fi
                '''
            }
            
            post {
                success {
                    // Archive all JSON files created
                    archiveArtifacts artifacts: "message_details_*.json", allowEmptyArchive: true
                }
            }
        }
        
        // STEP 5: Activate Account
        stage('Step 5: Activate Account') {
            when {
                allOf {
                    // Only run if we have message details and signup was successful
                    expression {
                        return fileExists('signup_info.json') && 
                               sh(script: "ls -1 message_details_*.json 2>/dev/null | wc -l", returnStdout: true).trim() != "0"
                    }
                    expression {
                        return env.APPROVAL_ACTION in ['FULL_
