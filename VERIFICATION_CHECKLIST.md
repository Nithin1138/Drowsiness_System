# ✅ Verification Checklist - OTP Flow Setup

Use this checklist to verify your Driver Monitoring System is set up correctly.

---

## 📋 Pre-Setup Checklist

### System Requirements

- [ ] Python 3.8 or higher installed
  ```bash
  python --version
  # Should show: Python 3.8.x or higher
  ```

- [ ] pip package manager available
  ```bash
  pip --version
  # Should show pip version
  ```

- [ ] Telegram app installed (mobile or desktop)

- [ ] Internet connection available

---

## 🤖 Telegram Bot Setup

### Step 1: Create Bot

- [ ] Opened Telegram
- [ ] Found @BotFather
- [ ] Sent `/newbot` command
- [ ] Chose bot name (e.g., "Driver Safety Bot")
- [ ] Chose bot username (e.g., "my_driver_bot")
- [ ] Received bot token (format: `123456789:ABCdef...`)
- [ ] Saved bot token securely

**Verification:**
```
✅ You should have a token that looks like:
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

### Step 2: Set Environment Variable

**Windows PowerShell:**
- [ ] Opened PowerShell
- [ ] Ran: `$env:TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"`
- [ ] Verified: `echo $env:TELEGRAM_BOT_TOKEN`

**Windows CMD:**
- [ ] Opened Command Prompt
- [ ] Ran: `set TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE`
- [ ] Verified: `echo %TELEGRAM_BOT_TOKEN%`

**Linux/Mac:**
- [ ] Opened Terminal
- [ ] Ran: `export TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"`
- [ ] Verified: `echo $TELEGRAM_BOT_TOKEN`

**Verification:**
```bash
# Run this in the same terminal where you'll run app.py
echo $env:TELEGRAM_BOT_TOKEN  # PowerShell
echo %TELEGRAM_BOT_TOKEN%     # CMD
echo $TELEGRAM_BOT_TOKEN      # Linux/Mac

✅ Should display your bot token
```

---

## 📦 Dependencies Installation

- [ ] Navigated to project directory
  ```bash
  cd path/to/VIEW
  ```

- [ ] Installed requirements
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Verified installation
  ```bash
  pip list | grep Flask
  pip list | grep requests
  ```

**Verification:**
```
✅ Should see:
   Flask         2.3.3
   Flask-CORS    4.0.0
   requests      2.32.3
   (and other packages)
```

---

## 🎧 Telegram Listener Setup

### Step 1: Start Listener

- [ ] Opened new terminal/command prompt
- [ ] Navigated to project directory
- [ ] Set TELEGRAM_BOT_TOKEN in this terminal
- [ ] Ran: `python telegram_listener.py`

**Verification:**
```
✅ Should see:
   🤖 Telegram bot listener started...
```

**Keep this terminal running!**

---

### Step 2: Register Phone Number

- [ ] Opened Telegram app
- [ ] Searched for bot username (e.g., @my_driver_bot)
- [ ] Clicked "Start" or sent `/start`
- [ ] Received welcome message from bot
- [ ] Sent 10-digit phone number (e.g., `9876543210`)
- [ ] Received confirmation: "✅ Registered successfully"

**Verification:**
```bash
# Check data/users.json file
cat data/users.json

✅ Should contain:
   {
     "9876543210": 123456789
   }
```

---

## 🌐 Flask Server Setup

### Step 1: Start Server

- [ ] Opened another new terminal/command prompt
- [ ] Navigated to project directory
- [ ] Set TELEGRAM_BOT_TOKEN in this terminal
- [ ] Ran: `python app.py`

**Verification:**
```
✅ Should see:
   🚗 Driver Monitoring System Starting...
   📱 Frontend available at: http://localhost:5000
   * Running on http://0.0.0.0:5000
```

**Keep this terminal running!**

---

### Step 2: Verify Server

- [ ] Opened browser
- [ ] Navigated to: `http://localhost:5000`
- [ ] Saw login page with phone input

**Verification:**
```
✅ Browser should show:
   - "Login / Sign Up" heading
   - Phone number input field
   - "Send OTP" button
```

---

## 🧪 Automated Testing

### Run Test Script

- [ ] Opened another terminal
- [ ] Navigated to project directory
- [ ] Set TELEGRAM_BOT_TOKEN in this terminal
- [ ] Ran: `python test_otp_flow.py`

**Verification:**
```
✅ Should see all checks pass:
   ✅ PASS - Environment
   ✅ PASS - Data Files
   ✅ PASS - Telegram Bot
   ✅ PASS - User Registrations
   ✅ PASS - Flask Server
   
   🎉 All checks passed! Your system is ready.
```

---

## 🔐 OTP Flow Testing

### Step 1: Request OTP

- [ ] Opened browser: `http://localhost:5000`
- [ ] Entered registered phone number
- [ ] Clicked "Send OTP"
- [ ] Saw success message: "OTP sent successfully!"
- [ ] OTP input section appeared
- [ ] Timer started counting down from 5:00

