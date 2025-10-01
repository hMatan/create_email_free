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
                    echo "🧹 Enhanced cleanup - removing ALL old files..."
                }
                sh '''
                    echo "📂 Current workspace contents before cleanup:"
                    ls -la || true
                    echo ""
                    echo "🗑️ Removing ALL old files comprehensively..."

                    # קבצי אימייל והודעות
                    rm -f email_info.txt || true
                    rm -f message_ids.txt || true
                    rm -f message_details_*.json || true

                    # קבצי הרשמה
                    rm -f signup_*.json || true
                    rm -f signup_info.json || true

                    # קבצי הפעלה
                    rm -f activation_*.json || true
                    rm -f activation_info.json || true

                    # קבצי תוצאות
                    rm -f user.password.txt || true
                    rm -f email_sent.json || true
                    rm -f username_counter.txt || true

                    # קבצי לוגים ותיעוד
                    rm -f *.log || true
                    rm -f build_*_summary_*.txt || true

                    # קבצי תמונות (צילומי מסך)
                    rm -f *.png || true
                    rm -f signup_*.png || true
                    rm -f activation_*.png || true

                    # קבצים זמניים נוספים
                    rm -f temp_* || true
                    rm -f tmp_* || true
                    rm -f *.tmp || true

                    # ניקוי Python cache
                    rm -rf __pycache__ || true
                    rm -f *.pyc || true

                    echo ""
                    echo "✅ Enhanced cleanup completed"
                    echo "📂 Workspace contents after cleanup:"
                    ls -la || true
                    echo ""
                    echo "🔢 File count after cleanup: $(ls -1 | wc -l)"
                '''
            }
        }

        stage('📱 WhatsApp Start Notification') {
            steps {
                script {
                    echo "📱 Sending WhatsApp start notification..."
                }
                sh '''
                    echo "📤 Contacting WhatsApp service..."

                    curl -X POST http://192.168.1.50:3000/webhook/jenkins \
                      -H "Content-Type: application/json" \
                      -d '{
                        "type": "start",
                        "buildNumber": "'$BUILD_NUMBER'",
                        "timestamp": "'$(date -Iseconds)'",
                        "message": "🚀 Starting EmbyIL Account Creation Process",
                        "details": "Build #'$BUILD_NUMBER' started"
                      }' \
                      --connect-timeout 10 \
                      --max-time 30 \
                      --silent \
                      --show-error \
                      || echo "⚠️ WhatsApp start notification failed"

                    echo "✅ WhatsApp start notification sent"
                '''
            }
        }

        stage('Step 1: Create Temporary Email') {
            steps {
                script {
                    echo "📧 Creating temporary email..."
                }
                sh '''
                    echo "🚀 Running enhanced email creator..."
                    timeout 180s ${PYTHON_PATH} -c "
from create_email import create_temporary_email
import sys
print('🌟 Starting EmbyIL email creation process...')
result = create_temporary_email()
if result:
    print('✅ Email created successfully')
    sys.exit(0)
else:
    print('❌ Failed to create email')
    sys.exit(1)
"
                '''
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
            post {
                always {
                    archiveArtifacts artifacts: 'email_info.txt', allowEmptyArchive: true
                }
            }
        }

        stage('📱 WhatsApp Email Created Notification') {
            when {
                expression { return fileExists('email_info.txt') }
            }
            steps {
                script {
                    echo "📱 Sending WhatsApp email created notification..."
                }
                sh '''
                    EMAIL_ADDRESS=$(grep "EMAIL_ADDRESS=" email_info.txt | cut -d'=' -f2 | tr -d '\r')

                    curl -X POST http://192.168.1.50:3000/webhook/jenkins \
                      -H "Content-Type: application/json" \
                      -d '{
                        "type": "progress",
                        "buildNumber": "'$BUILD_NUMBER'",
                        "timestamp": "'$(date -Iseconds)'",
                        "message": "📧 Temporary Email Created Successfully",
                        "details": "Email: '$EMAIL_ADDRESS'",
                        "stage": "Step 1: Email Creation"
                      }' \
                      --connect-timeout 10 \
                      --max-time 30 \
                      --silent \
                      --show-error \
                      || echo "⚠️ WhatsApp email notification failed"
                '''
            }
        }

        stage('Step 2: Website Signup') {
            steps {
                script {
                    echo "🌐 Starting website signup process..."
                }
                sh '''
                    echo "📝 Running website signup..."
                    timeout 600s ${PYTHON_PATH} -c "
from website_signup import EmbyILRegistration
import sys
print('🌐 Starting EmbyIL website registration...')
try:
    bot = EmbyILRegistration(headless=True)
    success = bot.register_account()
    if success:
        print('✅ Website registration completed successfully')
        sys.exit(0)
    else:
        print('❌ Website registration failed')
        sys.exit(1)
except Exception as e:
    print(f'❌ Registration error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        bot.cleanup()
        print('🧹 Browser cleanup completed')
    except:
        pass
"
                '''
                sh '''
                    echo "⏳ Waiting ${SIGNUP_WAIT_TIME} seconds for email delivery..."
                    echo "💡 This gives the email system time to process and deliver the verification email"
                    echo "🕐 Start time: $(date)"
                    sleep ${SIGNUP_WAIT_TIME}
                    echo "🕐 End time: $(date)"
                    echo "✅ Wait period completed - proceeding to check messages"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'signup_info.json', allowEmptyArchive: true
                }
            }
        }

        stage('📱 WhatsApp Account Registered Notification') {
            when {
                expression { return fileExists('signup_info.json') }
            }
            steps {
                script {
                    echo "📱 Sending WhatsApp account registered notification..."
                }
                sh '''
                    curl -X POST http://192.168.1.50:3000/webhook/jenkins \
                      -H "Content-Type: application/json" \
                      -d '{
                        "type": "progress",
                        "buildNumber": "'$BUILD_NUMBER'",
                        "timestamp": "'$(date -Iseconds)'",
                        "message": "🌐 Website Registration Completed",
                        "details": "Account registered successfully on EmbyIL",
                        "stage": "Step 2: Website Signup"
                      }' \
                      --connect-timeout 10 \
                      --max-time 30 \
                      --silent \
                      --show-error \
                      || echo "⚠️ WhatsApp signup notification failed"
                '''
            }
        }

        stage('Step 3: Check Messages with Enhanced Retry') {
            steps {
                script {
                    echo "📬 Checking for verification email with improved retry mechanism..."
                }
                sh '''
                    echo "🔍 Starting enhanced message checker..."
                    echo "⚙️ Configuration:"
                    echo "   • Max retries: ${EMAIL_CHECK_MAX_RETRIES}"
                    echo "   • Retry delay: ${EMAIL_CHECK_RETRY_DELAY} seconds"
                    echo "   • Max total time: ${MAX_TOTAL_WAIT_TIME} seconds"
                    echo "   • Start time: $(date)"
                    timeout ${MAX_TOTAL_WAIT_TIME}s ${PYTHON_PATH} -c "
from check_messages import read_email_info
import sys
email_id, email_address = read_email_info()
if not email_id or not email_address:
    print('❌ Could not read email information')
    sys.exit(1)
print(f'📧 Checking messages for: {email_address}')
try:
    from check_messages import get_email_messages_with_retry
    print('🚀 Using enhanced retry mechanism')
    messages = get_email_messages_with_retry(
        email_id, 
        max_retries=int('${EMAIL_CHECK_MAX_RETRIES}'), 
        retry_delay=int('${EMAIL_CHECK_RETRY_DELAY}')
    )
except ImportError:
    print('⚠️ Enhanced retry not available, using standard method')
    from check_messages import get_email_messages
    messages = get_email_messages(email_id)
if messages:
    print(f'🎉 SUCCESS! Found {len(messages)} new messages')
    print('📧 Email verification received!')
    sys.exit(0)
elif messages == []:
    print('📭 No new messages found (but email system is working)')
    print('⚠️ This might indicate timing issues or duplicate processing')
    sys.exit(1)
else:
    print('❌ No messages found after all retries')
    print('💡 This might indicate an issue with email delivery or timing')
    sys.exit(1)
"
                '''
                sh '''
                    EXIT_CODE=$?
                    echo "🔍 Checking results..."
                    echo "📊 Exit code: $EXIT_CODE"
                    echo "🕐 End time: $(date)"
                    if [ $EXIT_CODE -eq 0 ]; then
                        echo "✅ Message check completed successfully"
                        if [ -f "${MESSAGE_IDS_FILE}" ]; then
                            echo "📄 Message IDs file created:"
                            cat "${MESSAGE_IDS_FILE}"
                            MESSAGE_COUNT=$(grep -c "MESSAGE_ID=" "${MESSAGE_IDS_FILE}" || echo "0")
                            echo "📊 Total messages processed: $MESSAGE_COUNT"
                        else
                            echo "⚠️ No message IDs file found"
                        fi
                    else
                        echo "❌ Message check failed with code: $EXIT_CODE"
                        exit $EXIT_CODE
                    fi
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'message_ids.txt', allowEmptyArchive: true
                }
            }
        }

        stage('📱 WhatsApp Verification Email Received') {
            when {
                expression { return fileExists('message_ids.txt') }
            }
            steps {
                script {
                    echo "📱 Sending WhatsApp verification email notification..."
                }
                sh '''
                    MESSAGE_COUNT=$(grep -c "MESSAGE_ID=" message_ids.txt || echo "0")

                    curl -X POST http://192.168.1.50:3000/webhook/jenkins \
                      -H "Content-Type: application/json" \
                      -d '{
                        "type": "progress",
                        "buildNumber": "'$BUILD_NUMBER'",
                        "timestamp": "'$(date -Iseconds)'",
                        "message": "📬 Verification Email Received",
                        "details": "Found '$MESSAGE_COUNT' verification messages",
                        "stage": "Step 3: Email Verification"
                      }' \
                      --connect-timeout 10 \
                      --max-time 30 \
                      --silent \
                      --show-error \
                      || echo "⚠️ WhatsApp verification notification failed"
                '''
            }
        }

        stage('Step 4: Get Message Details') {
            when {
                expression { fileExists('message_ids.txt') }
            }
            steps {
                script {
                    echo "📖 Processing verification email details..."
                }
                sh '''
                    echo "🔍 Running message details extractor..."
                    timeout 300s ${PYTHON_PATH} -c "
from get_message_details import process_message_details
import sys
print('📖 Processing message details...')
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
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'message_details_*.json', allowEmptyArchive: true
                }
            }
        }

        stage('Step 5: Activate Account') {
            steps {
                script {
                    echo "🔐 Activating EmbyIL account..."
                }
                sh '''
                    MESSAGE_FILES=$(ls -1 message_details_*.json 2>/dev/null | wc -l)
                    echo "📁 Found $MESSAGE_FILES message detail files"
                    if [ "$MESSAGE_FILES" -eq 0 ]; then
                        echo "❌ No message details files found"
                        echo "💡 Cannot proceed with activation without verification email"
                        exit 1
                    fi
                    echo "📋 Message detail files:"
                    ls -la message_details_*.json || true
                '''
                sh '''
                    echo "🔓 Running account activation..."
                    timeout 600s ${PYTHON_PATH} -c "
from activate_account import EmbyILAccountActivation
import sys
print('🔐 Starting account activation process...')
try:
    bot = EmbyILAccountActivation(headless=True)
    success = bot.activate_account()
    if success:
        print('✅ Account activation completed successfully')
        sys.exit(0)
    else:
        print('❌ Account activation failed')
        sys.exit(1)
except Exception as e:
    print(f'❌ Activation error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    try:
        bot.cleanup()
        print('🧹 Browser cleanup completed')
    except:
        pass
"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'activation_info.json', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'user.password.txt', allowEmptyArchive: true
                }
            }
        }

        stage('📱 WhatsApp Success Notification - Immediate') {
            steps {
                script {
                    echo "📱 Sending immediate WhatsApp success notification..."
                }
                sh '''
                    if [ -f "user.password.txt" ]; then
                        EMAIL=$(grep "Email:" user.password.txt | cut -d':' -f2 | xargs)
                        USERNAME=$(grep "Username:" user.password.txt | cut -d':' -f2 | xargs)

                        echo "📧 Found credentials: Email=$EMAIL, Username=$USERNAME"

                        curl -X POST http://192.168.1.50:3000/webhook/jenkins \
                          -H "Content-Type: application/json" \
                          -d '{
                            "type": "success",
                            "buildNumber": "'$BUILD_NUMBER'",
                            "timestamp": "'$(date -Iseconds)'",
                            "message": "🎉 EmbyIL Account Created Successfully!",
                            "details": "Email: '$EMAIL', Username: '$USERNAME', Password: Aa123456!",
                            "stage": "Complete",
                            "credentials": {
                              "email": "'$EMAIL'",
                              "username": "'$USERNAME'",
                              "password": "Aa123456!",
                              "loginUrl": "https://client.embyiltv.io/login"
                            }
                          }' \
                          --connect-timeout 10 \
                          --max-time 30 \
                          --silent \
                          --show-error \
                          && echo "✅ WhatsApp success notification sent" \
                          || echo "⚠️ WhatsApp success notification failed"
                    else
                        echo "❌ user.password.txt not found"
                    fi
                '''
            }
        }

        stage('Step 6: Send Results') {
            when {
                expression { fileExists('user.password.txt') }
            }
            steps {
                script {
                    echo "📤 Sending final results and credentials..."
                }
                sh '''
                    echo "📧 Sending completion notification..."
                    timeout 180s ${PYTHON_PATH} -c "
import sys
print('📤 Starting notification process...')
try:
    from send_email import send_completion_email
    print('📧 Attempting to send email...')
    email_result = send_completion_email()
    print(f'📧 Email result: {email_result}')
except Exception as e:
    print(f'⚠️ Email sending failed: {e}')
    email_result = False
try:
    from send_approval_webhook import send_discord_notification
    print('📱 Attempting to send Discord notification...')
    discord_result = send_discord_notification()
    print(f'📱 Discord result: {discord_result}')
except Exception as e:
    print(f'⚠️ Discord notification failed: {e}')
    discord_result = False
if email_result or discord_result:
    print('✅ At least one notification method succeeded')
    sys.exit(0)
else:
    print('⚠️ All notification methods failed, but process completed')
    print('✅ Account creation was successful despite notification issues')
    sys.exit(0)
"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'email_sent.json', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        always {
            script {
                echo "📊 Pipeline execution completed"
            }
            sh '''
                echo ""
                echo "📋 EXECUTION SUMMARY"
                echo "===================="
                echo "📧 Email file: $([ -f email_info.txt ] && echo "✅ Created" || echo "❌ Missing")"
                echo "📝 Signup file: $([ -f signup_info.json ] && echo "✅ Created" || echo "❌ Missing")"
                echo "📬 Messages file: $([ -f message_ids.txt ] && echo "✅ Created" || echo "❌ Missing")"
                DETAIL_COUNT=$(ls message_details_*.json 2>/dev/null | wc -l)
                echo "📖 Details files: $DETAIL_COUNT found"
                echo "🔐 Activation file: $([ -f activation_info.json ] && echo "✅ Created" || echo "❌ Missing")"
                echo "🎟️ Credentials file: $([ -f user.password.txt ] && echo "✅ Created" || echo "❌ Missing")"
                echo "📤 Email log file: $([ -f email_sent.json ] && echo "✅ Created" || echo "❌ Missing")"
                echo "===================="
                if [ -f user.password.txt ]; then
                    echo "🎉 BUILD RESULT: SUCCESS - Account created!"
                else
                    echo "❌ BUILD RESULT: FAILED - Account not created"
                fi
            '''
            archiveArtifacts artifacts: '*.txt,*.json,*.png', allowEmptyArchive: true
            sh '''
                echo "🧹 Cleaning up sensitive files..."
                rm -f user.password.txt || true
                echo "✅ Cleanup completed"
            '''
        }

        success {
            script {
                echo "🎉 Pipeline completed successfully!"
            }
            sh '''
                echo "📤 Sending success notification..."
                ${PYTHON_PATH} -c "
import requests
import json
from datetime import datetime
webhook_url = '${DISCORD_WEBHOOK_URL}'
message = {
    'content': '🎉 **EmbyIL Account Creation Successful!**\\n' + \\
               '⏰ Completed at: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\\n' + \\
               '✅ New account created and activated\\n' + \\
               '📧 Credentials sent to user\\n' + \\
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

        failure {
            script {
                echo "❌ Pipeline failed!"
            }
            sh '''
                echo "📤 Sending failure notification..."
                ${PYTHON_PATH} -c "
import requests
import json
from datetime import datetime
webhook_url = '${DISCORD_WEBHOOK_URL}'
message = {
    'content': '❌ **EmbyIL Account Creation Failed!**\\n' + \\
               '⏰ Failed at: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\\n' + \\
               '🔍 Check Jenkins logs for details\\n' + \\
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
            sh '''
                echo "📱 Sending WhatsApp failure notification..."

                FAILED_STEP="Unknown"
                if [ ! -f "email_info.txt" ]; then
                    FAILED_STEP="Step 1: Email Creation"
                elif [ ! -f "signup_info.json" ]; then
                    FAILED_STEP="Step 2: Website Signup"
                elif [ ! -f "message_ids.txt" ]; then
                    FAILED_STEP="Step 3: Email Verification"
                elif [ ! -f "user.password.txt" ]; then
                    FAILED_STEP="Step 5: Account Activation"
                fi

                curl -X POST http://192.168.1.50:3000/webhook/jenkins \
                  -H "Content-Type: application/json" \
                  -d '{
                    "type": "failure",
                    "buildNumber": "'$BUILD_NUMBER'",
                    "timestamp": "'$(date -Iseconds)'",
                    "message": "❌ EmbyIL Account Creation Failed",
                    "details": "Failed at: '$FAILED_STEP'",
                    "stage": "Failed",
                    "retryInfo": "Will retry in 3 days"
                  }' \
                  --connect-timeout 10 \
                  --max-time 30 \
                  --silent \
                  --show-error \
                  || echo "⚠️ WhatsApp failure notification failed"
            '''
        }
    }
}
