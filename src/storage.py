"""
User storage module for the Telegram bot
Handles user data persistence and retrieval
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class UserStorage:
    """User storage system for tracking bot users"""
    
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize the storage system"""
        try:
            self.initialized = True
            print("User storage initialized successfully")
            return True
        except Exception as e:
            print(f"Storage initialization error: {e}")
            return False
    
    def save_user(self, user: Any) -> bool:
        """Save user data to storage"""
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
                'timestamp': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat()
            }
            
            self.users[str(user_id)] = user_data
            print(f"User saved to storage: {first_name} (ID: {user_id})")
            return True
        except Exception as e:
            print(f"Error saving user to storage: {e}")
            return False
    
    def get_total_users(self) -> int:
        """Get total number of users"""
        try:
            return len(self.users)
        except Exception as e:
            print(f"Error getting total users: {e}")
            return 0
    
    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """Get all users from storage"""
        try:
            return self.users.copy()
        except Exception as e:
            print(f"Error getting all users: {e}")
            return {}
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific user by ID"""
        try:
            return self.users.get(str(user_id))
        except Exception as e:
            print(f"Error getting user {user_id}: {e}")
            return None
    
    def update_user_activity(self, user_id: str) -> bool:
        """Update user's last seen timestamp"""
        try:
            if str(user_id) in self.users:
                self.users[str(user_id)]['last_seen'] = datetime.now().isoformat()
                return True
            return False
        except Exception as e:
            print(f"Error updating user activity: {e}")
            return False

# Global storage instance
storage = UserStorage()
