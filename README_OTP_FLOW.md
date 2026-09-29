# 🔐 OTP Authentication Flow - Complete Guide

## 📋 Overview

This Driver Monitoring System now includes a **secure OTP-based authentication flow** using **Telegram Bot** for OTP delivery.

### Why Telegram?
- ✅ **100% Free** - No SMS costs
- ✅ **Instant Delivery** - OTPs arrive in seconds
- ✅ **Reliable** - Works worldwide
- ✅ **Secure** - End-to-end encryption
- ✅ **Easy Setup** - 5 minutes to configure

---

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

**Windows:**
```cmd
start_system.bat
```

**Linux/Mac:**
```bash
chmod +x start_system.sh
./start_system.sh
```

### Option 2: Manual Startup

**Terminal 1 - Telegram Listener:**
```bash
python telegram_listener.py
```

**Terminal 2 - Flask Server:**
```bash
python app.py
```

**Terminal 3 - Detection (Optional):**
```bash
python c.py
```

---

## 📖 Complete Documentation

We've created comprehensive guides for you:

### 1. **START_HERE.md** ⭐ (Start with this!)
- 5-minute quick setup
- Step-by-step instructions
- Visual flow diagrams
- Troubleshooting tips

### 2. **SETUP_INSTRUCTIONS.md** (Detailed guide)
- Complete setup process
- Environment configuration
- Security best practices
- Production deployment tips

### 3. **IMPLEMENTATION_SUMMARY.md** (Technical details)
- Code changes made
- Architecture overview
- Security features
- System flow diagrams

---

## 🎯 The OTP Flow

```
┌──────────────────────────────────────────────────────────┐
│                    USER JOURNEY                          │
└──────────────────────────────────────────────────────────┘

1. 📱 User opens http://localhost:5000
   └─► Sees login page with phone input

2. ⌨️  User enters 10-digit phone number
   └─► Clicks "Send OTP"

3. 🔄 Flask generates 6-digit OTP
   └─► Sends to Telegram Bot API

4. 📨 Telegram delivers OTP to user's chat
   └─► User receives: "Your OTP is 123456. Valid for 5 minutes."

5. ⌨️  User enters OTP on website
   └─► Clicks "Verify OTP"

6. ✅ Flask verifies OTP
   └─► Creates session
   └─► Redirects to /home dashboard

7. 🎉 User is logged in!
   └─► Can access dashboard and history
```

---

## 🔧 Setup Checklist

- [ ] Create Telegram bot via @BotFather
- [ ] Copy bot token
- [ ] Set TELEGRAM_BOT_TOKEN environment variable
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Start telegram_listener.py
- [ ] Register phone number with bot
- [ ] Start Flask server (app.py)
- [ ] Test OTP flow: `python test_otp_flow.py`
- [ ] Open http://localhost:5000 and login

---

## 🧪 Testing

Run the automated test to verify everything is working:

```bash
python test_otp_flow.py
```

This checks:
- ✅ Environment variables
- ✅ Data files
- ✅ Telegram bot connection
- ✅ User registrations
- ✅ Flask server status

---

## 🔐 Security Features

| Feature | Description |
|---------|-------------|
| **OTP Expiry** | 5 minutes (300 seconds) |
| **Attempt Limit** | Maximum 3 verification attempts |
| **Session Auth** | Flask sessions with secret key |
| **Protected Routes** | /home and /history require login |
| **Input Validation** | Phone and OTP format checks |
| **No Token Exposure** | Bot token in environment variable |

---

## 📁 New Files Created

```
VIEW/
├── START_HERE.md              ⭐ Quick start guide
├── SETUP_INSTRUCTIONS.md      📖 Detailed setup
├── IMPLEMENTATION_SUMMARY.md  🔧 Technical details
├── README_OTP_FLOW.md        📋 This file
├── test_otp_flow.py          🧪 Automated test
├── start_system.bat          🪟 Windows startup
└── start_system.sh           🐧 Linux/Mac startup
```

---

## 🐛 Common Issues & Solutions

