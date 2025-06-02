from flask import Flask
import threading
import requests
import time
import json
import os
from collections import deque

# === Web server for Fly.io health ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Meme Bot is Running"

# === Bot Configuration ===
BOT_TOKEN = "7639604753:AAH6_rlQAFgoPr2jlShOA5SKgLT57Br_BxU"
CHAT_ID = "7636990835"
DONATION_WALLET = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"

# Cache to prevent reposting
posted_tokens = deque(maxlen=250)

# Inline buttons
inline_keyboard = {
    "inline_keyboard": [
        [{"text": "🔗 Refer Friends", "switch_inline_query": "invite "}],
        [{"text": "📢 Join Our Group", "url": "https://t.me/digistoryan"}]
    ]
}

# === Messaging ===
def send_telegram_message(msg, chat_id, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"❌ Send error: {e}", flush=True)

# === Token Fetching ===
def fetch_tokens():
    try:
        res = requests.get("https://cache.jup.ag/tokens", timeout=10)
        return res.json()  # Return all tokens, not just top 100
    except Exception as e:
        print(f"❌ Token fetch error: {e}", flush=True)
        return []

def fetch_token_data(address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{address}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json().get("pair", {})
    except Exception as e:
        print(f"❌ Dex error: {e}", flush=True)
    return {}

# === Format Message ===
def format_token_msg(token, info):
    name = token['name']
    symbol = token['symbol']
    address = token['address']

    price_sol = float(info.get("priceNative", 0))
    price_usd = float(info.get("priceUsd", 0))
    mcap = int(float(info.get("fdv", 0)))
    volume = int(float(info.get("volume", {}).get("h24", 0)))
    liquidity = int(float(info.get("liquidity", {}).get("base", 0)))
    holders = info.get("holders", "?")

    return (
        f"⏺ | 📈 *{name}* / `${symbol}`\n"
        f"🆕 Token with Live Data\n"
        f"💸 `{price_sol:.4f} SOL` (${price_usd:.2f})\n"
        f"📊 Mkt Cap: `${mcap:,}` | 🔁 Vol 24h: `{volume:,} SOL`\n"
        f"💧 LP: `{liquidity:,} SOL` | 🪙 Holders: `{holders}`\n\n"
        f"[📍 View on DexScreener](https://dexscreener.com/solana/{address})\n"
        f"[🟢 Buy on Jupiter](https://jup.ag/swap/SOL-{address})\n"
        f"💰 *Donate:* `{DONATION_WALLET}`"
    )

# === Bot Runner ===
def run_bot():
    send_telegram_message("🚀 Token Bot Started!", CHAT_ID)

    if not os.path.exists("welcome_sent.flag"):
        welcome_text = (
            "👋 Welcome to @coinupdater_bot!\n\n"
            "Now scanning and sharing all tokens with live data on Solana.\n"
            "Use the buttons below to refer friends or join our group."
        )
        send_telegram_message(welcome_text, CHAT_ID, inline_keyboard)
        with open("welcome_sent.flag", "w") as f:
            f.write("ok")

    while True:
        try:
            tokens = fetch_tokens()
            found = 0

            for token in tokens:
                address = token['address']
                if address in posted_tokens:
                    continue

                info = fetch_token_data(address)
                if info:
                    msg = format_token_msg(token, info)
                    send_telegram_message(msg, CHAT_ID, inline_keyboard)
                    posted_tokens.append(address)
                    found += 1
                    time.sleep(3)

                if found >= 5:
                    break  # Only post up to 5 tokens per loop

            if found == 0:
                send_telegram_message("⚠️ No tokens with live data found.", CHAT_ID)

            time.sleep(180)

        except Exception as e:
            send_telegram_message(f"❌ Bot crashed: {e}", CHAT_ID)
            time.sleep(30)

# === Launch ===
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
