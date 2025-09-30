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

def get_email_messages_with_retry(email_id, max_retries=10, retry_delay=30):
    """
    Get messages with retry mechanism for better reliability
    Args:
        email_id (str): The email ID from the text file
        max_retries (int): Maximum number of retry attempts (default: 10)
        retry_delay (int): Delay between retries in seconds (default: 30)
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

    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 Checking for new messages (attempt {attempt}/{max_retries})...")

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

                print(f"✅ Messages check completed!")
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
                    print("\n📧 New Messages Found!")
                    for i, message in enumerate(new_messages, 1):
                        message_id = message.get('id', 'N/A')
                        print(f"\n{'='*50}")
                        print(f"📨 New Message {i}")
                        print(f"{'='*50}")
                        print(f"🆔 Message ID: {message_id}")
                        print(f"📤 From: {message.get('from', message.get('sender', 'N/A'))}")
                        print(f"📧 To: {message.get('to', 'N/A')}")
                        print(f"📋 Subject: {message.get('subject', 'No Subject')}")
                        print(f"📅 Date: {message.get('date', message.get('created_at', 'N/A'))}")

                        # Show content if available
                        content = message.get('text', message.get('body', message.get('content', '')))
                        if content:
                            print(f"📄 Content Preview:")
                            print(f"{content[:200]}{'...' if len(content) > 200 else ''}")

                        # Save message ID to file
                        if message_id != 'N/A':
                            save_message_id(message_id, message)

                    return new_messages

                # If no new messages but we have processed messages, check if we should continue
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
                        print("⏰ Maximum retries reached - no messages received")
                        print("💡 This might indicate:")
                        print("  • Email verification was not sent")
                        print("  • Email was sent to a different address")
                        print("  • There's a delay in email delivery")
                        return None

            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                if attempt < max_retries:
                    print(f"⏳ Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                    continue
                else:
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
    print("💀 All retry attempts failed")
    return None

def get_email_messages(email_id, limit=25, offset=0):
    """
    Wrapper function for backward compatibility
    """
    return get_email_messages_with_retry(email_id, max_retries=10, retry_delay=30)

def main():
    """Main function for standalone execution"""
    print("🚀 Starting improved message checker with retry mechanism...")

    email_id, email_address = read_email_info()
    if email_id and email_address:
        print(f'📧 Checking messages for: {email_address}')
        messages = get_email_messages_with_retry(email_id)
        if messages:
            print(f'✅ Found {len(messages)} new messages')
        else:
            print('📭 No new messages found after all retries')
    else:
        print('❌ Could not read email information')
        exit(1)

if __name__ == "__main__":
    main()
