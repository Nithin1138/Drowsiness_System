# 🚀 Quick Start Guide - 3 Steps to Run

## ✅ Your .env file is already configured!

Your bot token is: `8359627312:AAH9-WQMQGEs1CSeHqOHuXuVju3h4B30FVQ`

---

## Step 1: Install python-dotenv (One-time)

```powershell
pip install python-dotenv
```

---

## Step 2: Start the System

### Option A: Use the Batch File (Easiest)

Just double-click `start_system.bat` or run:

```cmd
start_system.bat
```

This will open 2 windows:
- **Telegram Listener** - Handles phone registration
- **Flask Server** - Web application

### Option B: Manual Start

**Terminal 1 - Telegram Listener:**
```powershell
cd C:\Users\Lenovo\OneDrive\Desktop\ecs2\VIEW
python telegram_listener.py
```

**Terminal 2 - Flask Server:**
```powershell
cd C:\Users\Lenovo\OneDrive\Desktop\ecs2\VIEW
python app.py
```

---

## Step 3: Register Your Phone (First Time Only)

1. **Open Telegram** (mobile or desktop)

2. **Find your bot:**
   - Search for: `@your_bot_username`
   - Or use this link: `https://t.me/your_bot_username`

3. **Start the bot:**
   - Click "Start" or send `/start`
   - Bot will reply with welcome message

4. **Register your phone:**
   - Send your 10-digit phone number: `9618484381`
   - Bot will confirm: "✅ Registered successfully for phone 9618484381"

5. **Verify registration:**
   - Check the Telegram Listener terminal
   - You should see: `[INFO] Linked phone 9618484381 → chat 123456789`

---

## Step 4: Login and Use

1. **Open browser:** http://localhost:5000

2. **Enter phone number:** `9618484381`

3. **Click:** "Send OTP"

4. **Check Telegram** - You'll receive a message like:
   ```
   Your OTP is 123456. Valid for 5 minutes.
   ```

5. **Enter the OTP** on the website

6. **Click:** "Verify OTP"

7. **🎉 You're in!** - Dashboard will load

---

## 🎯 What You Should See

### Telegram Listener Terminal:
```
🤖 Telegram bot listener started...
Polling for updates...
[INFO] Linked phone 9618484381 → chat 123456789
```

### Flask Server Terminal:
```
🚗 Driver Monitoring System Starting...
📱 Frontend available at: http://localhost:5000
 * Running on http://127.0.0.1:5000
```

### Browser:
- Login page with phone input
- After OTP verification → Dashboard with driver status

---

## 🐛 Troubleshooting

### Problem: Bot not responding in Telegram

**Solution:**
1. Make sure Telegram Listener is running (check Terminal 1)
2. Verify your bot username is correct
3. Try sending `/start` again

### Problem: "No Telegram mapping for number"

**Solution:**
1. You haven't registered your phone with the bot yet
2. Follow Step 3 above to register
3. Check `data/users.json` - it should contain your phone number

### Problem: OTP not received

**Solution:**
1. Check Telegram Listener terminal for errors
2. Make sure you registered the correct phone number
3. Verify .env file has the correct bot token

### Problem: Can't access dashboard

**Solution:**
1. Make sure you completed OTP verification
2. Check Flask server is running
3. Try logging in again

---

## 📱 Optional: Start Detection System

To enable camera-based drowsiness detection:

```powershell
# Terminal 3
cd C:\Users\Lenovo\OneDrive\Desktop\ecs2\VIEW
python c.py
```

This will:
- Start camera monitoring
- Detect drowsiness, yawning, head movement
- Send alerts when needed
- Control Arduino (if connected)

---

## 🔄 Daily Usage

After the first-time setup, you only need to:

1. **Start services:**
   ```cmd
   start_system.bat
   ```

2. **Open browser:** http://localhost:5000

3. **Login with OTP**

4. **Done!** 🎉

---

## 📞 Need Help?

Check these files for more details:
- `START_HERE.md` - Detailed setup guide
- `VERIFICATION_CHECKLIST.md` - Step-by-step checklist
- `FLOW_DIAGRAM.md` - Visual flow diagrams
- `SETUP_INSTRUCTIONS.md` - Complete setup instructions

---

**Your system is ready to run! Just install python-dotenv and start the services.** 🚀

