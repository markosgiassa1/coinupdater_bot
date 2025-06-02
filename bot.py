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
posted_tokens = deque(maxlen=300)

# Meme-related keywords to detect tokens
MEME_KEYWORDS = ['dog', 'pepe', 'cat', 'elon', 'moon', 'baby', 'inu', 'panda', 'bonk', 'rat', 'wagmi', 'meme']

def send_telegram_message(text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    try:
        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code == 200:
            print(f"✅ Message sent")
        else:
            print(f"❌ Telegram error {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"❌ Exception sending telegram message: {e}")

def fetch_tradable_tokens():
    url = "https://api.jup.ag/tokens/v1/mints/tradable"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        tokens = resp.json()
        meme_tokens = [t for t in tokens if any(k in t["name"].lower() for k in MEME_KEYWORDS)]
        print(f"🔍 Found {len(meme_tokens)} meme tokens")
        return meme_tokens
    except Exception as e:
        print(f"❌ Error fetching tokens from Jupiter API: {e}")
        return []

def fetch_token_data(address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{address}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get("pair")
            return data
        else:
            print(f"❌ DexScreener status {resp.status_code} for {address}")
    except Exception as e:
        print(f"❌ DexScreener exception: {e}")
    return None

def format_token_message(token, info):
    name = token.get("name", "Unknown")
    symbol = token.get("symbol", "???")
    address = token.get("address", "unknown")

    if info:
        price_sol = float(info.get("priceNative", 0))
        price_usd = float(info.get("priceUsd", 0))
        fdv = int(float(info.get("fdv", 0)))
        volume_24h = int(float(info.get("volume", {}).get("h24", 0)))
        liquidity = int(float(info.get("liquidity", {}).get("base", 0)))
        holders = info.get("holders", "?")

        msg = (
            f"🚀 *{name}* / `${symbol}`\n"
            f"🆕 *New Meme Token* just dropped!\n"
            f"💸 Price: `{price_sol:.4f} SOL` (${price_usd:.2f})\n"
            f"📈 Mkt Cap: `${fdv:,}` | Vol: `{volume_24h:,} SOL`\n"
            f"💧 LP: `{liquidity:,} SOL` | 👥 Holders: `{holders}`\n\n"
            f"[📊 View on DexScreener](https://dexscreener.com/solana/{address})\n"
            f"[🛒 Buy on Jupiter](https://jup.ag/swap/SOL-{address})\n"
            f"❤️ Donate: `79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz`"
        )
    else:
        msg = (
            f"🚀 *{name}* / `${symbol}`\n"
            f"⚠️ No price data available yet\n\n"
            f"[🛒 Buy on Jupiter](https://jup.ag/swap/SOL-{address})\n"
            f"❤️ Donate: `79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz`"
        )
    return msg

def run_bot():
    print("🚀 Meme Bot Started")

    # Send welcome message once
    send_telegram_message(
        "👋 Welcome to *Meme Token Bot*! Stay updated with hot new Solana meme tokens.",
        reply_markup={
            "inline_keyboard": [
                [{"text": "📢 Join Our Group", "url": "https://t.me/digistoryan"}],
                [{"text": "🔗 Refer Friends", "switch_inline_query": "invite "}],
            ]
        },
    )

    while True:
        tokens = fetch_tradable_tokens()

        # Filter only new tokens
        new_tokens = [t for t in tokens if t.get("address") and t.get("address") not in posted_tokens]
        count_sent = 0

        for token in new_tokens[:10]:  # limit 10 per cycle
            address = token["address"]
            info = fetch_token_data(address)
            msg = format_token_message(token, info)
            send_telegram_message(msg)
            posted_tokens.append(address)
            count_sent += 1
            time.sleep(3)

        if count_sent == 0:
            print("ℹ️ No new tokens sent in this round.")

        print("⏳ Waiting 3 minutes before next round...\n")
        time.sleep(180)

# Start bot thread + web server
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
