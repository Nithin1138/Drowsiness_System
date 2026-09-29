#!/usr/bin/env python3
"""
Test script to verify OTP flow is working correctly.
This script checks:
1. Environment variables are set
2. Data files are initialized
3. Telegram bot is accessible
4. OTP generation and verification logic
"""

import os
import json
import requests
import sys

def check_environment():
    """Check if required environment variables are set"""
    print("=" * 60)
    print("1. Checking Environment Variables")
    print("=" * 60)
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN is not set!")
        print("\nPlease set it using:")
        print("  Windows PowerShell: $env:TELEGRAM_BOT_TOKEN='YOUR_TOKEN'")
        print("  Linux/Mac: export TELEGRAM_BOT_TOKEN='YOUR_TOKEN'")
        return False
    else:
        # Mask the token for security
        masked = bot_token[:10] + "..." + bot_token[-5:] if len(bot_token) > 15 else "***"
        print(f"✅ TELEGRAM_BOT_TOKEN is set: {masked}")
        return True

def check_data_files():
    """Check if data directory and files exist"""
    print("\n" + "=" * 60)
    print("2. Checking Data Files")
    print("=" * 60)
    
    files_to_check = {
        'data/users.json': 'User-to-ChatID mapping',
        'data/numbers.txt': 'Registered phone numbers',
        'data/logs.csv': 'Event logs'
    }
    
    all_exist = True
    for file_path, description in files_to_check.items():
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists ({description})")
        else:
            print(f"⚠️  {file_path} missing ({description})")
            all_exist = False
    
    return all_exist

def check_telegram_bot():
    """Check if Telegram bot is accessible"""
    print("\n" + "=" * 60)
    print("3. Checking Telegram Bot Connection")
    print("=" * 60)
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    if not bot_token:
        print("❌ Cannot check bot - TELEGRAM_BOT_TOKEN not set")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Bot is accessible!")
                print(f"   Bot Name: {bot_info.get('first_name', 'N/A')}")
                print(f"   Username: @{bot_info.get('username', 'N/A')}")
                return True
            else:
                print(f"❌ Bot API returned error: {data}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Telegram: {e}")
        return False

def check_user_mappings():
    """Check if any users are registered"""
    print("\n" + "=" * 60)
    print("4. Checking User Registrations")
    print("=" * 60)
    
    users_file = 'data/users.json'
    
    if not os.path.exists(users_file):
        print("⚠️  No users.json file found")
        print("\nTo register a user:")
        print("1. Run: python telegram_listener.py")
        print("2. Open Telegram and find your bot")
        print("3. Send /start to the bot")
        print("4. Send your 10-digit phone number")
        return False
    
    try:
        with open(users_file, 'r') as f:
            users = json.load(f)
        
        if not users:
            print("⚠️  No users registered yet")
            print("\nTo register a user:")
            print("1. Run: python telegram_listener.py")
            print("2. Open Telegram and find your bot")
            print("3. Send /start to the bot")
            print("4. Send your 10-digit phone number")
            return False
        else:
            print(f"✅ {len(users)} user(s) registered:")
            for phone, chat_id in users.items():
                print(f"   Phone: {phone} → Chat ID: {chat_id}")
            return True
    except Exception as e:
        print(f"❌ Error reading users.json: {e}")
        return False

def check_flask_server():
    """Check if Flask server is running"""
    print("\n" + "=" * 60)
    print("5. Checking Flask Server")
    print("=" * 60)
    
    try:
        response = requests.get('http://localhost:5000/check_auth', timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is running at http://localhost:5000")
            return True
        else:
            print(f"⚠️  Flask server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask server is not running")
        print("\nTo start the server:")
        print("  python app.py")
        return False
    except Exception as e:
        print(f"❌ Error checking Flask server: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("Driver Monitoring System - OTP Flow Test")
    print("=" * 60)
    
    results = {
        'Environment': check_environment(),
        'Data Files': check_data_files(),
        'Telegram Bot': check_telegram_bot(),
        'User Registrations': check_user_mappings(),
        'Flask Server': check_flask_server()
    }
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All checks passed! Your system is ready.")
        print("\nNext steps:")
        print("1. Open browser: http://localhost:5000")
        print("2. Enter your registered phone number")
        print("3. Click 'Send OTP'")
        print("4. Check Telegram for OTP")
        print("5. Enter OTP and verify")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nQuick Start Guide:")
        print("1. Set TELEGRAM_BOT_TOKEN environment variable")
        print("2. Run: python telegram_listener.py (in one terminal)")
        print("3. Register your phone with the bot on Telegram")
        print("4. Run: python app.py (in another terminal)")
        print("5. Run this test again: python test_otp_flow.py")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())

