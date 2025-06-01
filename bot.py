import requests
import time
import json
import os
from collections import deque

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
DONATION_WALLET = os.getenv("DONATION_WALLET")

# Token cache with fixed memory size
posted_tokens = deque(maxlen=250)

# Inline keyboard
inline_keyboard = {
    "inline_keyboard": [
        [{"text": "\ud83d\udd17 Refer Friends", "switch_inline_query": "invite "}],
        [{"text": "\ud83d\udce2 Join Our Group", "url": "https://t.me/digistoryan"}]
    ]
}

# Send Telegram message
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
        print(f"\u274c Send error: {e}")

# Fetch meme tokens from Jupiter
def fetch_tokens():
    try:
        res = requests.get("https://cache.jup.ag/tokens", timeout=10)
        res.raise_for_status()
        tokens = res.json()[:100]
        meme_keywords = ['dog', 'pepe', 'cat', 'elon', 'moon', 'baby', 'inu']
        return [t for t in tokens if any(k in t['name'].lower() for k in meme_keywords)]
    except Exception as e:
        print(f"\u274c Token fetch error: {e}")
        return []

# Fetch token info from Dexscreener
def fetch_token_data(address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{address}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json().get("pair", {})
    except Exception as e:
        print(f"\u274c Dex error: {e}")
    return {}

# Format the token message
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
        f"\u23fa | \ud83d\udc36 *{name}* / `${symbol}`\n"
        f"\U0001f195 New Meme Token | \ud83d\udfe2 Launched recently\n"
        f"\ud83d\udcb8 `{price_sol:.4f} SOL` (${price_usd:.2f})\n"
        f"\ud83d\udcca Mkt Cap: `${mcap:,}` | \ud83d\udd01 Vol 24h: `{volume:,} SOL`\n"
        f"\ud83d\udca7 LP: `{liquidity:,} SOL` | \U0001fa99 Holders: `{holders}`\n\n"
        f"[\ud83d\udccd View on DexScreener](https://dexscreener.com/solana/{address})\n"
        f"[\ud83d\udfe2 Buy on Jupiter](https://jup.ag/swap/SOL-{address})\n"
        f"\ud83d\udcb0 *Donate:* `{DONATION_WALLET}`"
    )

# Send welcome message only once (file flag)
if not os.path.exists("welcome_sent.flag"):
    welcome_text = (
        "\ud83d\udc4b Welcome to @coinupdater_bot!\n\n"
        "Get the latest new meme tokens on Solana.\n"
        "Use the buttons below to refer friends or join our group."
    )
    send_telegram_message(welcome_text, CHAT_ID, inline_keyboard)
    with open("welcome_sent.flag", "w") as f:
        f.write("ok")

# Main loop
restart_counter = 0
while True:
    try:
        print("ð Scanning for new meme tokens...")
        tokens = fetch_tokens()
        for token in tokens[:3]:
            address = token['address']
            if address not in posted_tokens:
                info = fetch_token_data(address)
                if info:
                    msg = format_token_msg(token, info)
                    send_telegram_message(msg, CHAT_ID, inline_keyboard)
                    posted_tokens.append(address)
                    print(f"â Posted {token['symbol']}")
                    time.sleep(3)

        restart_counter += 1
        if restart_counter >= 100:
            print("â»ï¸ Restarting bot to reset memory usage.")
            break

        time.sleep(180)

    except Exception as e:
        print(f"â Main loop error: {e}")
        time.sleep(10)
