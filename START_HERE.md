# 🚗 Driver Monitoring System - Quick Start Guide

## ⚡ Quick Setup (5 Minutes)

### Step 1: Get Your Telegram Bot Token (2 minutes)

1. Open Telegram app
2. Search for `@BotFather`
3. Send: `/newbot`
4. Name your bot: `Driver Safety Bot`
5. Username: `your_driver_bot` (must be unique)
6. **Copy the token** (looks like: `123456789:ABCdef...`)

### Step 2: Set Environment Variable (30 seconds)

**Windows PowerShell:**
```powershell
$env:TELEGRAM_BOT_TOKEN="PASTE_YOUR_TOKEN_HERE"
```

**Windows CMD:**
```cmd
set TELEGRAM_BOT_TOKEN=PASTE_YOUR_TOKEN_HERE
```

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="PASTE_YOUR_TOKEN_HERE"
```

### Step 3: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

### Step 4: Start Telegram Listener (30 seconds)

Open a **NEW terminal** and run:
```bash
python telegram_listener.py
```

Keep this running! You should see:
```
🤖 Telegram bot listener started...
```

### Step 5: Register Your Phone (1 minute)

1. Open Telegram
2. Find your bot (search for the username you created)
3. Click **Start** or send `/start`
4. Send your **10-digit phone number** (e.g., `9876543210`)
5. Bot will confirm: "✅ Registered successfully"

### Step 6: Start Flask Server (30 seconds)

Open **ANOTHER terminal** and run:
```bash
python app.py
```

You should see:
```
🚗 Driver Monitoring System Starting...
📱 Frontend available at: http://localhost:5000
```

### Step 7: Test It! (1 minute)

1. Open browser: **http://localhost:5000**
2. Enter your phone number
3. Click **Send OTP**
4. Check **Telegram** - you'll get the OTP
5. Enter OTP on website
6. Click **Verify OTP**
7. 🎉 You're in!

---

## 🧪 Verify Everything Works

Run the test script:
```bash
python test_otp_flow.py
```

This will check:
- ✅ Environment variables
- ✅ Data files
- ✅ Telegram bot connection
- ✅ User registrations
- ✅ Flask server

---

## 🎯 What You Need Running

For the **complete system**, you need **3 terminals**:

### Terminal 1: Telegram Listener
```bash
python telegram_listener.py
```
**Purpose:** Receives phone numbers from Telegram and maps them to chat IDs

### Terminal 2: Flask Server
```bash
python app.py
```
**Purpose:** Web server for login, dashboard, and API

### Terminal 3: Detection System (Optional)
```bash
python c.py
```
**Purpose:** Camera-based drowsiness detection + Arduino control

---

## 📋 The Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: User Registration (One-time)                       │
├─────────────────────────────────────────────────────────────┤
│  1. User opens Telegram                                     │
│  2. Finds bot and sends /start                              │
│  3. Sends phone number (e.g., 9876543210)                   │
│  4. telegram_listener.py saves to data/users.json           │
│     { "9876543210": 123456789 }                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Login Flow (Every time)                            │
├─────────────────────────────────────────────────────────────┤
│  1. User opens http://localhost:5000                        │
│  2. Enters phone number → clicks "Send OTP"                 │
│  3. Flask generates 6-digit OTP                             │
│  4. Flask sends OTP via Telegram to user's chat             │
│  5. User receives OTP in Telegram                           │
│  6. User enters OTP on website                              │
│  7. Flask verifies OTP                                      │
│  8. Session created → redirect to /home                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Monitoring (Continuous)                            │
├─────────────────────────────────────────────────────────────┤
│  1. c.py monitors driver via camera                         │
│  2. Detects: Drowsy, Yawning, Alert conditions              │
│  3. Sends status to Flask: POST /update_status              │
│  4. Flask logs events to data/logs.csv                      │
│  5. Dashboard shows real-time status                        │
│  6. Critical alerts → SMS to registered numbers             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### "Failed to send OTP"
- ✅ Check `telegram_listener.py` is running
- ✅ Verify you registered your phone with the bot
- ✅ Check `data/users.json` contains your phone number

### "OTP not received in Telegram"
- ✅ Make sure you sent your phone number to the bot
- ✅ Check the phone number matches exactly (10 digits)
- ✅ Look at Flask terminal for error messages

### "Can't access /home page"
- ✅ Complete OTP verification first
- ✅ Check browser cookies are enabled
- ✅ Try clearing browser cache

### Environment variable not working
- ✅ Set it in the **same terminal** where you run `app.py`
- ✅ Verify with: `echo $env:TELEGRAM_BOT_TOKEN` (PowerShell)
- ✅ Restart terminal if needed

---

## 📁 Project Structure

```
VIEW/
├── app.py                    # Flask backend (OTP, API, routes)
├── telegram_listener.py      # Maps phone → Telegram chat ID
├── c.py                      # Camera detection + Arduino
├── test_otp_flow.py         # Test script
├── SETUP_INSTRUCTIONS.md    # Detailed setup guide
├── START_HERE.md            # This file
├── templates/
│   ├── index.html           # Login page (OTP entry)
│   ├── home.html            # Dashboard
│   └── history.html         # Event history
└── data/
    ├── users.json           # Phone → Chat ID mapping
    ├── numbers.txt          # Registered numbers
    └── logs.csv             # Event logs
```

---

## 🎓 Understanding the System

### Why Telegram?
- ✅ **Free** - No SMS costs
- ✅ **Reliable** - Works worldwide
- ✅ **Fast** - Instant delivery
- ✅ **Secure** - End-to-end encryption

### How OTP Works
1. Flask generates random 6-digit code
2. Stores it temporarily (5 min expiry)
3. Sends to Telegram using bot API
4. User enters code
5. Flask verifies and creates session

### Security Features
- ✅ OTP expires after 5 minutes
- ✅ Max 3 verification attempts
- ✅ Session-based authentication
- ✅ Protected routes (/home, /history)

---

## 🚀 Next Steps

After successful setup:

1. **Test the detection system:**
   ```bash
   python c.py
   ```

2. **View the dashboard:**
   - http://localhost:5000/home

3. **Check event history:**
   - http://localhost:5000/history

4. **Add more users:**
   - Have them send their phone to your bot
   - They can login with OTP

---

## 📞 Need Help?

1. Run the test script: `python test_otp_flow.py`
2. Check Flask terminal for error messages
3. Verify all 3 terminals are running
4. Review `SETUP_INSTRUCTIONS.md` for detailed guide

---

**Made with ❤️ for driver safety**

