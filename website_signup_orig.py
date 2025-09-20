#!/usr/bin/env python3
'''
Website Signup Automation with Enhanced Password Requirements
Password: 8 characters, at least 1 capital letter, 1 number, and 1 ! symbol
'''

import requests
import json
import random
import string
import time
import re

def read_email_from_step1():
    try:
        with open('email_info.txt', 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if 'EMAIL_ADDRESS=' in line:
                    email = line.split('=')[1].strip()
                    print(f"📧 Found temp email: {email}")
                    return email
        return None
    except FileNotFoundError:
        print("❌ email_info.txt not found")
        return None

def generate_random_data():
    first_names = ['Alex', 'Jordan', 'Casey', 'Morgan', 'Riley', 'Taylor', 'Sage', 'River', 'Blake', 'Quinn']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson', 'Moore']
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    # Generate password with specific requirements:
    # - 8 characters total
    # - At least 1 capital letter
    # - At least 1 number  
    # - At least 1 ! symbol
    password = generate_secure_password()
    
    print(f"🎭 Generated: {first_name} {last_name}")
    print(f"🔐 Password: {password}")
    
    return first_name, last_name, password

def generate_secure_password():
    '''Generate 8-character password with: 1+ capital, 1+ number, 1+ ! symbol'''
    
    # Required characters
    capital_letter = random.choice(string.ascii_uppercase)  # A-Z
    number = random.choice(string.digits)                   # 0-9
    exclamation = '!'                                       # !
    
    # Fill remaining 5 positions with mix of letters and numbers
    remaining_chars = []
    for _ in range(5):
        char_type = random.choice(['lower', 'upper', 'digit'])
        if char_type == 'lower':
            remaining_chars.append(random.choice(string.ascii_lowercase))
        elif char_type == 'upper':
            remaining_chars.append(random.choice(string.ascii_uppercase))
        else:  # digit
            remaining_chars.append(random.choice(string.digits))
    
    # Combine all characters
    all_chars = [capital_letter, number, exclamation] + remaining_chars
    
    # Shuffle to randomize positions
    random.shuffle(all_chars)
    
    password = ''.join(all_chars)
    
    # Verify password meets requirements
    has_capital = any(c.isupper() for c in password)
    has_number = any(c.isdigit() for c in password)
    has_exclamation = '!' in password
    is_8_chars = len(password) == 8
    
    if not (has_capital and has_number and has_exclamation and is_8_chars):
        # Fallback: force requirements if shuffle didn't work
        print("🔄 Regenerating password to meet requirements...")
        return generate_secure_password()
    
    print(f"✅ Password validation: Length={len(password)}, Capital={has_capital}, Number={has_number}, Exclamation={has_exclamation}")
    
    return password

def extract_csrf_token(html_content):
    '''Extract CSRF token from HTML if present'''
    patterns = [
        r'<input[^>]*name=["\']_token["\'][^>]*value=["\']([^"\']*)["\']',
        r'<input[^>]*name=["\']csrf_token["\'][^>]*value=["\']([^"\']*)["\']',
        r'<meta[^>]*name=["\']csrf-token["\'][^>]*content=["\']([^"\']*)["\']',
        r'csrf["\']\\s*:\\s*["\']([^"\']*)["\']'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            token = match.group(1)
            print(f"🛡️ Found CSRF token: {token[:20]}...")
            return token
    
    return None

def attempt_smart_form_signup(email, first_name, last_name, password):
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive'
    }
    
    session.headers.update(headers)
    signup_url = 'https://client.embyiltv.io/sign-up'
    
    try:
        print(f"🌐 Loading signup page...")
        response = session.get(signup_url, timeout=30)
        
        if response.status_code != 200:
            return False, f"Cannot access page: {response.status_code}"
        
        print("✅ Page loaded successfully")
        
        # Extract CSRF token if present
        csrf_token = extract_csrf_token(response.text)
        
        # Comprehensive form data variations with secure password
        form_variations = [
            # Standard web forms
            {
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'password': password,
                'confirmPassword': password,
                'passwordConfirm': password,
                'terms': 'on',
                'privacy': 'on',
                'agree': '1'
            },
            # Alternative naming
            {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': password,
                'password_confirmation': password,
                'confirm_password': password,
                'accept_terms': '1',
                'accept_privacy': '1'
            },
            # Rails-style
            {
                'user[first_name]': first_name,
                'user[last_name]': last_name,
                'user[email]': email,
                'user[password]': password,
                'user[password_confirmation]': password
            },
            # Single name field
            {
                'name': f"{first_name} {last_name}",
                'fullName': f"{first_name} {last_name}",
                'email': email,
                'password': password,
                'confirm_password': password,
                'password_confirm': password
            },
            # Django style
            {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password1': password,
                'password2': password
            },
            # Common alternative field names
            {
                'fname': first_name,
                'lname': last_name,
                'email_address': email,
                'pwd': password,
                'pwd_confirm': password,
                'terms_accepted': 'true'
            },
            # Registration form style
            {
                'registration[first_name]': first_name,
                'registration[last_name]': last_name,
                'registration[email]': email,
                'registration[password]': password,
                'registration[password_confirmation]': password,
                'registration[terms]': '1'
            }
        ]
        
        # Add CSRF token to all variations if found
        if csrf_token:
            for variation in form_variations:
                variation['_token'] = csrf_token
                variation['csrf_token'] = csrf_token
                variation['authenticity_token'] = csrf_token
        
        # Try different submission endpoints
        endpoints = ['', '/register', '/signup', '/auth/register', '/user/register', '/account/register']
        
        for endpoint in endpoints:
            submit_url = signup_url + endpoint if endpoint else signup_url
            
            for i, form_data in enumerate(form_variations, 1):
                try:
                    print(f"🔄 Trying {submit_url} with variation {i}...")
                    print(f"   🔐 Using password: {password}")
                    
                    # Form submission headers
                    form_headers = headers.copy()
                    form_headers.update({
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Origin': 'https://client.embyiltv.io',
                        'Referer': signup_url,
                        'X-Requested-With': 'XMLHttpRequest'
                    })
                    
                    # Submit form
                    post_response = session.post(
                        submit_url, 
                        data=form_data, 
                        headers=form_headers, 
                        timeout=30,
                        allow_redirects=True
                    )
                    
                    print(f"   📊 Status: {post_response.status_code}")
                    
                    # Check response
                    response_text = post_response.text.lower()
                    
                    # Success indicators
                    success_words = [
                        'success', 'welcome', 'created', 'registered', 
                        'thank you', 'confirmation', 'verify email',
                        'check your email', 'account created', 'registration successful',
                        'sign up successful', 'signup successful'
                    ]
                    
                    # Error indicators  
                    error_words = [
                        'error', 'failed', 'invalid', 'already exists',
                        'incorrect', 'missing required', 'try again',
                        'password', 'weak password', 'requirements'
                    ]
                    
                    success_found = any(word in response_text for word in success_words)
                    error_found = any(word in response_text for word in error_words)
                    
                    # Check for password-specific errors
                    password_errors = [
                        'password must contain', 'password should contain',
                        'password requirements', 'password too weak',
                        'capital letter', 'number', 'special character'
                    ]
                    
                    password_error_found = any(error in response_text for error in password_errors)
                    
                    if password_error_found:
                        print(f"   ⚠️ Password requirements error detected")
                        # Don't return here, try other variations
                        continue
                    
                    if post_response.status_code in [200, 201] and success_found:
                        return True, f"Form submitted successfully - success detected (variation {i})"
                    
                    elif post_response.status_code in [302, 303, 307, 308]:
                        redirect_url = post_response.headers.get('location', '').lower()
                        if any(word in redirect_url for word in ['success', 'welcome', 'dashboard', 'profile']):
                            return True, f"Signup successful - redirected to success page (variation {i})"
                        elif 'error' not in redirect_url and 'login' not in redirect_url:
                            return True, f"Form submitted - redirected (likely successful, variation {i})"
                    
                    elif error_found and not password_error_found:
                        print(f"   ❌ General error detected in response")
                        continue
                    
                    elif post_response.status_code == 200 and not error_found:
                        # No clear error, might be successful
                        return True, f"Form submitted successfully (status 200, variation {i})"
                    
                except requests.exceptions.RequestException as e:
                    print(f"   ⚠️ Request failed: {str(e)[:50]}")
                    continue
        
        return False, "All form submission attempts failed - password requirements may not be met"
        
    except Exception as e:
        return False, f"Error: {e}"

def save_signup_info(first_name, last_name, email, password, success, message):
    signup_info = {
        'signup_data': {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password,
            'password_requirements': {
                'length': len(password),
                'has_capital': any(c.isupper() for c in password),
                'has_number': any(c.isdigit() for c in password),
                'has_exclamation': '!' in password,
                'meets_requirements': (
                    len(password) == 8 and
                    any(c.isupper() for c in password) and
                    any(c.isdigit() for c in password) and
                    '!' in password
                )
            }
        },
        'result': {
            'success': success,
            'message': message,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'website': 'https://client.embyiltv.io/sign-up'
        },
        'instructions': {
            'password_policy': '8 characters, 1+ capital letter, 1+ number, 1+ exclamation mark (!)',
            'next_steps': [
                "Check the temporary email for confirmation messages",
                "Look for account activation or welcome emails",
                "Follow any verification links if received"
            ]
        }
    }
    
    with open('signup_info.json', 'w') as f:
        json.dump(signup_info, f, indent=4)
    
    print("💾 Signup info saved to signup_info.json")
    return signup_info

def main():
    print("🤖 Enhanced Website Signup Automation")
    print("🔐 Password Policy: 8 chars, 1+ capital, 1+ number, 1+ !")
    print("=" * 60)
    
    email = read_email_from_step1()
    if not email:
        return False
    
    first_name, last_name, password = generate_random_data()
    
    # Validate password meets requirements
    has_capital = any(c.isupper() for c in password)
    has_number = any(c.isdigit() for c in password)
    has_exclamation = '!' in password
    is_8_chars = len(password) == 8
    
    print(f"\n📋 Signup Information:")
    print(f"   🎭 Name: {first_name} {last_name}")
    print(f"   📧 Email: {email}")
    print(f"   🔐 Password: {password}")
    print(f"   ✅ Length: {len(password)}/8")
    print(f"   ✅ Capital: {has_capital}")
    print(f"   ✅ Number: {has_number}")
    print(f"   ✅ Exclamation: {has_exclamation}")
    
    if not (has_capital and has_number and has_exclamation and is_8_chars):
        print("❌ Password does not meet requirements! Regenerating...")
        return False
        
    print("\n🚀 Starting enhanced form submission...")
    success, message = attempt_smart_form_signup(email, first_name, last_name, password)
    
    save_signup_info(first_name, last_name, email, password, success, message)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Signup completed successfully!")
    else:
        print("⚠️ Signup had issues, but continuing...")
    
    print(f"💬 {message}")
    print("📧 Check temporary email for confirmation")
    
    return True

if __name__ == "__main__":
    try:
        main()
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        exit(0)  # Continue pipeline even on errors
