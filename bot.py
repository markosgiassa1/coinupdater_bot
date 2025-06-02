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

# Inline keyboard for Telegram message
inline_keyboard = {
    "inline_keyboard": [
        [{"text": "🔗 Refer Friends", "switch_inline_query": "invite "}],
        [{"text": "📢 Join Our Group", "url": "https://t.me/digistoryan"}]
    ]
}

# === Send Telegram Message ===
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

# === Fetch Meme Tokens from Jupiter ===
def fetch_tokens():
    try:
        res = requests.get("https://cache.jup.ag/tokens", timeout=10)
        tokens = res.json()[:1000]
        meme_keywords = [
            'bonk', 'dog', 'cat', 'meme', 'panda', 'rat', 'elon', 'pepe',
            'wagmi', 'jeet', 'snek', 'wojak', 'moon', 'pump'
        ]
        filtered = [t for t in tokens if any(k in t['name'].lower() for k in meme_keywords)]
        return filtered
    except Exception as e:
        print(f"❌ Token fetch error: {e}", flush=True)
        return []

# === Fetch Price and Market Info from Dexscreener ===
def fetch_token_data(address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{address}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if "pair" in data:
                return data["pair"]
            else:
                print(f"⚠️ Token {address} not found on DexScreener.")
        else:
            print(f"❌ DexScreener error: {res.status_code}")
    except Exception as e:
        print(f"❌ Dex error: {e}", flush=True)
    return {}

# === Format Message to Send ===
def format_token_msg(token, info):
    name = token['name']
    symbol = token['symbol']
    address = token['address']

    price_sol = float(info.get("priceNative", 0))
    price_usd = float(info.get("priceUsd", 0))
    mcap = int(float(info.get("fdv", 0)))
    volume = int(float(info.get("volume", {}).get("h24", 0)))
    liquidity = int(float(info.get("liquidity", {}).get("usd", 0)))

    return (
        f"⏺ | 🐶 *{name}* / `${symbol}`\n"
        f"🆕 New Meme Token | 🟢 Launched recently\n"
        f"💸 `{price_sol:.4f} SOL` (${price_usd:.2f})\n"
        f"📊 Mkt Cap: `${mcap:,}` | 🔁 Vol 24h: `{volume:,} USD`\n"
        f"💧 LP: `{liquidity:,} USD`\n\n"
        f"[📍 View on DexScreener](https://dexscreener.com/solana/{address})\n"
        f"[🟢 Buy on Jupiter](https://jup.ag/swap/SOL-{address})\n"
        f"💰 *Donate:* `{DONATION_WALLET}`"
    )

# === Main Bot Loop ===
def run_bot():
    send_telegram_message("🚀 Meme Bot Started!", CHAT_ID)

    if not os.path.exists("welcome_sent.flag"):
        welcome_text = (
            "👋 Welcome to @coinupdater_bot!\n\n"
            "Get the latest meme tokens on Solana.\n"
            "Use the buttons below to refer friends or join our group."
        )
        send_telegram_message(welcome_text, CHAT_ID, inline_keyboard)
        with open("welcome_sent.flag", "w") as f:
            f.write("ok")

    while True:
        try:
            tokens = fetch_tokens()
            print(f"🔍 Fetched {len(tokens)} meme tokens")

            if not tokens:
                send_telegram_message("⚠️ No meme tokens found.", CHAT_ID)

            for token in tokens[:5]:  # Change limit as needed
                address = token['address']
                if address in posted_tokens:
                    continue

                print(f"🧪 Checking {token['name']} - {address}")
                info = fetch_token_data(address)

                if info:
                    msg = format_token_msg(token, info)
                    send_telegram_message(msg, CHAT_ID, inline_keyboard)
                    posted_tokens.append(address)
                    time.sleep(3)
                else:
                    print(f"⚠️ No valid Dex info for {token['name']} ({address})")

            time.sleep(180)

        except Exception as e:
            print(f"❌ Bot crashed: {e}")
            send_telegram_message(f"❌ Bot crashed: {e}", CHAT_ID)
            time.sleep(30)

# === Launch Bot & Web Server ===
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
