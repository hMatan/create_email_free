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
        response = requests.get(url, headers=headers)

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

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
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

def display_message_details(message_data, index=None):
    """
    Display detailed message information in a formatted way

    Args:
        message_data (dict): The message data from API
        index (int): Optional index number for display
    """

    message_id = message_data.get('id', 'N/A')

    header_text = f"📧 MESSAGE DETAILS"
    if index is not None:
        header_text = f"📧 MESSAGE {index} DETAILS"

    print(f"\n{'='*60}")
    print(header_text)
    print(f"{'='*60}")
    print(f"🆔 Message ID: {message_id}")

    # Display basic information
    print(f"📤 From: {message_data.get('from', message_data.get('sender', 'N/A'))}")
    print(f"📧 To: {message_data.get('to', message_data.get('recipient', 'N/A'))}")
    print(f"📋 Subject: {message_data.get('subject', 'No Subject')}")
    print(f"📅 Date: {message_data.get('date', message_data.get('created_at', 'N/A'))}")

    # Display content
    text_content = message_data.get('text', message_data.get('body', message_data.get('content', '')))
    if text_content:
        print(f"\n📄 Text Content:")
        print(f"{'-'*40}")
        print(text_content)
        print(f"{'-'*40}")

    # Display HTML content
    html_content = message_data.get('html', message_data.get('html_body', ''))
    if html_content:
        print(f"\n🌐 HTML Content:")
        print(f"📏 Length: {len(html_content)} characters")
        # Show first 200 characters of HTML
        html_preview = html_content[:200] + "..." if len(html_content) > 200 else html_content
        print(f"👁️ Preview: {html_preview}")

    # Display headers if available
    headers = message_data.get('headers', {})
    if headers:
        print(f"\n📋 Headers:")
        for key, value in headers.items():
            print(f"  {key}: {value}")

    # Display attachments
    attachments = message_data.get('attachments', [])
    if attachments:
        print(f"\n📎 Attachments ({len(attachments)}):")
        for i, attachment in enumerate(attachments, 1):
            print(f"  {i}. {attachment.get('filename', 'Unknown')} - {attachment.get('size', 'Unknown size')}")

    # Display additional metadata
    print(f"\n📊 Additional Info:")
    print(f"  🔒 Read: {message_data.get('read', 'Unknown')}")
    print(f"  ⭐ Flagged: {message_data.get('flagged', 'Unknown')}")

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
            json.dump(message_data, f, indent=2)

        print(f"💾 Detailed message saved to: {filename}")

    except Exception as e:
        print(f"❌ Error saving message details: {e}")

def process_stored_messages():
    """
    Process all message IDs from the file and get their details
    """

    # Read email ID (needed for API calls)
    email_id = read_email_info()
    if not email_id:
        return

    # Read message IDs we want to find
    target_message_ids = read_message_ids()
    if not target_message_ids:
        return

    print(f"\n🚀 Looking for {len(target_message_ids)} specific messages...")

    # Get all messages from the API
    all_messages = get_all_messages(email_id)
    if all_messages is None:
        return

    # Filter to only the messages we care about
    filtered_messages = filter_messages_by_ids(all_messages, target_message_ids)

    if not filtered_messages:
        print("\n📭 No matching messages found")
        print("💡 This could mean:")
        print("  - Messages have expired and been deleted")
        print("  - Message IDs in file are from a different email")
        print("  - There's a sync issue between stored IDs and current messages")
        return

    print(f"\n📧 Processing {len(filtered_messages)} matching messages...")

    for i, message in enumerate(filtered_messages, 1):
        message_id = message.get('id', 'N/A')

        print(f"\n{'#'*60}")
        print(f"Processing message {i}/{len(filtered_messages)}")
        print(f"{'#'*60}")

        # Display the details
        display_message_details(message, i)

        # Ask if user wants to save details
        save_choice = input(f"\n💾 Save detailed info for message {message_id}? (y/N): ").strip().lower()
        if save_choice == 'y':
            save_message_details(message_id, message)

        # Ask if user wants to continue (except for last message)
        if i < len(filtered_messages):
            continue_choice = input(f"\n➡️ Continue to next message? (Y/n): ").strip().lower()
            if continue_choice == 'n':
                print("⏹️ Stopping message processing")
                break

def show_all_vs_stored():
    """
    Show comparison between all messages and stored message IDs
    """

    # Read email ID
    email_id = read_email_info()
    if not email_id:
        return

    # Read stored message IDs
    stored_ids = read_message_ids()

    # Get all current messages
    all_messages = get_all_messages(email_id)
    if all_messages is None:
        return

    current_ids = [msg.get('id') for msg in all_messages if msg.get('id')]

    print(f"\n📊 Message Comparison:")
    print(f"📄 Stored message IDs: {len(stored_ids)}")
    print(f"📬 Current messages in inbox: {len(current_ids)}")

    # Find matches and differences
    matches = set(stored_ids) & set(current_ids)
    stored_only = set(stored_ids) - set(current_ids)
    current_only = set(current_ids) - set(stored_ids)

    print(f"✅ Matching messages: {len(matches)}")
    print(f"⚠️ Stored but missing from inbox: {len(stored_only)}")
    print(f"🆕 In inbox but not stored: {len(current_only)}")

    if stored_only:
        print(f"\n📭 Missing from inbox (possibly expired):")
        for msg_id in list(stored_only)[:5]:  # Show first 5
            print(f"  - {msg_id}")
        if len(stored_only) > 5:
            print(f"  ... and {len(stored_only) - 5} more")

    if current_only:
        print(f"\n🆕 New messages not in stored list:")
        for msg_id in list(current_only)[:5]:  # Show first 5
            print(f"  - {msg_id}")
        if len(current_only) > 5:
            print(f"  ... and {len(current_only) - 5} more")

def main():
    """Main function"""
    print("🚀 Starting corrected message details fetcher...")
    print("💡 Note: Using the working API endpoint to fetch all messages,")
    print("   then filtering to show only the ones from your stored list.")

    print("\n🎯 Options:")
    print("  1. Process stored message IDs (show detailed info)")
    print("  2. Compare stored vs current messages")
    print("  3. List stored message IDs only")

    choice = input("\nChoose option (1, 2, or 3): ").strip()

    if choice == "1":
        process_stored_messages()
    elif choice == "2":
        show_all_vs_stored()
    elif choice == "3":
        read_message_ids()
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
