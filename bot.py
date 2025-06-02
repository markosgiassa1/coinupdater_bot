from flask import Flask
import threading
import requests
import time
import json
import os
from collections import deque

# === Web Server (for Fly.io health check) ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Coin Updater Bot is Running"

# === Telegram Bot Configuration ===
BOT_TOKEN = "7639604753:AAH6_rlQAFgoPr2jlShOA5SKgLT57Br_BxU"
CHAT_ID = "7636990835"
DONATION_WALLET = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"

posted_tokens = deque(maxlen=250)  # Prevent reposting same tokens

inline_keyboard = {
    "inline_keyboard": [
        [{"text": "🔗 Refer Friends", "switch_inline_query": "invite "}],
        [{"text": "💰 Donate", "url": f"https://t.me/donate?wallet={DONATION_WALLET}"}],  # Replace URL if you want real donation page
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
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"❌ Send error: {e}", flush=True)

# === Solana Token Fetcher ===
def fetch_tokens():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        pairs = data.get("pairs", [])

        solana_tokens = []
        for pair in pairs:
            base = pair.get("baseToken", {})
            quote = pair.get("quoteToken", {})

            # Filter valid SPL token addresses (usually > 32 chars)
            if not base.get("address") or len(base["address"]) < 32:
                continue

            # Skip wrapped SOL, WSOL, USDC, etc.
            symbol = base.get("symbol", "").lower()
            if symbol in ["sol", "wsol", "usdc", "usdt"]:
                continue

            solana_tokens.append({
                "address": base["address"],
                "name": base["name"],
                "symbol": base["symbol"]
            })

        return solana_tokens

    except Exception as e:
        send_telegram_message(f"❌ Error fetching Solana tokens:\n{e}", CHAT_ID)
        return []

# === Token Detail Fetcher ===
def fetch_token_data(address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{address}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json().get("pair", {})
    except Exception as e:
        print(f"❌ Dex error: {e}", flush=True)
    return {}

# === Token Info Formatter ===
def format_token_msg(token, info):
    name = token.get('name', '?')
    symbol = token.get('symbol', '?')
    address = token.get('address', '?')

    try:
        price_sol = float(info.get("priceNative", 0))
        price_usd = float(info.get("priceUsd", 0))
        mcap = int(float(info.get("fdv", 0)))
        volume = int(float(info.get("volume", {}).get("h24", 0)))
        liquidity = int(float(info.get("liquidity", {}).get("base", 0)))
        holders = info.get("holders", "?")
    except:
        price_sol, price_usd, mcap, volume, liquidity = 0, 0, 0, 0, 0
        holders = "?"

    return (
        f"⏺ | 🪙 *{name}* / `${symbol}`\n"
        f"🆕 New Token Detected on *Solana*\n"
        f"💸 `{price_sol:.4f} SOL` (${price_usd:.2f})\n"
        f"📊 Mkt Cap: `${mcap:,}` | 🔁 24h Vol: `{volume:,} SOL`\n"
        f"💧 LP: `{liquidity:,} SOL` | 🪙 Holders: `{holders}`\n\n"
        f"[📍 View on DexScreener](https://dexscreener.com/solana/{address})\n"
        f"[🟢 Buy on Jupiter](https://jup.ag/swap/SOL-{address})\n\n"
        f"💰 *Donate:* `{DONATION_WALLET}`"
    )

# === Bot Logic ===
def run_bot():
    send_telegram_message("🚀 Coin Updater Bot Started!", CHAT_ID, inline_keyboard)

    # Welcome message (sent once)
    if not os.path.exists("welcome_sent.flag"):
        welcome_text = (
            "👋 Welcome to @coinupdater_bot!\n\n"
            "This bot automatically tracks and posts *newly launched tokens* on the Solana blockchain.\n\n"
            "🔍 What It Does:\n"
            "• Scans newest tokens from DexScreener\n"
            "• Posts:\n"
            "  ├ 💸 Price (SOL & USD)\n"
            "  ├ 📊 Market Cap\n"
            "  ├ 🔁 Volume\n"
            "  ├ 💧 LP\n"
            "  └ 🪙 Holders\n\n"
            f"💰 Support the bot: `{DONATION_WALLET}`\n\n"
            "✅ Get instant alerts for *real* Solana tokens!"
        )
        send_telegram_message(welcome_text, CHAT_ID, inline_keyboard)
        with open("welcome_sent.flag", "w") as f:
            f.write("ok")

    # Main loop
    while True:
        try:
            tokens = fetch_tokens()

            if not tokens:
                send_telegram_message("⚠️ No Solana tokens found.", CHAT_ID, inline_keyboard)

            for token in tokens[:5]:  # Process top 5 new tokens
                address = token.get('address')
                if not address or address in posted_tokens:
                    continue

                info = fetch_token_data(address)
                if info:
                    msg = format_token_msg(token, info)
                    send_telegram_message(msg, CHAT_ID, inline_keyboard)
                    posted_tokens.append(address)
                    time.sleep(3)
                else:
                    send_telegram_message(
                        f"⚠️ `{token.get('name', '?')}` has no Dex data.\n`{address}`", CHAT_ID, inline_keyboard
                    )

            time.sleep(180)  # Check every 3 minutes

        except Exception as e:
            send_telegram_message(f"❌ Bot crashed: {e}", CHAT_ID, inline_keyboard)
            time.sleep(30)

# === Launch ===
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
