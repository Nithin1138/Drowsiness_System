# 🔄 OTP Authentication Flow - Visual Diagrams

## 📊 Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DRIVER MONITORING SYSTEM                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Browser    │◄───────►│    Flask     │◄───────►│  Telegram    │
│  (Frontend)  │  HTTP   │   (app.py)   │  API    │     Bot      │
└──────────────┘         └──────┬───────┘         └──────────────┘
                                │                         ▲
                                │                         │
                                ▼                         │
                         ┌──────────────┐                 │
                         │  Data Files  │                 │
                         │              │                 │
                         │ users.json   │◄────────────────┘
                         │ numbers.txt  │         telegram_listener.py
                         │ logs.csv     │         (Maps phone → chat_id)
                         └──────┬───────┘
                                ▲
                                │
                         ┌──────┴───────┐
                         │    c.py      │
                         │ (Detection)  │
                         │   + Arduino  │
                         └──────────────┘
```

---

## 🔐 OTP Authentication Flow (Step-by-Step)

### Phase 1: One-Time Registration

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: USER REGISTRATION (Do this once)                      │
└─────────────────────────────────────────────────────────────────┘

Step 1: User opens Telegram
   │
   ▼
Step 2: Searches for bot (e.g., @driver_safety_bot)
   │
   ▼
Step 3: Sends /start command
   │
   ▼
Step 4: Bot replies with welcome message
   │
   ▼
Step 5: User sends 10-digit phone number (e.g., 9876543210)
   │
   ▼
Step 6: telegram_listener.py receives the message
   │
   ▼
Step 7: Saves to data/users.json:
        {
          "9876543210": 123456789
        }
        (phone → chat_id mapping)
   │
   ▼
Step 8: Bot confirms: "✅ Registered successfully"

✅ Registration Complete! User can now login.
```

---

### Phase 2: Login Flow (Every Time)

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: LOGIN FLOW (Every time user wants to access system)   │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐
│ Browser  │  User opens http://localhost:5000
└────┬─────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  index.html (Login Page)                                     │
│  ┌────────────────────────────────────────────────────┐      │
│  │  Enter Phone Number: [__________]                  │      │
│  │  [Send OTP]                                        │      │
│  └────────────────────────────────────────────────────┘      │
└────┬─────────────────────────────────────────────────────────┘
     │ User enters: 9876543210
     │ Clicks: Send OTP
     ▼
┌──────────────────────────────────────────────────────────────┐
│  POST /send_otp                                              │
│  { "phone": "9876543210" }                                   │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Flask (app.py)                                              │
│  1. Validates phone number (10 digits)                       │
│  2. Generates random 6-digit OTP: 123456                     │
│  3. Stores in memory:                                        │
│     otp_storage["9876543210"] = {                            │
│       "otp": "123456",                                       │
│       "timestamp": 1234567890,                               │
│       "attempts": 0                                          │
│     }                                                        │
│  4. Calls send_sms_via_fast2sms()                            │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  send_sms_via_fast2sms() - Fallback Chain                   │
│                                                              │
│  Try 1: Fast2SMS (if API key configured)                    │
│         ❌ Not configured → Skip                             │
│                                                              │
│  Try 2: Textbelt (free but limited)                         │
│         ❌ Rate limited → Skip                               │
│                                                              │
│  Try 3: Telegram Bot ✅                                      │
│         1. Load data/users.json                             │
│         2. Find chat_id for "9876543210" → 123456789        │
│         3. Send message via Telegram API:                   │
│            POST https://api.telegram.org/bot{TOKEN}/sendMessage
│            {                                                 │
│              "chat_id": 123456789,                          │
│              "text": "Your OTP is 123456. Valid for 5 min." │
│            }                                                 │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Telegram Server                                             │
│  Delivers message to user's Telegram chat                    │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  User's Telegram App                                         │
│  📱 Notification: "Your OTP is 123456. Valid for 5 minutes." │
└────┬─────────────────────────────────────────────────────────┘
     │
     │ User sees OTP: 123456
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Browser (index.html)                                        │
│  ┌────────────────────────────────────────────────────┐      │
│  │  Enter OTP: [______]                               │      │
│  │  [Verify OTP]                                      │      │
│  │  Resend OTP in 4:58                                │      │
│  └────────────────────────────────────────────────────┘      │
└────┬─────────────────────────────────────────────────────────┘
     │ User enters: 123456
     │ Clicks: Verify OTP
     ▼