**Verification:**
```
✅ Browser should show:
   - "OTP sent successfully!" message (green)
   - OTP input field
   - "Verify OTP" button
   - Timer: "Resend OTP in 4:59"
```

---

### Step 2: Receive OTP

- [ ] Checked Telegram app
- [ ] Received message from bot
- [ ] Message contains 6-digit OTP
- [ ] Message says "Valid for 5 minutes"

**Verification:**
```
✅ Telegram should show:
   "Your OTP is 123456. Valid for 5 minutes."
```

---

### Step 3: Verify OTP

- [ ] Entered 6-digit OTP on website
- [ ] Clicked "Verify OTP"
- [ ] Saw success message: "Login successful!"
- [ ] Redirected to `/home` dashboard

**Verification:**
```
✅ Browser should show:
   - Dashboard page
   - "Driver Monitoring Dashboard" heading
   - Current driver status
   - Navigation buttons (Home, History, Logout)
```

---

## 🎯 Dashboard Access

### Verify Protected Routes

- [ ] Accessed: `http://localhost:5000/home`
  - Should show dashboard (if logged in)
  - Should redirect to login (if not logged in)

- [ ] Accessed: `http://localhost:5000/history`
  - Should show history page (if logged in)
  - Should redirect to login (if not logged in)

**Verification:**
```
✅ When logged in:
   - /home shows dashboard
   - /history shows event logs
   
✅ When not logged in:
   - Both redirect to login page
```

---

## 🔄 Detection System (Optional)

### Start Detection

- [ ] Opened another terminal
- [ ] Navigated to project directory
- [ ] Ran: `python c.py`
- [ ] Camera started
- [ ] Face detection working

**Verification:**
```
✅ Should see:
   - Camera window opens
   - Face landmarks detected
   - Status updates in terminal
```

---

## 📊 System Status Summary

### Running Services

Check that you have these terminals running:

- [ ] **Terminal 1**: `telegram_listener.py`
  ```
  🤖 Telegram bot listener started...
  ```

- [ ] **Terminal 2**: `app.py`
  ```
  🚗 Driver Monitoring System Starting...
  * Running on http://0.0.0.0:5000
  ```

- [ ] **Terminal 3** (Optional): `c.py`
  ```
  Camera initialized
  Face detection active
  ```

---

### Data Files

Check that these files exist and have content:

- [ ] `data/users.json`
  ```json
  {
    "9876543210": 123456789
  }
  ```

- [ ] `data/numbers.txt`
  ```
  (May be empty initially)
  ```

- [ ] `data/logs.csv`
  ```csv
  timestamp,event,number
  (May have sample data)
  ```

---

## 🐛 Troubleshooting Checklist

### If OTP not received:

- [ ] telegram_listener.py is running
- [ ] Phone number is registered in data/users.json
- [ ] TELEGRAM_BOT_TOKEN is set correctly
- [ ] Bot token is valid (check with test script)
- [ ] Phone number format is correct (10 digits, no spaces)

### If can't access dashboard:

- [ ] Completed OTP verification
- [ ] Browser cookies are enabled
- [ ] Session is active (not expired)
- [ ] Flask server is running

### If detection not working:

- [ ] Camera is connected
- [ ] c.py is running
- [ ] shape_predictor_68_face_landmarks.dat file exists
- [ ] OpenCV and dlib are installed correctly

---

## ✅ Final Verification

### Complete System Test

1. **Registration** ✅
   - [ ] Bot created
   - [ ] Phone registered with bot
   - [ ] Appears in data/users.json

2. **Services** ✅
   - [ ] telegram_listener.py running
   - [ ] app.py running
   - [ ] Both accessible

3. **OTP Flow** ✅
   - [ ] Can request OTP
   - [ ] Receive OTP in Telegram
   - [ ] Can verify OTP
   - [ ] Redirected to dashboard

4. **Dashboard** ✅
   - [ ] Can access /home
   - [ ] Can access /history
   - [ ] Can logout
   - [ ] Protected routes work

5. **Detection** (Optional) ✅
   - [ ] c.py starts
   - [ ] Camera works
   - [ ] Status updates

---

## 🎉 Success Criteria

**Your system is fully operational if:**

✅ All services start without errors
✅ OTP is received in Telegram
✅ Login works successfully
✅ Dashboard is accessible
✅ Protected routes require authentication
✅ Test script passes all checks

---

## 📞 Need Help?

If any checkbox is unchecked:

1. **Review the error messages** in the terminal
2. **Check the relevant guide:**
   - START_HERE.md (quick start)
   - SETUP_INSTRUCTIONS.md (detailed setup)
   - FLOW_DIAGRAM.md (visual flow)
3. **Run the test script:** `python test_otp_flow.py`
4. **Verify environment variables** are set in the correct terminal

---

**Once all checkboxes are checked, your system is ready for production use! 🎉**

