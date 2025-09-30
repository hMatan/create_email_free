import requests
import json
import os
import time
import datetime

def read_email_info():
    """
    Read email information from the text file created by create_email.py
    Returns:
        tuple: (email_id, email_address) if successful, (None, None) if failed
    """
    if not os.path.exists('email_info.txt'):
        print("❌ Error: 'email_info.txt' file not found!")
        print("💡 Please run 'create_email.py' first to create a temporary email")
        return None, None

    try:
        email_id = None
        email_address = None
        expires_at = None

        with open('email_info.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('EMAIL_ID='):
                    email_id = line.split('=', 1)[1]
                elif line.startswith('EMAIL_ADDRESS='):
                    email_address = line.split('=', 1)[1]
                elif line.startswith('EXPIRES_AT='):
                    expires_at = line.split('=', 1)[1]

        if email_id and email_address:
            print("📂 Email information loaded from file:")
            print(f"📧 Email Address: {email_address}")
            print(f"🆔 Email ID: {email_id}")
            if expires_at:
                print(f"⏰ Expires at: {expires_at}")
            return email_id, email_address
        else:
            print("❌ Error: Invalid email information in file")
            return None, None

    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None, None

def read_processed_messages():
    """
    Read already processed message IDs from file
    Returns:
        set: Set of processed message IDs
    """
    processed_ids = set()
    if os.path.exists('message_ids.txt'):
        try:
            with open('message_ids.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('MESSAGE_ID='):
                        message_id = line.split('=', 1)[1]
                        processed_ids.add(message_id)
        except Exception as e:
            print(f"⚠️ Warning: Error reading message_ids.txt: {e}")

    return processed_ids

def save_message_id(message_id, message_info):
    """
    Save message ID and basic info to text file
    Args:
        message_id (str): The message ID
        message_info (dict): Message information dictionary
    """
    try:
        with open('message_ids.txt', 'a') as f:
            # Write message ID and basic info
            f.write(f"MESSAGE_ID={message_id}\n")
            f.write(f"FROM={message_info.get('from', 'N/A')}\n")
            f.write(f"SUBJECT={message_info.get('subject', 'No Subject')}\n")
            f.write(f"DATE={message_info.get('date', message_info.get('created_at', 'N/A'))}\n")
            f.write(f"PROCESSED_AT={json.dumps({'timestamp': datetime.datetime.now().isoformat()})}\n")
            f.write("---\n")  # Separator between messages

        print(f"💾 Message ID saved to message_ids.txt: {message_id}")

    except Exception as e:
        print(f"❌ Error saving message ID: {e}")

def get_email_messages_with_retry(email_id, max_retries=15, retry_delay=45):
    """
    Get messages with retry mechanism for better reliability
    Args:
        email_id (str): The email ID from the text file
        max_retries (int): Maximum number of retry attempts (default: 15)
        retry_delay (int): Delay between retries in seconds (default: 45)
    Returns:
        list: List of new messages if successful, None if all retries failed
    """
    if not email_id:
        print("❌ Error: No email ID provided")
        return None

    # Read already processed message IDs
    processed_ids = read_processed_messages()

    # API endpoint with email_id
    url = f'https://boomlify-temp-mail-api2.p.rapidapi.com/api/v1/emails/{email_id}/messages?limit=25&offset=0'

    # Headers
    headers = {
        'x-rapidapi-host': 'boomlify-temp-mail-api2.p.rapidapi.com',
        'x-rapidapi-key': 'c815bd8438mshaec3510f9c39d67p1b034bjsn3f4575728890'
    }

    print(f"🔄 Starting enhanced message checking with {max_retries} retries...")
    print(f"⏰ Retry delay: {retry_delay} seconds")
    print(f"📬 Already processed: {len(processed_ids)} messages")

    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n🔍 Checking for messages (attempt {attempt}/{max_retries})...")

            # Make the GET request
            response = requests.get(url, headers=headers, timeout=30)

            # Debug information
            print(f"📊 Response status: {response.status_code}")

            # Check if request was successful
            if response.status_code == 200:
                # Parse the JSON response
                result = response.json()

                # Handle both possible response structures
                messages = []
                if isinstance(result, dict):
                    messages = result.get('messages', result.get('data', []))
                elif isinstance(result, list):
                    messages = result

                print(f"📬 Total messages found: {len(messages)}")

                # Filter new messages
                new_messages = []
                for message in messages:
                    message_id = message.get('id')
                    if message_id and message_id not in processed_ids:
                        new_messages.append(message)

                print(f"🆕 New messages: {len(new_messages)}")

                # If we found new messages, return them immediately
                if new_messages:
                    print("\n🎉 NEW MESSAGES FOUND!")
                    print("=" * 60)

                    for i, message in enumerate(new_messages, 1):
                        message_id = message.get('id', 'N/A')
                        sender = message.get('from', message.get('sender', 'N/A'))
                        subject = message.get('subject', 'No Subject')
                        date = message.get('date', message.get('created_at', 'N/A'))

                        print(f"\n📨 Message {i}/{len(new_messages)}")
                        print("-" * 40)
                        print(f"🆔 ID: {message_id}")
                        print(f"📤 From: {sender}")
                        print(f"📋 Subject: {subject}")
                        print(f"📅 Date: {date}")

                        # Show content preview
                        content = message.get('text', message.get('body', message.get('content', '')))
                        if content:
                            preview = content.replace('\n', ' ').strip()
                            if len(preview) > 100:
                                preview = preview[:100] + "..."
                            print(f"📄 Preview: {preview}")

                        # Save message ID to file
                        if message_id != 'N/A':
                            save_message_id(message_id, message)

                    print("=" * 60)
                    print(f"✅ Successfully found {len(new_messages)} new messages!")
                    return new_messages

                # If no new messages but we have processed messages, continue retrying
                elif len(messages) > 0:
                    print("📭 No new messages (all messages already processed)")
                    if attempt < max_retries:
                        print(f"⏳ Waiting {retry_delay} seconds before next attempt...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print("⏰ Maximum retries reached with no new messages")
                        return []

                # If no messages at all, continue retrying
                else:
                    print("📭 No messages found in mailbox")
                    if attempt < max_retries:
                        print(f"⏳ Waiting {retry_delay} seconds before retry {attempt + 1}...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print("\n⏰ MAXIMUM RETRIES REACHED")
                        print("=" * 50)
                        print("❌ No messages received after all attempts")
                        print("\n💡 Possible reasons:")
                        print("  • Email verification was not sent")
                        print("  • Email was sent to a different address")  
                        print("  • Delay in email delivery system")
                        print("  • Email service provider filtering")
                        print("\n🔧 Suggestions:")
                        print("  • Check if registration was successful")
                        print("  • Verify the email address is correct")
                        print("  • Try creating a new temporary email")
                        return None

            elif response.status_code == 404:
                print("❌ Email ID not found - email may have expired")
                return None
            elif response.status_code == 429:
                print("⚠️ Rate limit exceeded - waiting longer...")
                if attempt < max_retries:
                    print(f"⏳ Extended wait: {retry_delay * 2} seconds...")
                    time.sleep(retry_delay * 2)
                    continue
                else:
                    return None
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"📄 Response: {response.text[:200]}...")
                if attempt < max_retries:
                    print(f"⏳ Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return None

        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout (attempt {attempt})")
            if attempt < max_retries:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
                continue
            else:
                print("❌ All requests timed out")
                return None

        except requests.exceptions.ConnectionError:
            print(f"🌐 Connection error (attempt {attempt})")
            if attempt < max_retries:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
                continue
            else:
                print("❌ All connection attempts failed")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed (attempt {attempt}): {e}")
            if attempt < max_retries:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
                continue
            else:
                return None

        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response (attempt {attempt}): {e}")
            if attempt < max_retries:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
                continue
            else:
                return None

        except Exception as e:
            print(f"❌ Unexpected error (attempt {attempt}): {e}")
            if attempt < max_retries:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
                continue
            else:
                return None

    # If we get here, all retries failed
    print("💀 All retry attempts exhausted")
    return None

def get_email_messages(email_id, limit=25, offset=0):
    """
    Original function for backward compatibility
    """
    print("📞 Using compatibility mode - calling enhanced version...")
    return get_email_messages_with_retry(email_id, max_retries=10, retry_delay=30)

def main():
    """Main function for standalone execution"""
    print("🌟 Enhanced EmbyIL Message Checker")
    print("=" * 60)
    print("🚀 Starting improved message checker with retry mechanism...")

    email_id, email_address = read_email_info()
    if email_id and email_address:
        print(f'\n📧 Checking messages for: {email_address}')
        print(f'🔧 Using enhanced retry mechanism')

        messages = get_email_messages_with_retry(email_id)

        if messages:
            print(f'\n🎉 SUCCESS!')
            print(f'✅ Found {len(messages)} new messages')
            print("📋 Messages have been saved to message_ids.txt")
        elif messages == []:
            print(f'\n📭 No new messages found (but some messages exist)')
        else:
            print('\n❌ No messages found after all retries')
            print('💡 Check if the registration process completed successfully')
    else:
        print('❌ Could not read email information')
        print('💡 Make sure create_email.py ran successfully first')
        exit(1)

if __name__ == "__main__":
    main()
