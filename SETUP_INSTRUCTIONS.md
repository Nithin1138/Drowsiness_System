# Driver Monitoring System - OTP Setup Instructions

## Overview
This system uses Telegram Bot for OTP delivery. The flow is:
1. User enters phone number → clicks "Send OTP"
2. Flask generates OTP and sends via Telegram Bot
3. OTP appears in Telegram chat
4. User enters OTP on site
5. Flask verifies OTP, starts session
6. User sees dashboard at `/home`

## Prerequisites
- Python 3.8+
- Telegram account
- All dependencies from `requirements.txt`

## Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts to create your bot:
   - Choose a name (e.g., "Driver Safety Bot")
   - Choose a username (e.g., "driver_safety_bot")
4. BotFather will give you a **Bot Token** like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
5. **Save this token** - you'll need it!

## Step 2: Set Environment Variables

### On Windows (PowerShell):
```powershell
$env:TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
```

### On Windows (Command Prompt):
```cmd
set TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
```

### On Linux/Mac:
```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
```

**Important:** Replace `YOUR_BOT_TOKEN_HERE` with the actual token from BotFather.

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Start the Telegram Listener

The Telegram listener maps phone numbers to Telegram chat IDs.

Open a **new terminal/command prompt** and run:

```bash
python telegram_listener.py
```

You should see:
```
🤖 Telegram bot listener started...
```

**Keep this terminal running!**

## Step 5: Register Your Phone Number with Telegram

1. Open Telegram
2. Search for your bot (the username you created)
3. Click "Start" or send `/start`
4. The bot will reply with a welcome message
5. Send your **10-digit phone number** (e.g., `9876543210`)
6. The bot will confirm registration

This links your phone number to your Telegram chat ID.

## Step 6: Start the Flask Application

Open **another terminal/command prompt** and run:

```bash
python app.py
```

You should see:
```
🚗 Driver Monitoring System Starting...
📱 Frontend available at: http://localhost:5000
```

## Step 7: Test the OTP Flow

1. Open browser and go to: `http://localhost:5000`
2. Enter your registered phone number (the one you sent to the bot)
3. Click "Send OTP"
4. Check your Telegram - you should receive an OTP message
5. Enter the OTP on the website
6. Click "Verify OTP"
7. You should be redirected to `/home` dashboard

## Step 8: Start Detection System (Optional)

To enable driver monitoring with camera:

```bash
python c.py
```

This will:
- Start camera monitoring
- Detect drowsiness, yawning, etc.
- Send status updates to Flask backend
- Control Arduino (if connected)

## Troubleshooting

### OTP not received in Telegram?

1. **Check if telegram_listener.py is running**
   - You should see it running in a terminal
   
2. **Verify phone number registration**
   - Send your phone number to the bot again
   - Check `data/users.json` - it should contain your mapping:
     ```json
     {
       "9876543210": 123456789
     }
     ```

3. **Check environment variable**
   - In the terminal where you run `app.py`, verify:
     ```bash
     # Windows PowerShell
     echo $env:TELEGRAM_BOT_TOKEN
     
     # Linux/Mac
     echo $TELEGRAM_BOT_TOKEN
     ```

4. **Check Flask logs**
   - Look for messages like:
     - `[INFO] Telegram message sent to chat...` (success)
     - `[WARN] No Telegram mapping for number...` (not registered)
     - `[WARN] Telegram failed...` (bot token issue)

### "Failed to send OTP" error?

- Make sure `telegram_listener.py` is running
- Verify you registered your phone number with the bot
- Check that `TELEGRAM_BOT_TOKEN` environment variable is set

### Can't access /home page?

- Make sure you completed OTP verification
- Check browser console for errors
- Try logging out and logging in again

## File Structure

```
VIEW/
├── app.py                          # Flask backend
├── telegram_listener.py            # Telegram bot listener
├── c.py                           # Detection system
├── templates/
│   ├── index.html                 # Login page (OTP entry)
│   ├── home.html                  # Dashboard
│   └── history.html               # Event history
├── data/
│   ├── users.json                 # Phone → Chat ID mapping
│   ├── numbers.txt                # Registered numbers
│   └── logs.csv                   # Event logs
└── requirements.txt
```

## Running in Production

For production deployment:

1. **Use a process manager** (e.g., PM2, systemd)
2. **Set environment variables permanently**
3. **Use HTTPS** for the Flask app
4. **Consider using a database** instead of JSON files
5. **Add rate limiting** to prevent OTP spam

## Security Notes

- Never commit your `TELEGRAM_BOT_TOKEN` to version control
- Use environment variables for sensitive data
- OTPs expire after 5 minutes
- Maximum 3 OTP verification attempts
- Sessions are required to access protected pages

## Support

If you encounter issues:
1. Check all terminals are running (Flask + Telegram listener)
2. Verify environment variables are set
3. Check `data/users.json` for phone number mapping
4. Review Flask console logs for error messages

