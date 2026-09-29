from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import csv
import os
from datetime import datetime
import json
import random
import time
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ----------------------------
# Configuration (set env vars if possible)
# ----------------------------
FAST2SMS_API_KEY = ''
FAST2SMS_SENDER_ID = ''
FAST2SMS_URL = 'https://www.fast2sms.com/dev/bulkV2'
# Telegram (fallback, reliable & free)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')  # e.g. 123456789:ABC... (recommended)
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')      # your numeric chat id

# Textbelt free key (very limited: ~1 SMS/day per IP). Good for one-off demos.
TEXTBELT_KEY = 'textbelt'

# ----------------------------
# SMS sending with fallbacks: Fast2SMS -> Textbelt -> Telegram
# ----------------------------
def send_sms_via_fast2sms(number: str, message: str, *, is_otp: bool = False) -> bool:
    """
    Try to send SMS using (in order):
      1) Fast2SMS transactional API (if FAST2SMS_API_KEY is provided and works)
      2) Textbelt free SMS (limited)
      3) Telegram bot message (recommended fallback — reliable & free)
    Returns True on success, False otherwise.
    """
    # Normalize number: expect 10-digit local Indian number; Textbelt/Telegram will need +91 prefix for SMS
    clean_num = ''.join(filter(str.isdigit, number)) if number else ''
    if len(clean_num) == 10:
        sms_number_international = '+91' + clean_num
    else:
        sms_number_international = clean_num  # if user provided full number already

    # Prepare OTP message formatting
    if is_otp:
        sms_message = f"Your OTP is {message}. Valid for 5 minutes."
    else:
        sms_message = message

    # 1) Try Fast2SMS if key present
    if FAST2SMS_API_KEY:
        try:
            payload = {
                'sender_id': FAST2SMS_SENDER_ID,
                'message': sms_message,
                'language': 'english',
                'route': 'q',   # transactional quick route (no website verification required for this)
                'numbers': clean_num
            }
            headers = {
                'authorization': FAST2SMS_API_KEY,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache'
            }
            resp = requests.post(FAST2SMS_URL, data=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                try:
                    rj = resp.json()
                except ValueError:
                    print(f"[WARN] Fast2SMS non-JSON response: {resp.text}")
                    rj = {}
                if rj.get('return') is True:
                    print(f"[INFO] Fast2SMS: SMS sent to {clean_num}")
                    return True
                else:
                    print(f"[WARN] Fast2SMS returned false/failed: {rj}")
            else:
                print(f"[WARN] Fast2SMS HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"[WARN] Fast2SMS exception: {e}")

    # 2) Fallback to Textbelt (free but rate-limited)
    try:
        tb_payload = {
            'phone': sms_number_international,
            'message': sms_message,
            'key': TEXTBELT_KEY
        }
        tb_resp = requests.post('https://textbelt.com/text', data=tb_payload, timeout=10)
        if tb_resp.status_code == 200:
            tb_json = tb_resp.json()
            if tb_json.get('success'):
                print(f"[INFO] Textbelt SMS sent to {sms_number_international}")
                return True
            else:
                print(f"[WARN] Textbelt failed: {tb_json}")
        else:
            print(f"[WARN] Textbelt HTTP {tb_resp.status_code}: {tb_resp.text}")
    except Exception as e:
        print(f"[WARN] Textbelt exception: {e}")

    # 3) Final fallback: Telegram message per-user mapping
    if TELEGRAM_BOT_TOKEN:
        try:
            # Load per-user mappings from data/users.json
            mapping_file = "data/users.json"
            if os.path.exists(mapping_file):
                with open(mapping_file, "r") as f:
                    user_map = json.load(f)
            else:
                user_map = {}

            # Find chat_id linked to this phone number
            chat_id = user_map.get(clean_num)
            if chat_id:
                tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                tg_payload = {"chat_id": chat_id, "text": sms_message}
                tg_resp = requests.post(tg_url, json=tg_payload, timeout=10)
                if tg_resp.status_code == 200 and tg_resp.json().get("ok"):
                    print(f"[INFO] Telegram message sent to chat {chat_id} for {clean_num}")
                    return True
                else:
                    print(f"[WARN] Telegram failed: {tg_resp.text}")
            else:
                print(f"[WARN] No Telegram mapping for number {clean_num}")
        except Exception as e:
            print(f"[WARN] Telegram exception: {e}")
    else:
        print("[INFO] Telegram bot token not configured")

    return False


# ----------------------------
# The rest of your Flask app — unchanged logic and routes
# ----------------------------
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session
CORS(app)  # Enable CORS for frontend JavaScript

# Store OTPs temporarily (in production, use a proper database)
otp_storage = {}

# Global driver status variable
driver_status = "Awake"

@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    phone = data.get('phone')
    
    if not phone or len(phone) != 10 or not phone.isdigit():
        return jsonify({'success': False, 'message': 'Invalid phone number'}), 400
    
    # Generate a 6-digit OTP
    otp = f"{random.randint(100000, 999999)}"
    otp_storage[phone] = {
        'otp': otp,
        'timestamp': time.time(),
        'attempts': 0
    }
    
    # Send OTP via Fast2SMS/Textbelt/Telegram (fallback chain)
    sms_sent = send_sms_via_fast2sms(phone, otp, is_otp=True)
    if not sms_sent:
        return jsonify({'success': False, 'message': 'Failed to send OTP'}), 500
    
    return jsonify({
        'success': True,
        'message': 'OTP sent successfully'
    })

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone = data.get('phone')
    user_otp = data.get('otp')
    
    if not phone or not user_otp:
        return jsonify({
            'success': False,
            'message': 'Phone and OTP are required'
        }), 400
    
    stored = otp_storage.get(phone)
    if not stored:
        return jsonify({
            'success': False,
            'message': 'No OTP found for this number'
        }), 400
    
    # Check if OTP is expired (5 minutes)
    if time.time() - stored['timestamp'] > 300:
        del otp_storage[phone]
        return jsonify({
            'success': False,
            'message': 'OTP expired'
        }), 400
    
    # Check attempts
    if stored['attempts'] >= 3:
        del otp_storage[phone]
        return jsonify({
            'success': False,
            'message': 'Too many attempts. Request new OTP'
        }), 400
    
    stored['attempts'] += 1
    
    if stored['otp'] != user_otp:
        return jsonify({
            'success': False,
            'message': 'Invalid OTP'
        }), 400
    
    # OTP verified successfully
    del otp_storage[phone]
    session['phone'] = phone  # Set session
    
    return jsonify({
        'success': True,
        'message': 'OTP verified successfully'
    })

@app.route('/check_auth')
def check_auth():
    phone = session.get('phone')
    return jsonify({
        'authenticated': bool(phone),
        'phone': phone
    })

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    """Clear session and logout user"""
    session.clear()  # Clear entire session
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

# Data file paths
NUMBERS_FILE = "data/numbers.txt"
LOGS_FILE = "data/logs.csv"
USERS_FILE = "data/users.json"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Initialize data files if they don't exist
def initialize_data_files():
    if not os.path.exists(NUMBERS_FILE):
        with open(NUMBERS_FILE, 'w') as f:
            f.write("")

    if not os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            # Include optional 'number' column for per-user history
            writer.writerow(['timestamp', 'event', 'number'])

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)

# Read mobile numbers from file
def read_numbers():
    try:
        with open(NUMBERS_FILE, 'r') as f:
            numbers = f.read().strip().split('\n')
            return [num for num in numbers if num.strip()]
    except FileNotFoundError:
        return []

# Save mobile numbers to file
def save_numbers(numbers):
    with open(NUMBERS_FILE, 'w') as f:
        f.write('\n'.join(numbers))

# Add log entry
def add_log(event, number: str | None = None):
    with open(LOGS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            event,
            number or ''
        ])

