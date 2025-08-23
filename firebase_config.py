import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_firebase():
    """Initialize Firebase connection"""
    try:
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            database_url = os.getenv("FIREBASE_DATABASE_URL")
            
            if database_url:
                # Initialize Firebase with database URL only (for Vercel deployment)
                firebase_admin.initialize_app({
                    'databaseURL': database_url
                })
                print("Firebase initialized successfully with database URL")
            else:
                print("No Firebase database URL provided")
                return None
        
        return db.reference()
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        return None

def save_user_to_firebase(user):
    """Save user data to Firebase"""
    try:
        ref = db.reference('users')
        
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
            'timestamp': firebase_admin.db.ServerValue.TIMESTAMP
        }
        ref.child(str(user_id)).set(user_data)
        print(f"User saved to Firebase: {first_name} (ID: {user_id})")
        return True
    except Exception as e:
        print(f"Error saving user to Firebase: {e}")
        return False

def get_total_users():
    """Get total number of users from Firebase"""
    try:
        ref = db.reference('users')
        users = ref.get()
        return len(users) if users else 0
    except Exception as e:
        print(f"Error getting total users: {e}")
        return 0

def get_all_users():
    """Get all users from Firebase"""
    try:
        ref = db.reference('users')
        users = ref.get()
        return users if users else {}
    except Exception as e:
        print(f"Error getting all users: {e}")
        return {}
