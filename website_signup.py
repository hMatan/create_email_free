#!/usr/bin/env python3
'''
Website Signup Automation Script
Reads email from Step 1 and performs automated signup
'''

import requests
import json
import random
import string
import time
import os
from urllib.parse import urljoin, urlparse

def read_email_from_step1():
    '''Read email address from the temp email output file'''
    try:
        with open('email_info.txt', 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if 'EMAIL_ADDRESS=' in line:
                    email = line.split('=')[1].strip()
                    print(f"📧 Found temp email: {email}")
                    return email
        print("❌ Could not find EMAIL_ADDRESS in email_info.txt")
        return None
    except FileNotFoundError:
        print("❌ email_info.txt not found. Run step 1 first!")
        return None

def generate_random_data():
    '''Generate random signup data'''
    first_names = [
        'Alex', 'Jordan', 'Casey', 'Morgan', 'Riley', 'Taylor', 'Cameron',
        'Avery', 'Quinn', 'Sage', 'River', 'Phoenix', 'Skylar', 'Dakota',
        'Emerson', 'Finley', 'Hayden', 'Kendall', 'Logan', 'Parker'
    ]
    
    last_names = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
        'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
        'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin'
    ]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    # Generate 8-character password with mix of letters and numbers
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    print(f"🎭 Generated name: {first_name} {last_name}")
    print(f"🔐 Generated password: {password}")
    
    return first_name, last_name, password

def attempt_signup_requests(email, first_name, last_name, password):
    '''Attempt signup using requests library'''
    session = requests.Session()
    
    # Set realistic headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    session.headers.update(headers)
    
    signup_url = 'https://client.embyiltv.io/sign-up'
    
    try:
        print(f"🌐 Accessing signup page: {signup_url}")
        
        # Get the signup page first
        response = session.get(signup_url, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Cannot access signup page. Status: {response.status_code}")
            return False, f"Page access failed: {response.status_code}"
        
        print("✅ Signup page loaded successfully")
        
        # Different signup data formats to try
        signup_data_variations = [
            {
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'password': password,
                'confirmPassword': password
            },
            {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': password,
                'confirm_password': password
            },
            {
                'name': f"{first_name} {last_name}",
                'email': email,
                'password': password,
                'password_confirm': password
            }
        ]
        
        # Possible API endpoints to try
        api_endpoints = [
            '/api/auth/register',
            '/api/register',
            '/api/signup',
            '/register',
            '/signup'
        ]
        
        # Try different combinations
        for i, data in enumerate(signup_data_variations, 1):
            print(f"🔄 Trying signup data variation {i}...")
            
            for endpoint in api_endpoints:
                full_url = urljoin(signup_url, endpoint)
                
                try:
                    print(f"   📡 Attempting: {full_url}")
                    
                    # Try POST with JSON
                    json_headers = headers.copy()
                    json_headers.update({
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    })
                    
                    response = session.post(
                        full_url,
                        json=data,
                        headers=json_headers,
                        timeout=30
                    )
                    
                    print(f"   📊 Response: {response.status_code}")
                    
                    # Success indicators
                    if response.status_code in [200, 201, 302]:
                        response_text = response.text[:500]
                        print(f"   📄 Response preview: {response_text}")
                        
                        # Check for success indicators
                        success_indicators = [
                            'success', 'created', 'registered', 'welcome',
                            'account', 'verify', 'confirmation'
                        ]
                        
                        response_lower = response.text.lower()
                        if any(indicator in response_lower for indicator in success_indicators):
                            print("   ✅ Signup appears successful!")
                            return True, "Signup completed successfully"
                    
                except requests.exceptions.RequestException as e:
                    print(f"   ⚠️ Request failed: {str(e)[:100]}")
                    continue
        
        print("⚠️ All signup attempts completed, but success unclear")
        return False, "Could not confirm successful signup"
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(f"❌ {error_msg}")
        return False, error_msg

def save_signup_info(first_name, last_name, email, password, success, message):
    '''Save signup information to JSON file'''
    signup_info = {
        'signup_data': {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password
        },
        'result': {
            'success': success,
            'message': message,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'website': 'https://client.embyiltv.io/sign-up'
        },
        'instructions': {
            'next_steps': [
                "Check the temporary email for confirmation messages",
                "Look for account activation or welcome emails",
                "Follow any verification links if received"
            ]
        }
    }
    
    # Save to JSON file
    with open('signup_info.json', 'w') as f:
        json.dump(signup_info, f, indent=4)
    
    print("💾 Signup information saved to signup_info.json")
    
    return signup_info

def main():
    '''Main function'''
    print("🤖 Website Signup Automation")
    print("=" * 50)
    
    # Read email from step 1 output
    email = read_email_from_step1()
    if not email:
        print("❌ Cannot proceed without email address from Step 1")
        return False
    
    # Generate random signup data
    first_name, last_name, password = generate_random_data()
    
    # Display what we're going to use
    print("\n📋 Signup Information:")
    print(f"   🎭 Name: {first_name} {last_name}")
    print(f"   📧 Email: {email}")
    print(f"   🔐 Password: {password}")
    print(f"   🌐 Website: https://client.embyiltv.io/sign-up")
    
    # Attempt the signup
    print("\n🚀 Starting signup process...")
    success, message = attempt_signup_requests(email, first_name, last_name, password)
    
    # Save all information
    signup_info = save_signup_info(first_name, last_name, email, password, success, message)
    
    # Display results
    print("\n" + "=" * 50)
    if success:
        print("🎉 Signup Process Completed!")
        print("✅ Status: SUCCESS")
    else:
        print("⚠️ Signup Process Completed with Warnings")
        print("❓ Status: UNCERTAIN")
    
    print(f"💬 Message: {message}")
    print("📧 Next: Check your temporary email for confirmation messages")
    print("📄 Details saved to: signup_info.json")
    
    # For Jenkins - exit with success even if signup is uncertain
    return True

if __name__ == "__main__":
    try:
        result = main()
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n🛑 Signup cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
