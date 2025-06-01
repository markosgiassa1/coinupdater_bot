import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

msg = "Test message from Fly.io"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": msg,
}
resp = requests.post(url, data=payload)
print(f"Status: {resp.status_code}, Response: {resp.text}")
