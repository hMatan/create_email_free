import requests
import json
import os

def read_message_ids():
    """
    Read message IDs from the message_ids.txt file
    Returns:
        list: List of message IDs if successful, empty list if no file or no IDs
    """
    if not os.path.exists('message_ids.txt'):
        print("❌ Error: 'message_ids.txt' file not found!")
        print("💡 Please run 'check_messages.py' first to get some messages")
        return []

    try:
        message_ids = []
        with open('message_ids.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('MESSAGE_ID='):
                    message_id = line.split('=', 1)[1]
                    message_ids.append(message_id)

        if message_ids:
            print(f"📄 Found {len(message_ids)} message IDs in file:")
            for i, msg_id in enumerate(message_ids, 1):
                print(f"  {i}. {msg_id}")
        else:
            print("📄 message_ids.txt file exists but contains no message IDs")

        return message_ids

    except Exception as e:
        print(f"❌ Error reading message_ids.txt: {e}")
        return []

def read_email_info():
    """
    Read email ID from email_info.txt (needed for the API call)
    Returns:
        str: email_id if successful, None if failed
    """
    if not os.path.exists('email_info.txt'):
        print("❌ Error: 'email_info.txt' file not found!")
        print("💡 Please run 'create_email.py' first to create a temporary email")
        return None

    try:
        email_id = None
        with open('email_info.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('EMAIL_ID='):
                    email_id = line.split('=', 1)[1]
                    break

        if email_id:
            print(f"📧 Using email ID from file: {email_id}")
            return email_id
        else:
            print("❌ Error: No EMAIL_ID found in email_info.txt")
            return None

    except Exception as e:
        print(f"❌ Error reading email_info.txt: {e}")
        return None

def get_all_messages(email_id, limit=25, offset=0):
    """
    Get all messages for the email using the correct API endpoint
    Args:
        email_id (str): The email ID from email_info.txt
        limit (int): Maximum number of messages to retrieve (default: 25)
        offset (int): Number of messages to skip (default: 0)
    Returns:
        list: List of all messages if successful, None if failed
    """
    # Use the correct API endpoint that we know works
    url = f'https://boomlify-temp-mail-api2.p.rapidapi.com/api/v1/emails/{email_id}/messages?limit={limit}&offset={offset}'

    # Headers
    headers = {
        'x-rapidapi-host': 'boomlify-temp-mail-api2.p.rapidapi.com',
        'x-rapidapi-key': 'c815bd8438mshaec3510f9c39d67p1b034bjsn3f4575728890'
    }

    try:
        print(f"🔄 Fetching all messages from email...")

        # Make the GET request
        response = requests.get(url, headers=headers, timeout=30)

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

            print(f"✅ Retrieved {len(messages)} total messages from API")
            return messages
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def filter_messages_by_ids(all_messages, target_message_ids):
    """
    Filter messages to only include those with IDs from our list
    Args:
        all_messages (list): All messages from the API
        target_message_ids (list): Message IDs we want to find
    Returns:
        list: Filtered messages that match our IDs
    """
    filtered_messages = []
    found_ids = []

    for message in all_messages:
        message_id = message.get('id')
        if message_id in target_message_ids:
            filtered_messages.append(message)
            found_ids.append(message_id)

    missing_ids = set(target_message_ids) - set(found_ids)

    print(f"✅ Found {len(filtered_messages)} messages matching our stored IDs")

    if missing_ids:
        print(f"⚠️ Missing {len(missing_ids)} messages (may have expired or been deleted):")
        for missing_id in missing_ids:
            print(f"  - {missing_id}")

    return filtered_messages

def save_message_details(message_id, message_data):
    """
    Save detailed message information to a file
    Args:
        message_id (str): The message ID
        message_data (dict): The detailed message data
    """
    try:
        filename = f"message_details_{message_id}.json"
        with open(filename, 'w') as f:
            json.dump(message_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Detailed message saved to: {filename}")
        return True

    except Exception as e:
        print(f"❌ Error saving message details: {e}")
        return False

def process_message_details():
    """
    Process all message IDs from the file and get their details automatically for Jenkins
    Returns True if successful, False otherwise
    """
    print("🔄 Starting automated message details processing...")

    # Read email ID (needed for API calls)
    email_id = read_email_info()
    if not email_id:
        print("❌ Could not read email ID")
        return False

    # Read message IDs we want to find
    target_message_ids = read_message_ids()
    if not target_message_ids:
        print("❌ No message IDs found to process")
        return False

    print(f"🚀 Processing {len(target_message_ids)} message IDs for Jenkins...")

    # Get all messages from the API
    all_messages = get_all_messages(email_id)
    if all_messages is None:
        print("❌ Failed to retrieve messages from API")
        return False

    # Filter to only the messages we care about
    filtered_messages = filter_messages_by_ids(all_messages, target_message_ids)

    if not filtered_messages:
        print("❌ No matching messages found")
        print("💡 This could mean messages have expired or there's a sync issue")
        return False

    print(f"✅ Found {len(filtered_messages)} matching messages")

    # Process and save each message automatically
    saved_count = 0
    for i, message in enumerate(filtered_messages, 1):
        message_id = message.get('id', 'N/A')

        print(f"📧 Processing message {i}/{len(filtered_messages)}: {message_id}")

        # Display brief details
        subject = message.get('subject', 'No Subject')
        sender = message.get('from', message.get('sender', 'N/A'))
        print(f"   📋 Subject: {subject}")
        print(f"   📤 From: {sender}")

        # Automatically save the message details
        if save_message_details(message_id, message):
            saved_count += 1
            print(f"   ✅ Saved details for message {message_id}")
        else:
            print(f"   ❌ Failed to save message {message_id}")

    print(f"\n🎉 Processing completed!")
    print(f"✅ Successfully processed {saved_count}/{len(filtered_messages)} messages")

    return saved_count > 0

def main():
    """Main function for standalone execution"""
    print("🚀 Starting message details processor...")
    print("💡 This will automatically process all stored message IDs")

    result = process_message_details()

    if result:
        print("\n🎉 SUCCESS!")
        print("✅ All message details have been processed and saved")
    else:
        print("\n❌ FAILED!")
        print("💡 Check the logs above for specific error details")

if __name__ == "__main__":
    main()
