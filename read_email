import requests
import json
import os

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
            f.write(f"PROCESSED_AT={json.dumps({'timestamp': __import__('datetime').datetime.now().isoformat()})}\n")
            f.write("---\n")  # Separator between messages

        print(f"💾 Message ID saved to message_ids.txt: {message_id}")

    except Exception as e:
        print(f"❌ Error saving message ID: {e}")

def get_email_messages(email_id, limit=25, offset=0):
    """
    Get messages for a temporary email using the Boomlify API and save new message IDs

    Args:
        email_id (str): The email ID from the text file
        limit (int): Maximum number of messages to retrieve (default: 25)
        offset (int): Number of messages to skip (default: 0)

    Returns:
        list: List of new messages if successful, None if failed
    """

    if not email_id:
        print("❌ Error: No email ID provided")
        return None

    # Read already processed message IDs
    processed_ids = read_processed_messages()

    # API endpoint with email_id
    url = f'https://boomlify-temp-mail-api2.p.rapidapi.com/api/v1/emails/{email_id}/messages?limit={limit}&offset={offset}'

    # Headers
    headers = {
        'x-rapidapi-host': 'boomlify-temp-mail-api2.p.rapidapi.com',
        'x-rapidapi-key': 'c815bd8438mshaec3510f9c39d67p1b034bjsn3f4575728890'
    }

    try:
        print("🔄 Checking for new messages...")

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

            print(f"✅ Messages check completed!")
            print(f"📬 Total messages found: {len(messages)}")

            # Filter new messages
            new_messages = []
            for message in messages:
                message_id = message.get('id')
                if message_id and message_id not in processed_ids:
                    new_messages.append(message)

            print(f"🆕 New messages: {len(new_messages)}")

            # Display and save new messages
            if new_messages:
                print("\n📧 New Messages:")
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
                        print(f"📄 Content:")
                        print(f"{content}")

                    # Show HTML content info if available
                    html_content = message.get('html', message.get('html_body', ''))
                    if html_content:
                        print(f"🌐 HTML Content: Available ({len(html_content)} characters)")

                    # Show attachments if any
                    attachments = message.get('attachments', [])
                    if attachments:
                        print(f"📎 Attachments: {len(attachments)} file(s)")

                    # Save message ID to file
                    if message_id != 'N/A':
                        save_message_id(message_id, message)

            elif len(messages) > 0:
                print("📭 No new messages (all messages already processed)")
                print(f"💡 Processed message IDs are stored in message_ids.txt")
            else:
                print("📭 No messages found")
                print("💡 Tip: Send an email to your temporary address and run this script again")

            return new_messages

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

def show_message_ids_summary():
    """
    Show summary of all processed message IDs
    """
    if not os.path.exists('message_ids.txt'):
        print("📄 No message_ids.txt file found - no messages processed yet")
        return

    try:
        message_count = 0
        with open('message_ids.txt', 'r') as f:
            content = f.read()
            message_count = content.count('MESSAGE_ID=')

        print(f"\n📊 Message IDs Summary:")
        print(f"📄 File: message_ids.txt")
        print(f"📈 Total processed messages: {message_count}")

        # Show last few message IDs
        message_ids = []
        with open('message_ids.txt', 'r') as f:
            for line in f:
                if line.startswith('MESSAGE_ID='):
                    message_id = line.split('=', 1)[1].strip()
                    message_ids.append(message_id)

        if message_ids:
            print(f"\n🆔 Recent Message IDs:")
            for i, msg_id in enumerate(message_ids[-5:], 1):  # Show last 5
                print(f"  {i}. {msg_id}")

            if len(message_ids) > 5:
                print(f"  ... and {len(message_ids) - 5} more")

    except Exception as e:
        print(f"❌ Error reading message summary: {e}")

def check_messages_continuously():
    """
    Continuously check for messages with user input
    """
    email_id, email_address = read_email_info()

    if not email_id:
        return

    print(f"\n🔄 Monitoring messages for: {email_address}")
    print("\n🎯 Options:")
    print("  1. Check once and exit")
    print("  2. Check continuously (press Enter to check again, 'q' to quit)")
    print("  3. Show message IDs summary")

    choice = input("\nChoose option (1, 2, or 3): ").strip()

    if choice == "1":
        get_email_messages(email_id)
        show_message_ids_summary()
    elif choice == "2":
        print("\n🔄 Continuous monitoring started...")
        print("💡 Press Enter to check for new messages, type 'q' and Enter to quit, 's' for summary")

        while True:
            user_input = input("\nPress Enter to check messages ('q' to quit, 's' for summary): ").strip().lower()

            if user_input == 'q':
                print("👋 Goodbye!")
                break
            elif user_input == 's':
                show_message_ids_summary()
            else:
                get_email_messages(email_id)
    elif choice == "3":
        show_message_ids_summary()
    else:
        print("❌ Invalid choice, checking once...")
        get_email_messages(email_id)
        show_message_ids_summary()

def main():
    """Main function"""
    print("🚀 Starting message checker with ID tracking...")
    check_messages_continuously()

if __name__ == "__main__":
    main()
