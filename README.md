# 🚗 Driver Monitoring System

A Flask-based web application for monitoring driver status with real-time updates, OTP authentication, and alert logging.

## 🔐 NEW: OTP Authentication Flow

This system now includes **secure OTP-based login using Telegram Bot**!

### 📖 Quick Start Guides

- **⭐ [START_HERE.md](START_HERE.md)** - 5-minute quick setup guide
- **📖 [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** - Detailed setup instructions
- **📋 [README_OTP_FLOW.md](README_OTP_FLOW.md)** - Complete OTP flow documentation
- **🔧 [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

### 🚀 Quick Start (OTP Flow)

**Windows:**
```cmd
start_system.bat
```

**Linux/Mac:**
```bash
chmod +x start_system.sh
./start_system.sh
```

Then open: **http://localhost:5000** and login with OTP!

---

## 🌟 Features

- **🔐 OTP Authentication**: Secure login via Telegram Bot (no SMS costs!)
- **Real-time Driver Status**: Live monitoring of driver state (Awake, Drowsy, Yawning, Song Played, Alert Sent)
- **Mobile Number Registration**: Store primary and secondary mobile numbers
- **History Logging**: Track important events (Drowsy, Alert Sent, Song Played)
- **Web Dashboard**: Modern, responsive interface for monitoring
- **REST API**: Easy integration with detection algorithms
- **CORS Support**: Frontend can communicate with backend seamlessly
- **Session Management**: Secure authentication with session-based access control

## 🚀 Traditional Quick Start (Without OTP)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Access the Web Interface
- **Login**: http://localhost:5000
- **Dashboard**: http://localhost:5000/home (requires OTP login)
- **History**: http://localhost:5000/history (requires OTP login)

## 📁 Project Structure

```
ECS/
├── app.py                          # Main Flask application
├── requirements.txt                 # Python dependencies
├── test_detection_integration.py   # Integration test script
├── templates/                      # HTML templates
│   ├── index.html                  # Registration page
│   ├── home.html                   # Dashboard page
│   └── history.html                # History logs page
└── data/                          # Data storage
    ├── numbers.txt                 # Stored mobile numbers
    └── logs.csv                    # Event logs
```

## 🔌 API Endpoints

### Web Pages
- `GET /` - Registration page
- `GET /home` - Driver dashboard
- `GET /history` - Event history

### API Endpoints
- `GET /get_status` - Get current driver status
- `POST /update_status` - Update driver status
- `GET /get_logs` - Get event logs
- `POST /add_number` - Save mobile numbers
- `GET /get_numbers` - Get stored numbers
- `POST /simulate_update` - Simulate status update (testing)

### Example API Usage

#### Update Driver Status
```python
import requests

# Update status from your detection code
response = requests.post('http://localhost:5000/update_status', 
                        json={'status': 'Drowsy'})
```

#### Get Current Status
```python
response = requests.get('http://localhost:5000/get_status')
status_data = response.json()
print(f"Current status: {status_data['status']}")
```

## 🔧 Integration with Detection Code

### Method 1: Direct Function Import
```python
from test_detection_integration import update_driver_status

# In your detection code:
if drowsiness_detected:
    update_driver_status('Drowsy')
    
if alert_sent:
    update_driver_status('Alert Sent')
    
if music_played:
    update_driver_status('Song Played')
```

### Method 2: HTTP Requests
```python
import requests

def update_driver_status(status):
    requests.post('http://localhost:5000/update_status', 
                 json={'status': status})
```

## 📱 Driver Status Types

- **Awake**: Driver is alert and focused
- **Drowsy**: Drowsiness detected
- **Yawning**: Yawning detected
- **Song Played**: Music played to keep driver alert
- **Alert Sent**: Emergency alert sent to registered numbers

## 🗂️ Data Storage

### Mobile Numbers (`data/numbers.txt`)
- One number per line
- Stored as plain text
- Supports primary and secondary numbers

### Event Logs (`data/logs.csv`)
- CSV format with columns: timestamp, event
- Only logs: Drowsy, Alert Sent, Song Played
- Timestamps in format: YYYY-MM-DD HH:MM:SS

## 🧪 Testing

### Run Integration Test
```bash
python test_detection_integration.py
```

### Manual API Testing
```bash
# Get current status
curl http://localhost:5000/get_status

# Update status
curl -X POST http://localhost:5000/update_status -H "Content-Type: application/json" -d '{"status":"Drowsy"}'

# Simulate update
curl -X POST http://localhost:5000/simulate_update
```

## 🔮 Future Enhancements

### Twilio SMS Integration
The Flask app is structured to easily add Twilio SMS functionality:

```python
from twilio.rest import Client

def send_sms(message, to_number):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=twilio_number,
        to=to_number
    )
```

### Database Integration
Replace file storage with SQLite/PostgreSQL:
- Add database models
- Update CRUD operations
- Add data persistence

### Real-time Updates
Add WebSocket support for instant updates:
- Use Flask-SocketIO
- Real-time status updates
- Live notifications

## 🛠️ Development

### Adding New Status Types
1. Update the `valid_statuses` list in `app.py`
2. Add CSS classes in `templates/home.html`
3. Update the simulation in `test_detection_integration.py`

### Customizing the UI
- Modify CSS in the HTML template files
- Update JavaScript for new functionality
- Add new API endpoints as needed

## 📞 Support

For questions or issues:
1. Check the API endpoints are responding
2. Verify Flask app is running on port 5000
3. Check browser console for JavaScript errors
4. Review the test script for integration examples

---

**Ready to monitor drivers! 🚗👁️**
# Drowsiness_System