### Issue: "Failed to send OTP"

**Solution:**
1. Check telegram_listener.py is running
2. Verify phone is registered with bot
3. Check data/users.json contains your phone

### Issue: "OTP not received in Telegram"

**Solution:**
1. Send your phone number to the bot again
2. Check phone number format (10 digits, no spaces)
3. Look at Flask terminal for error messages

### Issue: "Can't access /home page"

**Solution:**
1. Complete OTP verification first
2. Check browser cookies are enabled
3. Try clearing browser cache and login again

### Issue: "TELEGRAM_BOT_TOKEN not set"

**Solution:**
```bash
# Windows PowerShell
$env:TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"

# Linux/Mac
export TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"
```

---

## 💡 Pro Tips

1. **Keep telegram_listener.py running** - It's needed for new user registrations
2. **Use the test script** - Run `python test_otp_flow.py` before starting
3. **Check logs** - Flask terminal shows detailed error messages
4. **Multiple users** - Each user registers their own phone with the bot
5. **Detection system** - c.py works independently, start it when needed

---

## 🎓 How It Works (Technical)

### Backend (app.py)

1. **OTP Generation:**
   - Random 6-digit code
   - Stored with timestamp
   - 5-minute expiry

2. **OTP Delivery:**
   - Tries Fast2SMS (if configured)
   - Falls back to Textbelt (limited)
   - Falls back to Telegram (recommended)

3. **OTP Verification:**
   - Checks expiry
   - Validates attempts
   - Creates session on success

### Frontend (index.html)

1. **Phone Entry:**
   - 10-digit validation
   - Send OTP button

2. **OTP Entry:**
   - 6-digit validation
   - 5-minute countdown
   - Resend option

3. **Auto-redirect:**
   - Checks authentication
   - Redirects if logged in

### Telegram Integration (telegram_listener.py)

1. **Bot Listener:**
   - Polls for updates
   - Handles /start command
   - Registers phone numbers

2. **User Mapping:**
   - Saves to data/users.json
   - Maps phone → chat_id
   - Used for OTP delivery

---

## 🌟 Features

- ✅ **No SMS costs** - Uses Telegram
- ✅ **Instant delivery** - OTPs arrive in seconds
- ✅ **Secure** - Session-based authentication
- ✅ **User-friendly** - Simple OTP flow
- ✅ **Auto-expiry** - OTPs expire after 5 minutes
- ✅ **Protected routes** - Authentication required
- ✅ **Real-time detection** - c.py integrates seamlessly
- ✅ **Multi-user support** - Each user gets their own OTP
- ✅ **Fallback chain** - Multiple SMS providers

---

## 📞 Support

1. **Read the guides:**
   - START_HERE.md (quick start)
   - SETUP_INSTRUCTIONS.md (detailed)
   - IMPLEMENTATION_SUMMARY.md (technical)

2. **Run the test:**
   ```bash
   python test_otp_flow.py
   ```

3. **Check logs:**
   - Flask terminal shows errors
   - telegram_listener.py shows registrations

4. **Verify setup:**
   - TELEGRAM_BOT_TOKEN is set
   - Both services are running
   - Phone is registered with bot

---

## 🎯 Next Steps

After successful login:

1. **View Dashboard:**
   - http://localhost:5000/home
   - Real-time driver status

2. **Check History:**
   - http://localhost:5000/history
   - Event logs and alerts

3. **Start Detection:**
   ```bash
   python c.py
   ```
   - Camera-based monitoring
   - Arduino control
   - Automatic alerts

---

## 📊 System Status

| Component | Status | Purpose |
|-----------|--------|---------|
| app.py | ✅ Modified | OTP flow + API |
| telegram_listener.py | ✅ Ready | User registration |
| c.py | ✅ Ready | Detection system |
| templates/ | ✅ Ready | Frontend UI |
| data/ | ✅ Auto-created | Storage |

---

**🎉 Everything is ready! Start with START_HERE.md for a 5-minute setup.**

---

Made with ❤️ for driver safety

