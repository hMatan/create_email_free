import requests
import json

def create_temp_email():
    """
    Create a temporary email using the Boomlify API and save email ID and address to text file
    """

    # API endpoint
    url = 'https://boomlify-temp-mail-api2.p.rapidapi.com/api/v1/emails/create?time=10min'

    # Headers
    headers = {
        'Content-Type': 'application/json',
        'x-rapidapi-host': 'boomlify-temp-mail-api2.p.rapidapi.com',
        'x-rapidapi-key': 'c815bd8438mshaec3510f9c39d67p1b034bjsn3f4575728890'
    }

    # Data payload
    data = {
        "key1": "value",
        "key2": "value"
    }

    try:
        # Make the POST request
        response = requests.post(url, headers=headers, json=data)

        # Check if request was successful (200 or 201 for creation)
        if response.status_code in [200, 201]:
            # Parse the JSON response
            result = response.json()

            # Extract email ID and address from the response structure
            if 'success' in result and result['success'] and 'email' in result:
                email_data = result['email']
                email_id = email_data.get('id')
                email_address = email_data.get('address')
                expires_at = email_data.get('expires_at')

                print("✅ Temporary email created successfully!")
                print(f"📧 Email Address: {email_address}")
                print(f"🆔 Email ID: {email_id}")
                print(f"⏰ Expires at: {expires_at}")

                # Save to text file
                with open('email_info.txt', 'w') as f:
                    f.write(f"EMAIL_ID={email_id}\n")
                    f.write(f"EMAIL_ADDRESS={email_address}\n")
                    f.write(f"EXPIRES_AT={expires_at}\n")

                print("💾 Email information saved to 'email_info.txt'")

                return email_id, email_address
            else:
                print("❌ Unexpected response structure")
                print(json.dumps(result, indent=2))
                return None, None

        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None, None
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        return None, None

def main():
    """Main function"""
    print("🚀 Creating temporary email...")
    email_id, email_address = create_temp_email()

    if email_id and email_address:
        print(f"\n🎉 Success!")
        print(f"📧 You can now send emails to: {email_address}")
        print("📂 Email details saved to: email_info.txt")
        print("\n📝 Next step: Run 'check_messages.py' to check for new messages")
    else:
        print("\n❌ Failed to create temporary email")

if __name__ == "__main__":
    main()
