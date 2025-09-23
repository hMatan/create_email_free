# Save activation details
activation_info = {
    'timestamp': datetime.datetime.now().isoformat(),
    'activation_link': activation_link,
    'email': email,
    'website_signup_password': password,
    'username': username,
    'new_account_password': 'rh1234',
    'browser_used': self.browser_type,
    'success': True,
    'note': 'Used website signup password for activation, then set new account password'
}

# Save with timestamp
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f"activation_{timestamp}.json"

with open(filename, 'w') as f:
    json.dump(activation_info, f, indent=2)
print(f"💾 Activation info saved to: {filename}")

# Also save as activation_info.json for Jenkins
with open('activation_info.json', 'w') as f:
    json.dump(activation_info, f, indent=2)
print("💾 Also saved as: activation_info.json")

# Create user.password.txt with final credentials
user_password_content = f"""EmbyIL Account Credentials
========================
Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Email: {email}
Username: {username}
Password: rh1234

Login URL: https://client.embyiltv.io/login
Account Status: Activated
"""

with open('user.password.txt', 'w') as f:
    f.write(user_password_content)
print("💾 Final credentials saved to: user.password.txt")

print("🎉 Account activation completed successfully!")
print(f"📋 Final credentials:")
print(f"   Email: {email}")
print(f"   Username: {username}")
print(f"   New Password: rh1234")
print(f"   Browser Used: {self.browser_type}")
print("📄 All details saved to user.password.txt")
