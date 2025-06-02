from flask import Flask
import threading
import requests
import time
import json
from collections import deque

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Meme Bot is Running"

# === Configuration ===
BOT_TOKEN = "7639604753:AAH6_rlQAFgoPr2jlShOA5SKgLT57Br_BxU"
CHAT_ID = "7636990835"
DONATION_WALLET = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"

posted_tokens = deque(maxlen=1000)

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
        print(f"Telegram send error: {e}")
        return 0, str(e)

def fetch_tokens():
    try:
        url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        pairs = data.get("pairs", [])[:100]

        tokens = []
        for pair in pairs:
            if "baseToken" in pair:
                tokens.append({
                    "address": pair["baseToken"]["address"],
                    "name": pair["baseToken"]["name"],
                    "symbol": pair["baseToken"]["symbol"]
                })
        return tokens
    except Exception as e:
        send_telegram_message(f"❌ Error fetching Dex tokens:\n{e}")
        return []

def fetch_token_data(address):
    try:
        res = requests.get(f"https://api.dexscreener.com/latest/dex/pairs/solana/{address}", timeout=10)
        if res.status_code == 200:
            return res.json().get("pair", {})
        else:
            print(f"DexScreener error for {address}: {res.status_code}")
            return {}
    except Exception as e:
        print(f"DexScreener exception: {e}")
        return {}

def format_token_msg(token, info):
    name = token['name']
    symbol = token['symbol']
    address = token['address']
    emoji = "🐶" if is_meme_token(name) else "🧠"

    price_sol = float(info.get("priceNative", 0))
    price_usd = float(info.get("priceUsd", 0))
    mcap = int(float(info.get("fdv", 0)))

    volume = int(float(info.get("volume", {}).get("h24", 0)))
    volume_display = f"{volume:,} SOL" if volume > 0 else "❌"

    liquidity = int(float(info.get("liquidity", {}).get("base", 0)))
    liquidity_display = f"{liquidity:,} SOL" if liquidity > 0 else "❌"

    holders = info.get("holders")
    holders_display = f"{holders}" if holders not in (None, "?", 0) else "❌"

    return (
        f"⏺ | {emoji} *{name}* / `${symbol}`\n"
        f"🆕 New Token | 🟢 Just Launched\n"
        f"💸 `{price_sol:.4f} SOL` (${price_usd:.2f})\n"
        f"📊 Mkt Cap: `${mcap:,}` | 🔁 Vol 24h: `{volume_display}`\n"
        f"💧 LP: `{liquidity_display}` | 🪙 Holders: `{holders_display}`\n\n"
        f"[📍 View on DexScreener](https://dexscreener.com/solana/{address})\n"
        f"[🟢 Buy on Jupiter](https://jup.ag/swap/SOL-{address})\n"
        f"💰 *Donate:* `{DONATION_WALLET}`"
    )

if not is_meme_token(name):
    print(f"⏩ Not meme: {name}")
    continue
    
def run_bot():
    send_telegram_message("🚀 Meme Bot loop is now running...")

    while True:
        try:
            tokens = fetch_tokens()
            if not tokens:
                send_telegram_message("❌ No tokens fetched from Jupiter.")
                time.sleep(60)
                continue

            for token in tokens[:20]:
                addr = token.get("address")
                name = token.get("name", "")
                symbol = token.get("symbol", "")

                if not addr or addr in posted_tokens:
                    continue

                if not is_meme_token(name):
                    print(f"⏩ Not meme: {name}")
                    continue

                info = fetch_token_data(addr)
                if not info or not info.get("priceNative"):
                    print(f"❌ No Dex data for {name}")
                    continue

                msg = format_token_msg(token, info)
                if msg:
                    send_telegram_message(msg, inline_keyboard)
                    print(f"✅ Posted {name} ({symbol})")
                    posted_tokens.append(addr)
                    time.sleep(3)
                else:
                    print(f"⚠️ Could not format message for {name}")

            time.sleep(180)
        except Exception as e:
            print(f"🔴 Loop Error: {e}")
            send_telegram_message(f"❌ Bot crashed:\n{e}")
            time.sleep(60)

def start_thread():
    thread = threading.Thread(target=run_bot)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    start_thread()
    app.run(debug=False, host='0.0.0.0', port=5000)
