"""
Firebase REST API integration for the Telegram bot
Uses direct HTTP requests like the Node.js bot - no authentication required
"""
import requests
import json
import time
from typing import Dict, Any, Optional, List
from config import Config

class FirebaseREST:
    """Firebase REST API client for user management"""
    
    def __init__(self):
        self.base_url = Config.FIREBASE_DATABASE_URL
        if not self.base_url:
            raise ValueError("FIREBASE_DATABASE_URL not configured")
        
        # Remove trailing slash if present
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
    
    def save_user(self, user: Any) -> bool:
        """Save user to Firebase using REST API"""
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
                "id": user_id,
                "first_name": first_name,
                "username": username,
                "timestamp": int(time.time()),
                "last_seen": int(time.time())
            }
            
            # Firebase REST API endpoint
            url = f"{self.base_url}/users/{user_id}.json"
            
            # PUT request to create/update user
            response = requests.put(url, json=user_data, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"✅ User saved to Firebase: {first_name} (ID: {user_id})")
                return True
            else:
                print(f"❌ Firebase save failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error saving user to Firebase: {e}")
            return False
    
    def get_total_users(self) -> int:
        """Get total number of users from Firebase"""
        try:
            url = f"{self.base_url}/users.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                users = response.json()
                if users:
                    return len(users)
                return 0
            else:
                print(f"❌ Firebase get users failed: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"❌ Error getting total users from Firebase: {e}")
            return 0
    
    def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """Get all users from Firebase"""
        try:
            url = f"{self.base_url}/users.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                users = response.json()
                if users:
                    return users
                return {}
            else:
                print(f"❌ Firebase get users failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting all users from Firebase: {e}")
            return {}
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific user by ID from Firebase"""
        try:
            url = f"{self.base_url}/users/{user_id}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Firebase get user failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting user from Firebase: {e}")
            return None
    
    def update_user_activity(self, user_id: str) -> bool:
        """Update user's last seen timestamp in Firebase"""
        try:
            url = f"{self.base_url}/users/{user_id}/last_seen.json"
            timestamp = int(time.time())
            
            response = requests.put(url, json=timestamp, timeout=10)
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"❌ Firebase update activity failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating user activity in Firebase: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Firebase connection"""
        try:
            url = f"{self.base_url}/.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print("✅ Firebase connection successful")
                return True
            else:
                print(f"❌ Firebase connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Firebase connection error: {e}")
            return False

# Global Firebase instance
firebase = FirebaseREST()
