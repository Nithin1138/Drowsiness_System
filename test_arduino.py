#!/usr/bin/env python3
"""
Test file to verify Arduino Uno hardware functionality (LEDs, Buzzer, Motors).
This script cycles through all states (N, Y, B, X, E) on COM5 and explains
what you should see on the physical car system.

IMPORTANT: Please close c.py or any other script accessing COM5 before running this!
"""

import serial
import time
import sys

# Define port and states
PORT = "COM5"
BAUD = 9600

def test_states():
    print("=" * 60)
    print("         ECS CAR SYSTEM HARDWARE TESTER")
    print("=" * 60)
    print(f"Connecting to Arduino on {PORT}...")
    
    try:
        # Open serial port
        ser = serial.Serial(PORT, BAUD, timeout=1)
        # Arduino Uno resets upon open; wait 2.5 seconds for it to boot completely
        time.sleep(2.5) 
        print("✅ Ready! Initialized connection.\n")
    except Exception as e:
        print(f"❌ Error: Could not connect to {PORT}.")
        print("Please check:")
        print("  1. Is the Arduino connected to the computer via USB?")
        print("  2. Is c.py, new_test.py, or Arduino Serial Monitor currently running?")
        print("     (If so, close it to free the COM port, then run this test again.)")
        print(f"  Detalled error: {e}")
        return

    # Helper function to send state and hold
    def run_state(state, duration, description, expected_behavior):
        print("-" * 60)
        print(f"Testing State '{state}': {description}")
        print(f"Expected behavior: {expected_behavior}")
        print(f"Sending character '{state}'...")
        
        try:
            ser.write(state.encode())
            # Read feedback from Arduino serial if any
            time.sleep(0.5)
            if ser.in_waiting > 0:
                print(f"Arduino response: {ser.read(ser.in_waiting).decode().strip()}")
        except Exception as e:
            print(f"❌ Error sending data to Arduino: {e}")
            return
            
        print("Holding state...")
        # Tick down the seconds
        for i in range(duration, 0, -1):
            sys.stdout.write(f"\rTime remaining: {i} seconds... ")
            sys.stdout.flush()
            time.sleep(1)
        print(f"\rFinished State '{state}'.\n")

    try:
        # Cycle N: Normal
        run_state(
            state="N",
            duration=6,
            description="Normal / Awake Status",
            expected_behavior="YELLOW (Blue) LED should be GLOWING SOLID. Motors should run at FULL SPEED. Buzzer should be OFF."
        )

        # Cycle Y: Yawning
        run_state(
            state="Y",
            duration=6,
            description="Yawning Status",
            expected_behavior="YELLOW (Blue) LED should be FLASHING SLOWLY. Motors should run at FULL SPEED. Buzzer should be OFF."
        )

        # Cycle B: Drowsy
        run_state(
            state="B",
            duration=6,
            description="Drowsy Status",
            expected_behavior="YELLOW (Blue) LED should be FLASHING FAST. Buzzer should BEEP EXACTLY TWICE. Motors should run at FULL SPEED."
        )

        # Cycle X: Sleepy
        run_state(
            state="X",
            duration=7,
            description="Asleep Alert",
            expected_behavior="RED LED should be GLOWING SOLID. Buzzer should make a CONTINUOUS sound. Motors should run at FULL SPEED."
        )

        # Cycle E: Emergency Stop
        run_state(
            state="E",
            duration=10,
            description="Emergency Stop Status",
            expected_behavior="RED LED should be GLOWING SOLID. Buzzer should make a CONTINUOUS sound. Motors run for 5 seconds and then GRADUALLY SLOW DOWN to a COMPLETE STOP over 3 seconds."
        )

        # Reset back to Normal
        print("-" * 60)
        print("Resetting Arduino back to normal state...")
        ser.write(b"N")
        time.sleep(1)
        print("✅ Test cycle complete!")

    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user. Resetting Arduino...")
        try:
            ser.write(b"N")
        except:
            pass
    finally:
        ser.close()
        print("Disconnected serial port.")

if __name__ == "__main__":
    test_states()
