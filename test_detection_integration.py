#!/usr/bin/env python3
"""
Test script to demonstrate how to integrate your driver detection code with the Flask backend.
This shows how to update driver status from your detection algorithm.
"""

import requests
import time
import random

# Flask backend URL
BACKEND_URL = "http://localhost:5000"
ACTIVE_NUMBER = os.environ.get('ACTIVE_NUMBER', '').strip() or (open('data/numbers.txt').read().strip().split('\n')[0] if os.path.exists('data/numbers.txt') else '')

def update_driver_status(status):
    """
    Update driver status in the Flask backend.
    This is the function you'll call from your detection code.
    """
    try:
        payload = {"status": status}
        if ACTIVE_NUMBER:
            payload["number"] = ACTIVE_NUMBER
        response = requests.post(f"{BACKEND_URL}/update_status", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status updated: {result['old_status']} → {result['new_status']}")
            return True
        else:
            print(f"❌ Error updating status: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def get_current_status():
    """Get current driver status from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/get_status")
        if response.status_code == 200:
            result = response.json()
            print(f"📊 Current status: {result['status']} (as of {result['timestamp']})")
            return result['status']
        else:
            print(f"❌ Error getting status: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def simulate_detection_events():
    """
    Simulate driver detection events.
    In your real code, you would call update_driver_status() when your detection algorithm
    detects drowsiness, yawning, etc.
    """
    print("🚗 Starting driver detection simulation...")
    print("This simulates how your detection code would interact with the Flask backend.\n")
    
    # Simulate various detection events
    events = [
        ("Awake", "Driver is alert and focused"),
        ("Drowsy", "Drowsiness detected - alert sent"),
        ("Yawning", "Yawning detected - monitoring closely"),
        ("Song Played", "Music played to keep driver alert"),
        ("Alert Sent", "Emergency alert sent to registered numbers"),
        ("Awake", "Driver is alert again")
    ]
    
    for status, description in events:
        print(f"🔍 Detection: {description}")
        update_driver_status(status)
        time.sleep(2)  # Simulate processing time
    
    print("\n✅ Simulation complete!")
    print("Check the web interface at http://localhost:5000 to see the updates.")

if __name__ == "__main__":
    print("🧪 Driver Detection Integration Test")
    print("=" * 50)
    
    # Test connection
    print("1. Testing connection to Flask backend...")
    current_status = get_current_status()
    if current_status is None:
        print("❌ Cannot connect to Flask backend. Make sure it's running on port 5000.")
        exit(1)
    
    print("\n2. Running detection simulation...")
    simulate_detection_events()
    
    print("\n3. Final status check...")
    get_current_status()
    
    print("\n🌐 Open http://localhost:5000 in your browser to see the live dashboard!")
    print("\n📝 To integrate with your detection code:")
    print("   - Import this script or copy the update_driver_status() function")
    print("   - Call update_driver_status('Drowsy') when drowsiness is detected")
    print("   - Call update_driver_status('Alert Sent') when alert is sent")
    print("   - Call update_driver_status('Song Played') when music is played")
