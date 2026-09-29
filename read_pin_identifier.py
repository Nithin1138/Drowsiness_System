#!/usr/bin/env python3
"""
Python tool to read the output of find_led_pins.ino.
Monitors COM5 at 9600 baud and prints the active pin status.
"""

import serial
import time
import sys

PORT = "COM5"
BAUD = 9600

def main():
    print("=" * 60)
    print("      ARDUINO LED PIN SCANNER MONITOR")
    print("=" * 60)
    print(f"Connecting to Arduino on {PORT}...")

    try:
        # Open serial port
        ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(2)
        print("✅ Connected! Watching for pin actions...\n")
        print("Upload 'find_led_pins.ino' to your Arduino.")
        print("Watch your physical board and note which LED glows for each line below:\n")
    except Exception as e:
        print(f"❌ Error: Could not connect to {PORT}: {e}")
        return

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if line:
                    print(f" Arduino: {line}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping scanner monitor...")
    finally:
        ser.close()
        print("Disconnected.")

if __name__ == "__main__":
    main()
