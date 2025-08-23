import json
import os
from datetime import datetime

# Simple in-memory user storage (for development/testing)
users_storage = {}

def save_user_to_storage(user):
    """Save user data to simple storage"""
    try:
        # Handle both user objects and dictionaries
        if hasattr(user, 'id'):
            # User object (from bot.py)
            user_id = user.id
            first_name = user.first_name or ""
            username = user.username or ""
        else:
            # Dictionary (from webhook handler)
            user_id = user.get('id')
            first_name = user.get('first_name', '')
            username = user.get('username', '')
        
        user_data = {
            'id': user_id,
            'first_name': first_name,
            'username': username,
            'timestamp': datetime.now().isoformat()
        }
        
        users_storage[str(user_id)] = user_data
        print(f"User saved to storage: {first_name} (ID: {user_id})")
        return True
    except Exception as e:
        print(f"Error saving user to storage: {e}")
        return False

def get_total_users():
    """Get total number of users from storage"""
    try:
        return len(users_storage)
    except Exception as e:
        print(f"Error getting total users: {e}")
        return 0

def get_all_users():
    """Get all users from storage"""
    try:
        return users_storage
    except Exception as e:
        print(f"Error getting all users: {e}")
        return {}

def initialize_storage():
    """Initialize the storage system"""
    try:
        print("Simple user storage initialized successfully")
        return True
    except Exception as e:
        print(f"Storage initialization error: {e}")
        return False
