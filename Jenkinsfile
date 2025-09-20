pipeline {
    agent any
    
    // Schedule the pipeline to run every 10 minutes
    triggers {
        cron('H/10 * * * *')  // Runs every 10 minutes
    }
    
    environment {
        // Define workspace paths
        PYTHON_PATH = '/usr/bin/python3'  // Adjust path as needed
        WORKSPACE_DIR = "${WORKSPACE}"
        
        // Email configuration (if you want notifications)
        EMAIL_RECIPIENTS = 'your-email@example.com'  // Change this
        
        // Temp email configuration
        TEMP_EMAIL_FILE = 'email_info.txt'
        MESSAGE_IDS_FILE = 'message_ids.txt'
        SIGNUP_FILE = 'signup_info.json'
        
        // Archive paths for artifacts
        ARTIFACTS_PATTERN = '*.txt,*.json,message_details_*.json,signup_*.json'
    }
    
    options {
        // Keep builds for 30 days or max 50 builds
        buildDiscarder(logRotator(daysToKeepStr: '30', numToKeepStr: '50'))
        
        // Set build timeout to 20 minutes (increased for signup step)
        timeout(time: 20, unit: 'MINUTES')
        
        // Disable concurrent builds
        disableConcurrentBuilds()
        
        // Add timestamps to console output
        timestamps()
    }
    
    stages {
        stage('Setup Environment') {
            steps {
                script {
                    echo "🚀 Starting Complete Email & Signup Pipeline"
                    echo "📅 Build Date: ${new Date()}"
                    echo "🔢 Build Number: ${BUILD_NUMBER}"
                    echo "📂 Workspace: ${WORKSPACE_DIR}"
                }
                
                // Clean up old files if needed (optional)
                sh '''
                    echo "🧹 Cleaning up old files..."
                    find . -name "message_details_*.json" -mtime +7 -delete || true
                    find . -name "signup_*.json" -mtime +7 -delete || true
                    find . -name "*.png" -mtime +7 -delete || true
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
                    
                    echo "✅ All Python scripts found"
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
                    echo "📧 Check your temporary email for messages before continuing"
                    echo "🌐 You can send test emails to the address created in Step 1"
                    
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
                                echo "📧 ➤ Send test emails to: ${emailAddress}"
                                echo "💌 ➤ Send your test messages now, then click OK below"
                                echo "🌐 ➤ This email will be used for website signup in Step 4"
                            }
                        } catch (Exception e) {
                            echo "⚠️ Could not extract email address, check email_info.txt"
                        }
                    }
                }
                
                // 🛑 This is where the pipeline PAUSES and waits for user input
                script {
                    def userInput = input(
                        message: '📧 Ready to check messages and signup to website?\n\n💌 Make sure you sent test emails to the address above.\n\n🌐 The email will be used for automatic website signup.\n\nClick OK to proceed with all steps.',
                        ok: 'OK - Proceed with all steps',
                        parameters: [
                            choice(
                                name: 'APPROVAL_ACTION',
                                choices: ['FULL_PROCESS', 'SKIP_SIGNUP', 'MESSAGES_ONLY'],
                                description: 'FULL_PROCESS: All steps including signup | SKIP_SIGNUP: Steps 2&3 only | MESSAGES_ONLY: Step 2 only'
                            )
                        ]
                    )
                    
                    // Store the user input for later use
                    env.APPROVAL_ACTION = userInput
                    
                    echo "✅ Manual approval received!"
                    echo "🎛️ Selected action: ${env.APPROVAL_ACTION}"
                    
                    if (env.APPROVAL_ACTION == 'FULL_PROCESS') {
                        echo "🚀 All steps will be executed including website signup"
                    } else if (env.APPROVAL_ACTION == 'SKIP_SIGNUP') {
                        echo "ℹ️ Website signup will be skipped"
                    } else {
                        echo "ℹ️ Only message checking will be performed"
                    }
                }
            }
        }
        
        stage('Step 2: Check for New Messages') {
            steps {
                script {
                    echo "🔍 Step 2: Checking for new messages..."
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
        
        stage('Step 3: Get Message Details') {
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
                    echo "📖 Step 3: Getting detailed message information..."
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
        
        // 🌐 NEW STEP 4: Website Signup
        stage('Step 4: Website Signup') {
            when {
                // Only run if user chose full process
                expression {
                    return env.APPROVAL_ACTION == 'FULL_PROCESS'
                }
            }
            
            steps {
                script {
                    echo "🌐 Step 4: Automated website signup..."
                    echo "✅ User approved website signup process"
                }
                
                sh '''
                    echo "🤖 Running automated website signup..."
                    
                    # First verify we have the email file
                    if [ ! -f "${TEMP_EMAIL_FILE}" ]; then
                        echo "❌ No email file found for signup"
                        exit 1
                    fi
                    
                    # Extract email address for display
                    EMAIL_ADDR=$(grep 'EMAIL_ADDRESS=' "${TEMP_EMAIL_FILE}" | cut -d'=' -f2 || echo 'Unknown')
                    echo "📧 Using email for signup: $EMAIL_ADDR"
                    
                    # Run the signup automation
                    timeout 300s ${PYTHON_PATH} website_signup.py
                    
                    SIGNUP_RESULT=$?
                    
                    if [ $SIGNUP_RESULT -eq 0 ]; then
                        echo "✅ Website signup completed successfully"
                        
                        # Display signup info if file was created
                        if [ -f "signup_info.json" ]; then
                            echo "📋 Signup Details:"
                            cat signup_info.json | python3 -m json.tool || cat signup_info.json
                        fi
                    else
                        echo "⚠️ Website signup completed with warnings"
                        echo "💡 Check signup logs for details"
                    fi
                    
                    # Always continue the pipeline even if signup has issues
                    exit 0
                '''
            }
            
            post {
                success {
                    // Archive signup files and any screenshots
                    archiveArtifacts artifacts: "signup_*.json,signup_*.png", allowEmptyArchive: true
                }
            }
        }
        
        stage('Generate Summary Report') {
            steps {
                script {
                    echo "📊 Generating complete pipeline summary report..."
                }
                
                sh '''
                    # Create a comprehensive summary report
                    REPORT_FILE="complete_pipeline_summary_$(date +%Y%m%d_%H%M%S).txt"
                    
                    echo "=== COMPLETE EMAIL & SIGNUP PIPELINE SUMMARY ===" > "$REPORT_FILE"
                    echo "Date: $(date)" >> "$REPORT_FILE"
                    echo "Build Number: ${BUILD_NUMBER}" >> "$REPORT_FILE"
                    echo "Jenkins Job: ${JOB_NAME}" >> "$REPORT_FILE"
                    echo "Manual Approval: ${APPROVAL_ACTION}" >> "$REPORT_FILE"
                    echo "" >> "$REPORT_FILE"
                    
                    # Email info
                    if [ -f "${TEMP_EMAIL_FILE}" ]; then
                        echo "📧 TEMPORARY EMAIL INFO:" >> "$REPORT_FILE"
                        cat "${TEMP_EMAIL_FILE}" >> "$REPORT_FILE"
                        echo "" >> "$REPORT_FILE"
                    fi
                    
                    # Message count
                    if [ -f "${MESSAGE_IDS_FILE}" ]; then
                        MSG_COUNT=$(grep -c "MESSAGE_ID=" "${MESSAGE_IDS_FILE}" || echo "0")
                        echo "📬 TOTAL MESSAGES PROCESSED: $MSG_COUNT" >> "$REPORT_FILE"
                        echo "" >> "$REPORT_FILE"
                    fi
                    
                    # Detailed message files
                    DETAIL_COUNT=$(ls -1 message_details_*.json 2>/dev/null | wc -l)
                    echo "📖 DETAILED MESSAGE FILES CREATED: $DETAIL_COUNT" >> "$REPORT_FILE"
                    
                    if [ $DETAIL_COUNT -gt 0 ]; then
                        echo "" >> "$REPORT_FILE"
                        echo "📄 DETAILED MESSAGE FILES:" >> "$REPORT_FILE"
                        ls -la message_details_*.json >> "$REPORT_FILE" 2>/dev/null || true
                    fi
                    
                    # Signup information
                    if [ -f "signup_info.json" ]; then
                        echo "" >> "$REPORT_FILE"
                        echo "🌐 WEBSITE SIGNUP INFORMATION:" >> "$REPORT_FILE"
                        cat signup_info.json >> "$REPORT_FILE" 2>/dev/null || echo "Could not read signup info"
                    fi
                    
                    # Screenshots info
                    SCREENSHOT_COUNT=$(ls -1 *.png 2>/dev/null | wc -l)
                    if [ $SCREENSHOT_COUNT -gt 0 ]; then
                        echo "" >> "$REPORT_FILE"
                        echo "📸 SCREENSHOTS CAPTURED: $SCREENSHOT_COUNT" >> "$REPORT_FILE"
                        ls -la *.png >> "$REPORT_FILE" 2>/dev/null || true
                    fi
                    
                    echo "" >> "$REPORT_FILE"
                    echo "=== END COMPLETE SUMMARY ===" >> "$REPORT_FILE"
                    
                    echo "📄 Complete summary report created: $REPORT_FILE"
                    cat "$REPORT_FILE"
                '''
            }
            
            post {
                success {
                    archiveArtifacts artifacts: "complete_pipeline_summary_*.txt", allowEmptyArchive: true
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "🏁 Complete pipeline finished"
                
                // Clean up workspace but keep important files
                sh '''
                    echo "🧹 Cleaning up temporary files..."
                    # Remove Python cache files
                    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
                    find . -name "*.pyc" -delete 2>/dev/null || true
                '''
            }
        }
        
        success {
            script {
                echo "✅ Complete pipeline completed successfully"
                
                if (env.APPROVAL_ACTION == 'FULL_PROCESS') {
                    echo "🎉 All steps completed including website signup"
                } else if (env.APPROVAL_ACTION == 'SKIP_SIGNUP') {
                    echo "ℹ️ Message processing completed, signup was skipped"
                } else {
                    echo "ℹ️ Only message checking was performed"
                }
                
                echo "📊 Check archived artifacts for detailed results"
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline failed"
            }
        }
        
        unstable {
            script {
                echo "⚠️ Pipeline completed with warnings"
            }
        }
        
        aborted {
            script {
                echo "🛑 Pipeline was aborted (possibly during manual approval)"
            }
        }
    }
}
