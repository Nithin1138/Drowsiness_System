# telegram_listener.py
import requests
import time
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DATA_FILE = "data/users.json"

os.makedirs("data", exist_ok=True)

def save_mapping(phone, chat_id):
    if not phone:
        return
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    data[phone] = chat_id
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[INFO] Linked phone {phone} → chat {chat_id}")

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"offset": offset, "timeout": 30}
    # Set a read/connect timeout slightly larger than Telegram's internal poll timeout (30s)
    resp = requests.get(url, params=params, timeout=35)
    return resp.json()

def main():



    # Verify bot token is loaded
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
        print("[ERROR] Bot token not loaded from .env file!")
        print(f"[ERROR] Current token: {BOT_TOKEN}")
        print("[ERROR] Please check your .env file contains: TELEGRAM_BOT_TOKEN=your_token")
        return

    print(f"[INFO] Bot token loaded: {BOT_TOKEN[:20]}...")
    print("[INFO] Polling for updates...")

    offset = None
    while True:
        try:
            updates = get_updates(offset)
            if "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    message = update.get("message", {})
                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text", "")
                    if text and chat_id:
                        print(f"[INFO] Received message: {text} from chat {chat_id}")
                        if text.startswith("/start"):
                            reply = (
                                "Welcome to the Driver Safety Bot 🚗\n"
                                "Please send your *phone number* (10 digits) to register."
                            )
                            requests.post(
                                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                                json={"chat_id": chat_id, "text": reply},
                                timeout=10
                            )
                        elif text.isdigit() and len(text) == 10:
                            save_mapping(text, chat_id)
                            reply = (
                                f"✅ Registered successfully for phone {text}.\n"
                                "Now you can use the Driver Monitoring web app!"
                            )
                            requests.post(
                                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                                json={"chat_id": chat_id, "text": reply},
                                timeout=10
                            )
        except requests.exceptions.RequestException as re:
            print(f"[WARN] Telegram connection issue: {re}")
            print("[INFO] Please verify your internet connection or proxy settings. Retrying in 10 seconds...")
            time.sleep(10)
            continue
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            import traceback
            traceback.print_exc()
        time.sleep(2)

if __name__ == "__main__":
    main()
