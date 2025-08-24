"""
User storage module for the Telegram bot
Handles user data persistence and retrieval using Firebase REST API
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from .firebase_rest import firebase

class UserStorage:
    """User storage system for tracking bot users using Firebase REST API"""
    
    def __init__(self):
        self.initialized = False
        self._fallback_storage = {}  # Fallback if Firebase fails
    
    def initialize(self) -> bool:
        """Initialize the storage system with Firebase"""
        try:
            # Test Firebase connection
            if firebase.test_connection():
                self.initialized = True
                print("✅ Firebase storage initialized successfully")
                return True
            else:
                print("⚠️ Firebase connection failed, using fallback storage")
                self.initialized = False
                return False
        except Exception as e:
            print(f"❌ Storage initialization error: {e}")
            self.initialized = False
            return False
    
    def save_user(self, user: Any) -> bool:
        """Save user data to Firebase using REST API"""
        try:
            # Try Firebase first
            if self.initialized:
                success = firebase.save_user(user)
                if success:
                    return True
            
            # Fallback to in-memory storage if Firebase fails
            return self._save_user_fallback(user)
            
        except Exception as e:
            print(f"❌ Error saving user: {e}")
            return self._save_user_fallback(user)
    
    def _save_user_fallback(self, user: Any) -> bool:
        """Fallback in-memory storage"""
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
            
            self._fallback_storage[str(user_id)] = user_data
            print(f"📝 User saved to fallback storage: {first_name} (ID: {user_id})")
            return True
        except Exception as e:
            print(f"❌ Error saving user to fallback storage: {e}")
            return False
    
    def get_total_users(self) -> int:
        """Get total number of users from Firebase or fallback"""
        try:
            if self.initialized:
                count = firebase.get_total_users()
                if count >= 0:
                    return count
            
            # Fallback to in-memory storage
            return len(self._fallback_storage)
            
        except Exception as e:
            print(f"❌ Error getting total users: {e}")
            return len(self._fallback_storage)
    
    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """Get all users from Firebase or fallback"""
        try:
            if self.initialized:
                users = firebase.get_all_users()
                if users:
                    return users
            
            # Fallback to in-memory storage
            return self._fallback_storage.copy()
            
        except Exception as e:
            print(f"❌ Error getting all users: {e}")
            return self._fallback_storage.copy()
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific user by ID from Firebase or fallback"""
        try:
            if self.initialized:
                user = firebase.get_user(user_id)
                if user:
                    return user
            
            # Fallback to in-memory storage
            return self._fallback_storage.get(str(user_id))
            
        except Exception as e:
            print(f"❌ Error getting user {user_id}: {e}")
            return self._fallback_storage.get(str(user_id))
    
    def update_user_activity(self, user_id: str) -> bool:
        """Update user's last seen timestamp in Firebase or fallback"""
        try:
            if self.initialized:
                success = firebase.update_user_activity(user_id)
                if success:
                    return True
            
            # Fallback to in-memory storage
            if str(user_id) in self._fallback_storage:
                self._fallback_storage[str(user_id)]['last_seen'] = datetime.now().isoformat()
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error updating user activity: {e}")
            # Fallback to in-memory storage
            if str(user_id) in self._fallback_storage:
                self._fallback_storage[str(user_id)]['last_seen'] = datetime.now().isoformat()
                return True
            return False
    
    def get_storage_status(self) -> Dict[str, Any]:
        """Get storage system status"""
        return {
            "firebase_connected": self.initialized,
            "fallback_active": not self.initialized,
            "total_users": self.get_total_users(),
            "storage_type": "Firebase REST API" if self.initialized else "In-Memory Fallback"
        }

# Global storage instance
storage = UserStorage()
