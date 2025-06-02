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

inline_keyboard = {
    "inline_keyboard": [
        [{"text": "🔗 Refer Friends", "switch_inline_query": "invite "}],
        [{"text": "📢 Join Our Group", "url": "https://t.me/digistoryan"}]
    ]
}

def send_telegram_message(msg, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code, r.text
    except Exception as e:
        return 0, str(e)

def fetch_tokens():
    try:
        res = requests.get("https://cache.jup.ag/tokens", timeout=10)
        res.raise_for_status()
        tokens = res.json()[:100]
        meme_keywords = ['dog', 'pepe', 'cat', 'elon', 'moon', 'baby', 'inu']
        return [t for t in tokens if any(k in t['name'].lower() for k in meme_keywords)]
    except Exception as e:
        send_telegram_message(f"❌ Error fetching tokens: {e}")
        return []

def fetch_token_data(address):
    try:
        res = requests.get(f"https://api.dexscreener.com/latest/dex/pairs/solana/{address}", timeout=10)
        if res.status_code == 200:
            return res.json().get("pair", {})
        else:
            send_telegram_message(f"⚠️ DexScreener error {res.status_code}")
    except Exception as e:
        send_telegram_message(f"❌ DexScreener exception: {e}")
    return {}

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

def run_bot():
    send_telegram_message("🚀 Meme Bot Started!")

    if not os.path.exists("welcome_sent.flag"):
        welcome_text = (
            "👋 *Welcome to @coinupdater_bot!*\n\n"
            "This bot automatically tracks and posts *newly launched meme tokens* on the *Solana blockchain*.\n\n"
            "🔍 *How It Works:*\n"
            "• Scans the top 100 new tokens from [Jupiter Aggregator](https://jup.ag)\n"
            "• Filters for meme-related tokens: `DOG`, `PEPE`, `CAT`, `ELON`, `BABY`, `INU`, etc\n"
            "• Verifies the tokens via [DexScreener](https://dexscreener.com)\n"
            "• Posts live stats like:\n"
            "  ├ 💸 Price (SOL & USD)\n"
            "  ├ 📊 Market Cap\n"
            "  ├ 🔁 24h Volume\n"
            "  ├ 💧 Liquidity Pool (LP)\n"
            "  └ 🪙 Number of Holders\n\n"
            "📢 *Example Message Format:*\n"
            "`DOGEPEPE / $DPEPE`\n"
            "`0.0012 SOL ($0.15)` | `MCap: $250K` | `Vol 24h: 12K SOL`\n"
            "`LP: 300 SOL` | `Holders: 192`\n"
            "[View on DexScreener](https://dexscreener.com)\n"
            "[Buy on Jupiter](https://jup.ag)\n\n"
            "📣 Use the buttons below to refer friends or join our group.\n"
            "💰 *Support this bot:* `{}`\n\n"
            "✅ Enjoy fast alpha alerts and instant meme token discoveries!".format(DONATION_WALLET)
        )
        send_telegram_message(welcome_text, inline_keyboard)
        with open("welcome_sent.flag", "w") as f:
            f.write("ok")

    while True:
        try:
            tokens = fetch_tokens()
            for token in tokens[:3]:
                addr = token["address"]
                if addr not in posted_tokens:
                    info = fetch_token_data(addr)
                    if info:
                        msg = format_token_msg(token, info)
                        send_telegram_message(msg, inline_keyboard)
                        posted_tokens.append(addr)
                        time.sleep(3)

            time.sleep(180)
        except Exception as e:
            send_telegram_message(f"❌ Main loop error:\n{e}")
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
