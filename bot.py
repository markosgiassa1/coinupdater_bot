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

inline_keyboard = {
    "inline_keyboard": [
        [{"text": "🔗 Refer Friends", "switch_inline_query": "invite "}],
        [{"text": "📢 Join Our Group", "url": "https://t.me/digistoryan"}]
    ]
}

# === Telegram message sender ===
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
        r = requests.post(url, data=payload, timeout=10)
        print(f"✅ Sent message: {r.status_code}")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# === Get meme tokens from Jupiter ===
def fetch_tokens():
    try:
        res = requests.get("https://cache.jup.ag/tokens", timeout=10)
        res.raise_for_status()
        all_tokens = res.json()
        meme_keywords = ['dog', 'pepe', 'cat', 'elon', 'moon', 'baby', 'inu']
        return [t for t in all_tokens if any(k in t['name'].lower() for k in meme_keywords)]
    except Exception as e:
        print(f"❌ Token fetch error: {e}")
        return []

# === DexScreener + fallback ===
def fetch_token_data(address, fallback=None):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{address}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            pair = res.json().get("pair")
            if pair:
                return pair
    except Exception as e:
        print(f"❌ Dex error for {address}: {e}")
    
    # Fallback
    print(f"ℹ️ No Dex info for {fallback.get('symbol')} - using fallback")
    return {
        "name": fallback.get("name", "?"),
        "symbol": fallback.get("symbol", "?"),
        "priceNative": "0",
        "priceUsd": "0",
        "fdv": 0,
        "volume": {"h24": 0},
        "liquidity": {"base": 0},
        "holders": "?"
    }

# === Message formatter ===
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
        f"⏺ | 🐶 *{name}* / `${symbol}`\n"
        f"🆕 New Meme Token | 🟢 Launched recently\n"
        f"💸 `{price_sol:.4f} SOL` (${price_usd:.2f})\n"
        f"📊 Mkt Cap: `${mcap:,}` | 🔁 Vol 24h: `{volume:,} SOL`\n"
        f"💧 LP: `{liquidity:,} SOL` | 🪙 Holders: `{holders}`\n\n"
        f"[📍 View on DexScreener](https://dexscreener.com/solana/{address})\n"
        f"[🟢 Buy on Jupiter](https://jup.ag/swap/SOL-{address})\n"
        f"💰 *Donate:* `{DONATION_WALLET}`"
    )

# === Bot logic ===
def run_bot():
    print("🚀 Meme Bot Started!")

    # Welcome message (send only once)
    if not os.path.exists("welcome_sent.flag"):
        welcome_text = (
            "👋 Welcome to @coinupdater_bot!\n\n"
            "Get the latest meme tokens on Solana.\n"
            "Use the buttons below to refer friends or join our group."
        )
        send_telegram_message(welcome_text, CHAT_ID, inline_keyboard)
        with open("welcome_sent.flag", "w") as f:
            f.write("ok")

    restart_counter = 0

    while True:
        try:
            print("🔍 Scanning for new tokens...")
            tokens = fetch_tokens()
            for token in tokens[:5]:
                address = token['address']
                if address not in posted_tokens:
                    info = fetch_token_data(address, fallback=token)
                    if info:
                        msg = format_token_msg(token, info)
                        send_telegram_message(msg, CHAT_ID, inline_keyboard)
                        posted_tokens.append(address)
                        print(f"✅ Posted {token['symbol']}")
                        time.sleep(3)

            restart_counter += 1
            if restart_counter >= 100:
                print("♻️ Restarting bot to clear cache")
                break

            time.sleep(180)

        except Exception as e:
            print(f"❌ Main loop error: {e}")
            time.sleep(10)

# === Run ===
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
