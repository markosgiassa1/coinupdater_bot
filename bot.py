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

# === Telegram Message Sender ===
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
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Send error: {e}", flush=True)

# === Fetching Tokens ===
def fetch_tokens():
    try:
        res = requests.get("https://cache.jup.ag/tokens", timeout=10)
        tokens = res.json()[:1000]
        meme_keywords = list("abcdefghijklmnopqrstuvwxyz0123456789") + [
            'panda', 'bonk', 'rat', 'wagmi', 'meme'
        ]
        return [t for t in tokens if any(k in t['name'].lower() for k in meme_keywords)]
    except Exception as e:
        print(f"❌ Token fetch error: {e}", flush=True)
        return []

def fetch_token_data(address):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{address}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json().get("pair", {})
    except Exception as e:
        print(f"❌ Dex error: {e}", flush=True)
    return {}

# === Format Token Info to Message ===
def format_token_msg(token, info):
    name = token['name']
    symbol = token['symbol']
    address = token['address']

    try:
        price_sol = float(info.get("priceNative", 0))
        price_usd = float(info.get("priceUsd", 0))
        mcap = int(float(info.get("fdv", 0)))
        volume = int(float(info.get("volume", {}).get("h24", 0)))
        liquidity = int(float(info.get("liquidity", {}).get("base", 0)))
        holders = info.get("holders", "?")
    except:
        return None

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

# === Core Bot Logic ===
def bot_logic():
    print("🟢 Bot logic started", flush=True)

    # Only send "Started" once
    if not os.path.exists("started.flag"):
        send_telegram_message("🚀 Meme Bot Started!", CHAT_ID)
        with open("started.flag", "w") as f:
            f.write("yes")

    # Welcome message once
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
            if not tokens:
                print("⚠️ No tokens fetched.", flush=True)
                time.sleep(60)
                continue

            for token in tokens[:10]:
                address = token['address']
                if address in posted_tokens:
                    continue

                info = fetch_token_data(address)
                if info:
                    msg = format_token_msg(token, info)
                    if msg:
                        send_telegram_message(msg, CHAT_ID, inline_keyboard)
                        posted_tokens.append(address)
                        time.sleep(3)
                else:
                    print(f"⚠️ Skipping {token['name']} - No valid Dex info", flush=True)

            time.sleep(180)

        except Exception as e:
            print(f"❌ Loop crash: {e}", flush=True)
            send_telegram_message(f"⚠️ Bot crashed: {e}", CHAT_ID)
            time.sleep(30)

# === Crash-Proof Runner ===
def run_bot_forever():
    while True:
        try:
            bot_logic()
        except Exception as e:
            print(f"🔥 Total failure: {e}", flush=True)
            send_telegram_message(f"🔥 Bot totally crashed: {e}", CHAT_ID)
            time.sleep(60)

# === Launch Server and Bot ===
if __name__ == "__main__":
    threading.Thread(target=run_bot_forever, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
