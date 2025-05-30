import requests
import time
import json
import os 

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DONATION_WALLET = os.getenv("DONATION_WALLET")
                            
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
    requests.post(url, data=payload)

def fetch_tokens():
    url = "https://cache.jup.ag/tokens"
    res = requests.get(url)
    tokens = res.json()
    meme_keywords = ['dog', 'pepe', 'cat', 'elon', 'moon', 'baby', 'inu']
    return [t for t in tokens if any(k in t['name'].lower() for k in meme_keywords)]

def fetch_token_data(address):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{address}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json().get("pair", {})
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
    holders = info.get("holders", "?")  # Optional: add from Helius later

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

posted_tokens = set()

# Inline keyboard with Refer Friends and Join Group buttons
inline_keyboard = {
    "inline_keyboard": [
        [
            {
                "text": "🔗 Refer Friends",
                "switch_inline_query": "invite "
            }
        ],
        [
            {
                "text": "📢 Join Our Group",
                "url": "https://t.me/digistoryan"
            }
        ]
    ]
}

# Send welcome message with inline buttons once when script starts
welcome_text = (
    "👋 Welcome to @coinupdater_bot!\n\n"
    "Get the latest new meme tokens on Solana.\n"
    "Use the buttons below to refer friends or join our group."
)
send_telegram_message(welcome_text, CHAT_ID, inline_keyboard)

while True:
    print("🔍 Scanning for new meme tokens...")
    try:
        tokens = fetch_tokens()
        for token in tokens[:5]:  # Limit checks per scan
            address = token['address']
            if address not in posted_tokens:
                info = fetch_token_data(address)
                if info:
                    msg = format_token_msg(token, info)
                    send_telegram_message(msg, CHAT_ID, inline_keyboard)
                    posted_tokens.add(address)
                    time.sleep(3)
    except Exception as e:
        print("❌ Error:", e)

    time.sleep(180)  # Wait 3 minutes