# Read logs from file
def read_logs():
    logs = []
    try:
        with open(LOGS_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalize missing 'number' field for legacy rows
                if 'number' not in row:
                    row['number'] = ''
                logs.append(row)
    except FileNotFoundError:
        pass
    return logs

# Routes
@app.route('/')
def index():
    """Serve the login/index page"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Serve the login page to select previously saved numbers"""
    return render_template('login.html')

@app.route('/home')
def home():
    """Serve the home page with driver status"""
    # Check if user is authenticated
    if 'phone' not in session:
        return render_template('index.html')
    return render_template('home.html')

@app.route('/history')
def history():
    """Serve the history page with logs"""
    # Check if user is authenticated
    if 'phone' not in session:
        return render_template('index.html')
    return render_template('history.html')

@app.route('/test_alerts')
def test_alerts_page():
    """Serve the test alerts page"""
    # Check if user is authenticated
    if 'phone' not in session:
        return render_template('index.html')
    return render_template('test_alerts.html')

@app.route('/update_status', methods=['POST'])
def update_status():
    """Update driver status from detection code"""
    global driver_status
    
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    new_status = data['status']
    valid_statuses = ['Awake', 'Drowsy', 'Yawning', 'Song Played', 'Alert Sent']
    
    if new_status not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400
    
    # Update global status
    old_status = driver_status
    driver_status = new_status
    
    # Log only specific events
    if new_status in ['Drowsy', 'Alert Sent', 'Song Played']:
        # Attach optional phone number if provided by client
        number = data.get('number') if isinstance(data, dict) else None
        add_log(new_status, number)

        # Send alerts for both 'Alert Sent' and 'Drowsy' status
        if new_status in ['Alert Sent', 'Drowsy']:
            # Get numbers from both numbers.txt and users.json
            alert_numbers = read_numbers()

            # Also get numbers from users.json (Telegram registered users)
            try:
                if os.path.exists(USERS_FILE):
                    with open(USERS_FILE, 'r') as f:
                        users_data = json.load(f)
                        telegram_numbers = list(users_data.keys())
                        # Merge with existing alert numbers
                        alert_numbers = list(set(alert_numbers + telegram_numbers))
            except Exception as e:
                print(f"[WARN] Could not load users.json: {e}")

            if not alert_numbers:
                print("[WARN] No phone numbers registered for alerts!")
            else:
                print(f"[INFO] Sending alerts to {len(alert_numbers)} numbers...")

                # Customize message based on status
                if new_status == 'Alert Sent':
                    alert_message = f"🚨 EMERGENCY ALERT! Driver is UNRESPONSIVE or SLEEPY! Time: {datetime.now().strftime('%H:%M:%S')}"
                elif new_status == 'Drowsy':
                    alert_message = f"⚠️ WARNING! Driver is DROWSY! Time: {datetime.now().strftime('%H:%M:%S')}"
                else:
                    alert_message = f"🚨 ALERT! Driver status: {new_status} at {datetime.now().strftime('%H:%M:%S')}"

                for num in alert_numbers:
                    print(f"[INFO] Sending alert to {num}...")
                    success = send_sms_via_fast2sms(num, alert_message)
                    if success:
                        print(f"[SUCCESS] Alert sent to {num}")
                    else:
                        print(f"[FAILED] Could not send alert to {num}")
    
    return jsonify({
        'success': True,
        'old_status': old_status,
        'new_status': driver_status
    })

@app.route('/get_status', methods=['GET'])
def get_status():
    """Return current driver status as JSON"""
    return jsonify({
        'status': driver_status,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/add_number', methods=['POST'])
def add_number():
    """Save entered mobile numbers"""
    data = request.get_json()
    if not data or 'numbers' not in data:
        return jsonify({'error': 'Numbers are required'}), 400
    
    numbers = data['numbers']
    if not isinstance(numbers, list):
        return jsonify({'error': 'Numbers must be a list'}), 400
    
    # Validate mobile numbers (basic validation)
    valid_numbers = []
    for num in numbers:
        if isinstance(num, str) and num.strip():
            # Basic validation: should be digits and reasonable length
            clean_num = ''.join(filter(str.isdigit, num))
            if len(clean_num) >= 10:
                valid_numbers.append(clean_num)
    
    if not valid_numbers:
        return jsonify({'error': 'No valid mobile numbers provided'}), 400
    
    # Merge with existing numbers and deduplicate while preserving order
    existing_numbers = read_numbers()
    merged: list[str] = []
    seen = set()
    for num in existing_numbers + valid_numbers:
        if num not in seen:
            seen.add(num)
            merged.append(num)
    
    # Save merged list
    save_numbers(merged)
    
    return jsonify({
        'success': True,
        'saved_numbers': merged
    })

@app.route('/get_numbers', methods=['GET'])
def get_numbers():
    """Return stored mobile numbers"""
    numbers = read_numbers()
    return jsonify({'numbers': numbers})

@app.route('/get_logs', methods=['GET'])
def get_logs():
    """Return logs for history page (filtered per user number, newest first)."""
    logs = read_logs()
    allowed = {"Drowsy", "Alert Sent", "Song Played"}
    number = request.args.get('number', default='', type=str).strip()
    filtered = [log for log in logs if log.get('event') in allowed]
    if number:
        filtered = [log for log in filtered if (log.get('number') or '').strip() == number]
    # newest first (assuming file appends at end, reverse to show latest on top)
    filtered.reverse()
    return jsonify({'logs': filtered})

# API endpoint to simulate driver status updates (for testing)
@app.route('/simulate_update', methods=['POST'])
def simulate_update():
    """Simulate a driver status update (for testing purposes)"""
    import random

    statuses = ['Awake', 'Drowsy', 'Yawning', 'Song Played', 'Alert Sent']
    new_status = random.choice(statuses)

    # Update status
    global driver_status
    old_status = driver_status
    driver_status = new_status

    # Log if it's a loggable event
    if new_status in ['Drowsy', 'Alert Sent', 'Song Played']:
        add_log(new_status)

    return jsonify({
        'success': True,
        'old_status': old_status,
        'new_status': new_status,
        'message': 'Status updated via simulation'
    })

# API endpoint to test emergency alerts
@app.route('/test_emergency_alert', methods=['POST'])
def test_emergency_alert():
    """Test emergency alert system by sending alerts to all registered numbers"""
    print("\n" + "="*50)
    print("🚨 TESTING EMERGENCY ALERT SYSTEM")
    print("="*50)

    # Get numbers from both sources
    alert_numbers = read_numbers()

    # Also get numbers from users.json (Telegram registered users)
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                users_data = json.load(f)
                telegram_numbers = list(users_data.keys())
                alert_numbers = list(set(alert_numbers + telegram_numbers))
                print(f"[INFO] Found {len(telegram_numbers)} Telegram registered numbers")
    except Exception as e:
        print(f"[WARN] Could not load users.json: {e}")

    print(f"[INFO] Total numbers to alert: {len(alert_numbers)}")
    print(f"[INFO] Numbers: {alert_numbers}")

    if not alert_numbers:
        return jsonify({
            'success': False,
            'message': 'No phone numbers registered for alerts!'
        }), 400

    alert_message = f"🚨 TEST ALERT! This is a test of the emergency alert system. Time: {datetime.now().strftime('%H:%M:%S')}"

    results = []
    for num in alert_numbers:
        print(f"\n[INFO] Sending test alert to {num}...")
        success = send_sms_via_fast2sms(num, alert_message)
        results.append({
            'number': num,
            'success': success
        })
        if success:
            print(f"[SUCCESS] ✅ Alert sent to {num}")
        else:
            print(f"[FAILED] ❌ Could not send alert to {num}")

    print("\n" + "="*50)
    print("TEST COMPLETE")
    print("="*50 + "\n")

    return jsonify({
        'success': True,
        'message': f'Test alerts sent to {len(alert_numbers)} numbers',
        'results': results
    })

if __name__ == '__main__':
    # Initialize data files
    initialize_data_files()
    
    # Add some sample logs for demonstration
    if os.path.getsize(LOGS_FILE) == 0:
        sample_logs = [
            ('2024-01-15 09:30:00', 'Drowsy', '9999999999'),
            ('2024-01-15 10:15:00', 'Alert Sent', '9999999999'),
            ('2024-01-15 11:00:00', 'Song Played', '8888888888'),
            ('2024-01-15 14:30:00', 'Drowsy', '8888888888'),
            ('2024-01-15 15:45:00', 'Alert Sent', '9999999999')
        ]
        with open(LOGS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'event', 'number'])
            writer.writerows(sample_logs)
    
    print("🚗 Driver Monitoring System Starting...")
    print("📱 Frontend available at: http://localhost:5000")
    print("🔧 API endpoints available at: http://localhost:5000/api/...")
    print("📊 Test simulation: POST to http://localhost:5000/simulate_update")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
