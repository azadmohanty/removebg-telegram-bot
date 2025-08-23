import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_health_endpoint():
    """Test the health endpoint to see Firebase status"""
    print("🔍 Testing Health Endpoint...")
    print("-" * 50)
    
    try:
        response = requests.get("https://removebg-telegram-bot.vercel.app/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Firebase Connected: {data.get('firebase_connected')}")
            print(f"Firebase URL: {data.get('firebase_url')}")
            return data
        else:
            print("❌ Health endpoint failed")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_webhook_with_firebase():
    """Test webhook with Firebase integration"""
    print("\n🧪 Testing Webhook with Firebase...")
    print("-" * 50)
    
    # Test data (simulate a /start message)
    test_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "first_name": "Test User",
                "username": "testuser",
                "is_bot": False
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test User",
                "type": "private"
            },
            "date": 1234567890,
            "text": "/start"
        }
    }
    
    try:
        response = requests.post("https://removebg-telegram-bot.vercel.app/webhook", json=test_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook responded successfully!")
            return True
        else:
            print("❌ Webhook failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_environment_variables():
    """Test if environment variables are accessible"""
    print("\n🔧 Testing Environment Variables...")
    print("-" * 50)
    
    # Test local environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    api_key = os.getenv("REMOVE_BG_API_KEY")
    firebase_url = os.getenv("FIREBASE_DATABASE_URL")
    admin_id = os.getenv("ADMIN_USER_ID")
    
    print(f"TELEGRAM_BOT_TOKEN: {'✅ Set' if token else '❌ Not Set'}")
    print(f"REMOVE_BG_API_KEY: {'✅ Set' if api_key else '❌ Not Set'}")
    print(f"FIREBASE_DATABASE_URL: {'✅ Set' if firebase_url else '❌ Not Set'}")
    print(f"ADMIN_USER_ID: {'✅ Set' if admin_id else '❌ Not Set'}")
    
    if firebase_url:
        print(f"Firebase URL Value: {firebase_url}")
    
    return all([token, api_key, firebase_url, admin_id])

if __name__ == "__main__":
    print("🔍 Comprehensive Firebase Debugging")
    print("=" * 60)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test health endpoint
    health_data = test_health_endpoint()
    
    # Test webhook
    webhook_ok = test_webhook_with_firebase()
    
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print(f"Environment Variables: {'✅ OK' if env_ok else '❌ MISSING'}")
    print(f"Health Endpoint: {'✅ OK' if health_data else '❌ FAILED'}")
    print(f"Webhook: {'✅ OK' if webhook_ok else '❌ FAILED'}")
    
    if health_data:
        print(f"Firebase Connected: {'✅ YES' if health_data.get('firebase_connected') else '❌ NO'}")
    
    print("=" * 60)
    
    if not health_data or not health_data.get('firebase_connected'):
        print("\n🚨 FIREBASE ISSUES DETECTED:")
        print("1. Check if FIREBASE_DATABASE_URL is set in Vercel")
        print("2. Check Vercel deployment logs for Firebase errors")
        print("3. Verify Firebase database URL is correct")
        print("4. Check if Firebase project has proper permissions")