┌──────────────────────────────────────────────────────────────┐
│  POST /verify_otp                                            │
│  { "phone": "9876543210", "otp": "123456" }                  │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Flask (app.py)                                              │
│  1. Check if OTP exists for phone ✅                         │
│  2. Check if expired (5 min) ✅                              │
│  3. Check attempts (max 3) ✅                                │
│  4. Verify OTP matches ✅                                    │
│  5. Delete OTP from storage                                  │
│  6. Create session:                                          │
│     session['phone'] = "9876543210"                          │
│  7. Return success                                           │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Browser (index.html)                                        │
│  Receives success response                                   │
│  Redirects to: /home                                         │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  GET /home                                                   │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Flask (app.py)                                              │
│  1. Check session['phone'] exists ✅                         │
│  2. Render home.html                                         │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Browser shows Dashboard                                     │
│  ┌────────────────────────────────────────────────────┐      │
│  │  Driver Monitoring Dashboard                       │      │
│  │  ┌──────────────────────────────────────────┐      │      │
│  │  │  Current Status: Awake                   │      │      │
│  │  │  Last Updated: 2024-01-15 10:30:00       │      │      │
│  │  └──────────────────────────────────────────┘      │      │
│  │  [Home] [History] [Logout]                         │      │
│  └────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────┘

✅ User is now logged in and can access the dashboard!
```

---

## 🔄 Detection System Integration

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: CONTINUOUS MONITORING (While logged in)               │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   c.py       │  Camera-based detection running
│ (Detection)  │
└──────┬───────┘
       │ Detects: Driver is drowsy
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  POST /update_status                                         │
│  { "status": "Drowsy" }                                      │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Flask (app.py)                                              │
│  1. Updates global status: driver_status = "Drowsy"          │
│  2. Logs event to data/logs.csv                              │
│  3. If critical (Alert Sent):                                │
│     - Reads data/numbers.txt                                 │
│     - Sends SMS/Telegram to all registered numbers           │
└────┬─────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────────────────────────────┐
│  Browser (home.html)                                         │
│  Polls /get_status every 5 seconds                           │
│  Updates dashboard in real-time                              │
│  ┌────────────────────────────────────────────────────┐      │
│  │  Current Status: Drowsy ⚠️                         │      │
│  │  Last Updated: 2024-01-15 10:35:00                 │      │
│  └────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔒 Security Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  SECURITY FEATURES                                               │
└─────────────────────────────────────────────────────────────────┘

1. OTP Generation
   ├─ Random 6-digit code
   ├─ Stored with timestamp
   └─ 5-minute expiry

2. OTP Verification
   ├─ Check expiry (300 seconds)
   ├─ Max 3 attempts
   ├─ Delete after success
   └─ Delete after max attempts

3. Session Management
   ├─ Flask session with secret key
   ├─ session['phone'] = user's phone
   └─ Required for /home and /history

4. Route Protection
   ├─ /home → Check session
   ├─ /history → Check session
   └─ Redirect to / if not authenticated

5. Input Validation
   ├─ Phone: 10 digits only
   ├─ OTP: 6 digits only
   └─ Sanitized inputs
```

---

## 📊 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  DATA STORAGE                                                    │
└─────────────────────────────────────────────────────────────────┘

data/users.json
├─ Purpose: Map phone numbers to Telegram chat IDs
├─ Format: { "9876543210": 123456789 }
├─ Created by: telegram_listener.py
└─ Used by: app.py (for OTP delivery)

data/numbers.txt
├─ Purpose: Store registered phone numbers for alerts
├─ Format: One phone per line
├─ Created by: app.py
└─ Used by: app.py (for sending alerts)

data/logs.csv
├─ Purpose: Event history (Drowsy, Alert Sent, etc.)
├─ Format: timestamp,event,number
├─ Created by: app.py
└─ Used by: /history page

otp_storage (in-memory)
├─ Purpose: Temporary OTP storage
├─ Format: { "phone": { "otp": "123456", "timestamp": ..., "attempts": 0 } }
├─ Lifetime: 5 minutes or until verified
└─ Cleared: After verification or expiry
```

---

## 🎯 Complete User Journey

```
Day 1: Setup
├─ 1. Create Telegram bot
├─ 2. Set TELEGRAM_BOT_TOKEN
├─ 3. Start telegram_listener.py
├─ 4. Register phone with bot
├─ 5. Start app.py
└─ ✅ System ready

Day 2+: Daily Use
├─ 1. Start services (telegram_listener.py + app.py)
├─ 2. Open http://localhost:5000
├─ 3. Enter phone → Get OTP → Login
├─ 4. View dashboard
├─ 5. (Optional) Start c.py for detection
└─ ✅ Monitoring active
```

---

**This diagram shows the complete flow from registration to monitoring!**

