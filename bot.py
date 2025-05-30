import requests
import time
import json
import os

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DONATION_WALLET = os.getenv("DONATION_WALLET")

# Helper to send a Telegram message
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
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to send message: {e}")

# Fetch all tokens from Jupiter and filter by meme keywords
def fetch_tokens():
    url = "https://cache.jup.ag/tokens"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        tokens = res.json()
        meme_keywords = ['dog', 'pepe', 'cat', 'elon', 'moon', 'baby', 'inu']
        return [t for t in tokens if any(k in t['name'].lower() for k in meme_keywords)]
    except Exception as e:
        print("❌ Token fetch error:", e)
        return []

# Get token price and data from DexScreener
def fetch_token_data(address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{address}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json().get("pair", {})
    except Exception as e:
        print(f"❌ Dex data error for {address}: {e}")
    return {}

# Format the token data into a message
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

# Buttons for Telegram inline keyboard
inline_keyboard = {
    "inline_keyboard": [
        [{"text": "🔗 Refer Friends", "switch_inline_query": "invite "}],
        [{"text": "📢 Join Our Group", "url": "https://t.me/digistoryan"}]
    ]
}

# Welcome message (send once)
welcome_text = (
    "👋 Welcome to @coinupdater_bot!\n\n"
    "Get the latest new meme tokens on Solana.\n"
    "Use the buttons below to refer friends or join our group."
)

# Send once at startup
try:
    send_telegram_message(welcome_text, CHAT_ID, inline_keyboard)
except Exception as e:
    print("❌ Could not send welcome message:", e)

# Keep track of tokens we already posted
posted_tokens = set()

# 🔁 Main loop
while True:
    print("🔍 Scanning for new meme tokens...")
    try:
        tokens = fetch_tokens()
        for token in tokens[:3]:  # Limit how many we process
            address = token['address']
            if address not in posted_tokens:
                info = fetch_token_data(address)
                if info:
                    msg = format_token_msg(token, info)
                    send_telegram_message(msg, CHAT_ID, inline_keyboard)
                    posted_tokens.add(address)
                    print(f"✅ Posted {token['symbol']}")

                    # Sleep between each post to avoid spam
                    time.sleep(3)

        # Memory guard: keep recent 250 tokens
        if len(posted_tokens) > 500:
            posted_tokens = set(list(posted_tokens)[-250:])
    except Exception as e:
        print("❌ Main loop error:", e)

    # Sleep between full scans
    time.sleep(180)
