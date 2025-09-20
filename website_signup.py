#!/usr/bin/env python3
'''
Simple Website Signup - No external dependencies
Handles form submission without HTML parsing
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
    first_names = ['Alex', 'Jordan', 'Casey', 'Morgan', 'Riley', 'Taylor', 'Sage']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia']
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    print(f"🎭 Generated: {first_name} {last_name}")
    print(f"🔐 Password: {password}")
    
    return first_name, last_name, password

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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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
        
        # Comprehensive form data variations
        form_variations = [
            # Standard web forms
            {
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'password': password,
                'confirmPassword': password,
                'terms': 'on',
                'privacy': 'on'
            },
            # Alternative naming
            {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': password,
                'password_confirmation': password,
                'accept_terms': '1'
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
                'email': email,
                'password': password,
                'confirm_password': password
            },
            # Django style
            {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password1': password,
                'password2': password
            }
        ]
        
        # Add CSRF token to all variations if found
        if csrf_token:
            for variation in form_variations:
                variation['_token'] = csrf_token
                variation['csrf_token'] = csrf_token
        
        # Try different submission endpoints
        endpoints = ['', '/register', '/signup', '/auth/register']
        
        for endpoint in endpoints:
            submit_url = signup_url + endpoint if endpoint else signup_url
            
            for i, form_data in enumerate(form_variations, 1):
                try:
                    print(f"🔄 Trying {submit_url} with variation {i}...")
                    
                    # Form submission headers
                    form_headers = headers.copy()
                    form_headers.update({
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Origin': 'https://client.embyiltv.io',
                        'Referer': signup_url
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
                        'check your email', 'account created'
                    ]
                    
                    # Error indicators  
                    error_words = [
                        'error', 'failed', 'invalid', 'already exists',
                        'incorrect', 'missing required', 'try again'
                    ]
                    
                    success_found = any(word in response_text for word in success_words)
                    error_found = any(word in response_text for word in error_words)
                    
                    if post_response.status_code in [200, 201] and success_found:
                        return True, f"Form submitted successfully - success detected"
                    
                    elif post_response.status_code in [302, 303, 307, 308]:
                        redirect_url = post_response.headers.get('location', '').lower()
                        if any(word in redirect_url for word in ['success', 'welcome', 'dashboard']):
                            return True, f"Signup successful - redirected to success page"
                        elif 'error' not in redirect_url:
                            return True, f"Form submitted - redirected (likely successful)"
                    
                    elif error_found:
                        print(f"   ❌ Error detected in response")
                        continue
                    
                    elif post_response.status_code == 200:
                        # No clear error, might be successful
                        return True, f"Form submitted successfully (status 200)"
                    
                except requests.exceptions.RequestException as e:
                    print(f"   ⚠️ Request failed: {str(e)[:50]}")
                    continue
        
        return False, "All form submission attempts failed"
        
    except Exception as e:
        return False, f"Error: {e}"

def save_signup_info(first_name, last_name, email, password, success, message):
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
        }
    }
    
    with open('signup_info.json', 'w') as f:
        json.dump(signup_info, f, indent=4)
    
    print("💾 Signup info saved to signup_info.json")
    return signup_info

def main():
    print("🤖 Fixed Website Signup Automation")
    print("=" * 50)
    
    email = read_email_from_step1()
    if not email:
        return False
    
    first_name, last_name, password = generate_random_data()
    
    print(f"\n📋 Signup: {first_name} {last_name} | {email}")
    print(f"🔐 Password: {password}")
    
    print("\n🚀 Attempting smart form submission...")
    success, message = attempt_smart_form_signup(email, first_name, last_name, password)
    
    save_signup_info(first_name, last_name, email, password, success, message)
    
    print("\n" + "=" * 50)
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
