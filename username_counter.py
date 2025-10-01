#!/usr/bin/env python3
"""
Username Counter System for EmbyIL Registration
Maintains persistent state of last used username to avoid retries
"""
import json
import os
from datetime import datetime

class UsernameCounter:
    def __init__(self, counter_file='username_counter.json', base_username='tomtom'):
        self.counter_file = counter_file
        self.base_username = base_username
        self.counter_data = self.load_counter()

    def load_counter(self):
        """Load counter from persistent file"""
        try:
            if os.path.exists(self.counter_file):
                with open(self.counter_file, 'r') as f:
                    data = json.load(f)
                print(f"📂 Loaded counter: {data}")
                return data
            else:
                print("📂 No counter file found, starting fresh")
                return {
                    'last_username': f'{self.base_username}351',  # Start from 351
                    'last_number': 351,
                    'total_created': 0,
                    'last_updated': datetime.now().isoformat(),
                    'history': []
                }
        except Exception as e:
            print(f"⚠️ Error loading counter: {e}")
            return {
                'last_username': f'{self.base_username}351',
                'last_number': 351,
                'total_created': 0,
                'last_updated': datetime.now().isoformat(),
                'history': []
            }

    def save_counter(self):
        """Save counter to persistent file"""
        try:
            self.counter_data['last_updated'] = datetime.now().isoformat()
            with open(self.counter_file, 'w') as f:
                json.dump(self.counter_data, f, indent=2)
            print(f"💾 Counter saved: {self.counter_data['last_username']}")
        except Exception as e:
            print(f"⚠️ Error saving counter: {e}")

    def get_next_username(self):
        """Get the next available username"""
        next_number = self.counter_data['last_number'] + 1
        next_username = f"{self.base_username}{next_number}"

        print(f"🎯 Next username: {next_username}")
        return next_username, next_number

    def mark_username_used(self, username, success=True):
        """Mark a username as used and update counter"""
        # Extract number from username
        number = int(username.replace(self.base_username, ''))

        # Update counter data
        self.counter_data['last_username'] = username
        self.counter_data['last_number'] = number
        if success:
            self.counter_data['total_created'] += 1

        # Add to history
        self.counter_data['history'].append({
            'username': username,
            'number': number,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })

        # Keep only last 10 entries in history
        if len(self.counter_data['history']) > 10:
            self.counter_data['history'] = self.counter_data['history'][-10:]

        # Save to file
        self.save_counter()

        print(f"✅ Marked {username} as used (success: {success})")

    def get_current_status(self):
        """Get current counter status"""
        return {
            'last_username': self.counter_data['last_username'],
            'last_number': self.counter_data['last_number'],
            'next_username': f"{self.base_username}{self.counter_data['last_number'] + 1}",
            'total_created': self.counter_data['total_created'],
            'last_updated': self.counter_data['last_updated']
        }

# Example usage
if __name__ == "__main__":
    counter = UsernameCounter()

    # Get next username
    username, number = counter.get_next_username()
    print(f"Use this username: {username}")

    # Simulate successful registration
    # counter.mark_username_used(username, success=True)

    # Show status
    status = counter.get_current_status()
    print(f"Status: {status}")
