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

        // Discord Configuration
        DISCORD_WEBHOOK_URL = 'https://discordapp.com/api/webhooks/1420217589510176779/48UhPwNV4x_OPmbIXyrhsgnhxxoLAWJt1cW96T5Cum-RQCP19gJNlVAmSYH2ydatsQeo'

        // Email configuration
        EMAIL_RECIPIENTS = 'matan@yahoo.com'
        GMAIL_SENDER = 'your-jenkins-email@gmail.com'
        GMAIL_APP_PASSWORD = 'your-16-char-app-password'

        // File configurations
        TEMP_EMAIL_FILE = 'email_info.txt'
        MESSAGE_IDS_FILE = 'message_ids.txt'
        SIGNUP_FILE = 'signup_info.json'
        ACTIVATION_FILE = 'activation_info.json'
        USER_CREDENTIALS_FILE = 'user.password.txt'
        EMAIL_LOG_FILE = 'email_sent.json'

        // Timing configurations (improved)
        EMAIL_CHECK_MAX_RETRIES = '15'  // Increased from 10
        EMAIL_CHECK_RETRY_DELAY = '45'  // Increased from 30 seconds
        SIGNUP_WAIT_TIME = '60'         // Wait after signup before checking emails
        MAX_TOTAL_WAIT_TIME = '900'     // 15 minutes maximum total wait
    }

    options {
        // Set build timeout to 45 minutes (increased from 30)
        timeout(time: 45, unit: 'MINUTES')

        // Keep only last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))

        // Add timestamps to console output
        timestamps()

        // Disable concurrent builds
        disableConcurrentBuilds()
    }

    stages {
        stage('Cleanup Workspace') {
            steps {
                script {
                    echo "🧹 Cleaning up workspace..."

                    // Clean up all files from previous runs
                    sh '''
                        echo "📂 Current workspace contents:"
                        ls -la || true

                        echo "🗑️ Removing old files..."
                        rm -f email_info.txt || true
                        rm -f message_ids.txt || true
                        rm -f signup_info.json || true
                        rm -f activation_info.json || true
                        rm -f user.password.txt || true
                        rm -f email_sent.json || true
                        rm -f message_details_*.json || true
                        rm -f *.log || true

                        echo "✅ Workspace cleaned"
                        ls -la || true
                    '''
                }
            }
        }

        stage('Step 1: Create Temporary Email') {
            steps {
                script {
                    echo "📧 Creating temporary email..."

                    sh '''
                        echo "🚀 Running email creator..."
                        timeout 180s ${PYTHON_PATH} -c "
from create_email import create_temporary_email
result = create_temporary_email()
if not result:
    print('❌ Failed to create email')
    exit(1)
else:
    print('✅ Email created successfully')
"
                    '''

                    // Verify email file was created
                    sh '''
                        if [ -f "${TEMP_EMAIL_FILE}" ]; then
                            echo "✅ Email file created successfully"
                            echo "📄 Email file contents:"
                            cat "${TEMP_EMAIL_FILE}"
                        else
                            echo "❌ Email file not found!"
                            exit 1
                        fi
                    '''
                }
            }
            post {
                always {
                    // Archive email info file
                    archiveArtifacts artifacts: 'email_info.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Step 2: Website Signup') {
            steps {
                script {
                    echo "🌐 Starting website signup process..."

                    sh '''
                        echo "📝 Running website signup..."
                        timeout 600s ${PYTHON_PATH} -c "
from website_signup import EmbyILRegistration
import sys

try:
    # Create registration bot
    bot = EmbyILRegistration(headless=True)

    # Perform registration
    success = bot.register_account()

    if success:
        print('✅ Website registration completed successfully')
        sys.exit(0)
    else:
        print('❌ Website registration failed')
        sys.exit(1)

except Exception as e:
    print(f'❌ Registration error: {e}')
    sys.exit(1)
finally:
    try:
        bot.cleanup()
    except:
        pass
"
                    '''

                    // Add strategic wait time after signup
                    sh '''
                        echo "⏳ Waiting ${SIGNUP_WAIT_TIME} seconds for email delivery..."
                        echo "💡 This gives the email system time to process and deliver the verification email"
                        sleep ${SIGNUP_WAIT_TIME}
                        echo "✅ Wait period completed"
                    '''
                }
            }
            post {
                always {
                    // Archive signup info file
                    archiveArtifacts artifacts: 'signup_info.json', allowEmptyArchive: true
                }
            }
        }


// אחרי השלב השני, הוסף:
sh '''
    echo "⏳ Waiting ${SIGNUP_WAIT_TIME} seconds for email delivery..."
    sleep 60
    echo "✅ Wait period completed"
'''

        
        stage('Step 3: Check Messages with Retry') {
            steps {
                script {
                    echo "📬 Checking for verification email with improved retry mechanism..."

                    sh '''
                        echo "🔍 Starting enhanced message checker..."
                        timeout ${MAX_TOTAL_WAIT_TIME}s ${PYTHON_PATH} -c "
from check_messages import read_email_info, get_email_messages_with_retry
import sys

# Read email information
email_id, email_address = read_email_info()
if not email_id or not email_address:
    print('❌ Could not read email information')
    sys.exit(1)

print(f'📧 Checking messages for: {email_address}')
print(f'⚙️ Using enhanced retry mechanism:')
print(f'   • Max retries: ${EMAIL_CHECK_MAX_RETRIES}')
print(f'   • Retry delay: ${EMAIL_CHECK_RETRY_DELAY} seconds')
print(f'   • Max total time: ${MAX_TOTAL_WAIT_TIME} seconds')

# Use the improved retry mechanism
messages = get_email_messages_with_retry(
    email_id, 
    max_retries=int('${EMAIL_CHECK_MAX_RETRIES}'), 
    retry_delay=int('${EMAIL_CHECK_RETRY_DELAY}')
)

if messages:
    print(f'✅ Found {len(messages)} new messages')
    print('🎉 Email verification received!')
    sys.exit(0)
else:
    print('📭 No new messages found after all retries')
    print('⚠️ This might indicate an issue with email delivery or timing')
    sys.exit(1)
"
                    '''

                    // Verify message file was created if messages found
                    sh '''
                        if [ $? -eq 0 ]; then
                            echo "✅ Message check completed successfully"

                            if [ -f "${MESSAGE_IDS_FILE}" ]; then
                                echo "📄 Message IDs file created:"
                                cat "${MESSAGE_IDS_FILE}"
                            else
                                echo "⚠️ No message IDs file found (no messages received)"
                            fi
                        else
                            echo "❌ Message check failed"
                            exit 1
                        fi
                    '''
                }
            }
            post {
                always {
                    // Archive message IDs file
                    archiveArtifacts artifacts: 'message_ids.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Step 4: Get Message Details') {
            when {
                expression { fileExists('message_ids.txt') }
            }
            steps {
                script {
                    echo "📖 Processing verification email details..."

                    sh '''
                        echo "🔍 Running message details extractor..."
                        timeout 300s ${PYTHON_PATH} -c "
from get_message_details import process_message_details
import sys

try:
    result = process_message_details()
    if result:
        print('✅ Message details processed successfully')
        sys.exit(0)
    else:
        print('❌ Failed to process message details')
        sys.exit(1)
except Exception as e:
    print(f'❌ Error processing message details: {e}')
    sys.exit(1)
"
                    '''
                }
            }
            post {
                always {
                    // Archive message details files
                    archiveArtifacts artifacts: 'message_details_*.json', allowEmptyArchive: true
                }
            }
        }

        stage('Step 5: Activate Account') {
            steps {
                script {
                    echo "🔐 Activating EmbyIL account..."

                    // Check if we have message details files
                    sh '''
                        MESSAGE_FILES=$(ls -1 message_details_*.json 2>/dev/null | wc -l)
                        echo "📁 Found $MESSAGE_FILES message detail files"

                        if [ "$MESSAGE_FILES" -eq 0 ]; then
                            echo "❌ No message details files found"
                            echo "💡 Cannot proceed with activation without verification email"
                            exit 1
                        fi
                    '''

                    sh '''
                        echo "🔓 Running account activation..."
                        timeout 600s ${PYTHON_PATH} -c "
from activate_account import EmbyILAccountActivation
import sys

try:
    # Create activation bot
    bot = EmbyILAccountActivation(headless=True)

    # Perform activation
    success = bot.activate_account()

    if success:
        print('✅ Account activation completed successfully')
        sys.exit(0)
    else:
        print('❌ Account activation failed')
        sys.exit(1)

except Exception as e:
    print(f'❌ Activation error: {e}')
    sys.exit(1)
finally:
    try:
        bot.cleanup()
    except:
        pass
"
                    '''
                }
            }
            post {
                always {
                    // Archive activation info file
                    archiveArtifacts artifacts: 'activation_info.json', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'user.password.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Step 6: Send Results') {
            when {
                expression { fileExists('user.password.txt') }
            }
            steps {
                script {
                    echo "📤 Sending final results and credentials..."

                    sh '''
                        echo "📧 Sending completion notification..."
                        timeout 180s ${PYTHON_PATH} -c "
from send_email import send_completion_email
from send_approval_webhook import send_discord_notification
import sys

try:
    # Send email with credentials
    email_result = send_completion_email()

    # Send Discord notification
    discord_result = send_discord_notification()

    if email_result or discord_result:
        print('✅ Results sent successfully')
        sys.exit(0)
    else:
        print('⚠️ Failed to send results, but process completed')
        sys.exit(0)  # Don't fail the build for notification issues

except Exception as e:
    print(f'⚠️ Error sending results: {e}')
    print('✅ Process completed, but notification failed')
    sys.exit(0)  # Don't fail the build for notification issues
"
                    '''
                }
            }
            post {
                always {
                    // Archive email log file
                    archiveArtifacts artifacts: 'email_sent.json', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        always {
            script {
                echo "📊 Pipeline execution completed"

                // Display final summary
                sh '''
                    echo "\n📋 EXECUTION SUMMARY"
                    echo "===================="
                    echo "📧 Email file: $([ -f email_info.txt ] && echo "✅ Created" || echo "❌ Missing")"
                    echo "📝 Signup file: $([ -f signup_info.json ] && echo "✅ Created" || echo "❌ Missing")"
                    echo "📬 Messages file: $([ -f message_ids.txt ] && echo "✅ Created" || echo "❌ Missing")"
                    echo "📖 Details files: $(ls message_details_*.json 2>/dev/null | wc -l) found"
                    echo "🔐 Activation file: $([ -f activation_info.json ] && echo "✅ Created" || echo "❌ Missing")"
                    echo "🎟️ Credentials file: $([ -f user.password.txt ] && echo "✅ Created" || echo "❌ Missing")"
                    echo "📤 Email log file: $([ -f email_sent.json ] && echo "✅ Created" || echo "❌ Missing")"
                    echo "===================="
                '''
            }

            // Archive all artifacts
            archiveArtifacts artifacts: '*.txt,*.json', allowEmptyArchive: true

            // Clean up sensitive files but keep logs
            sh '''
                echo "🧹 Cleaning up sensitive files..."
                rm -f user.password.txt || true
                echo "✅ Cleanup completed"
            '''
        }

        success {
            script {
                echo "🎉 Pipeline completed successfully!"

                // Send success notification
                sh '''
                    echo "📤 Sending success notification..."
                    ${PYTHON_PATH} -c "
import requests
import json
from datetime import datetime

webhook_url = '${DISCORD_WEBHOOK_URL}'
message = {
    'content': '🎉 **EmbyIL Account Creation Successful!**\\n' +
               f'⏰ Completed at: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}\\n' +
               '✅ New account created and activated\\n' +
               '📧 Credentials sent to user\\n' +
               '🔄 Next run scheduled in 3 days'
}

try:
    response = requests.post(webhook_url, json=message, timeout=30)
    if response.status_code == 204:
        print('✅ Success notification sent to Discord')
    else:
        print(f'⚠️ Discord notification failed: {response.status_code}')
except Exception as e:
    print(f'⚠️ Error sending Discord notification: {e}')
" || true
                '''
            }
        }

        failure {
            script {
                echo "❌ Pipeline failed!"

                // Send failure notification
                sh '''
                    echo "📤 Sending failure notification..."
                    ${PYTHON_PATH} -c "
import requests
import json
from datetime import datetime

webhook_url = '${DISCORD_WEBHOOK_URL}'
message = {
    'content': '❌ **EmbyIL Account Creation Failed!**\\n' +
               f'⏰ Failed at: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}\\n' +
               '🔍 Check Jenkins logs for details\\n' +
               '🔄 Will retry in 3 days'
}

try:
    response = requests.post(webhook_url, json=message, timeout=30)
    if response.status_code == 204:
        print('✅ Failure notification sent to Discord')
    else:
        print(f'⚠️ Discord notification failed: {response.status_code}')
except Exception as e:
    print(f'⚠️ Error sending Discord notification: {e}')
" || true
                '''
            }
        }
    }
}
