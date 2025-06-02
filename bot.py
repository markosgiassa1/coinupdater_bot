import requests
import json
import time
import threading
from flask import Flask
from collections import deque

app = Flask(__name__)

BOT_TOKEN = "7639604753:AAH6_rlQAFgoPr2jlShOA5SKgLT57Br_BxU"
CHAT_ID = "7636990835"
DONATION_WALLET = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"

posted_tokens = deque(maxlen=250)

inline_keyboard = {
    "inline_keyboard": [
        [{"text": "🔗 Refer Friends", "switch_inline_query": "invite "}],
        [{"text": "💰 Donate", "url": f"https://t.me/donate?wallet={DONATION_WALLET}"}],
        [{"text": "📢 Join Our Group", "url": "https://t.me/digistoryan"}]
    ]
}

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
        resp = requests.post(url, data=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ Telegram send error: {e}", flush=True)

def scrape_tokens_from_jup():
    url = "https://api.jup.ag/api/v1/cooking-tokens"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        tokens = res.json()  # usually a list of tokens
        sol_tokens = []
        for t in tokens:
            if t.get("chainId") == 101:
                symbol = t.get("symbol", "").lower()
                if symbol in ["sol", "wsol", "usdc", "usdt"]:
                    continue
                sol_tokens.append(t)
        return sol_tokens
    except Exception as e:
        send_telegram_message(f"❌ Error fetching tokens from Jupiter Cooking API:\n{e}", CHAT_ID)
        return []

def format_token_msg(token):
    name = token.get('name', '?')
    symbol = token.get('symbol', '?')
    address = token.get('address', '?')
    decimals = token.get('decimals', '?')
    logo = token.get('logoURI', '')
    website = token.get('website', '')

    jupiter_link = f"https://jup.ag/swap/SOL-{address}"
    dex_link = f"https://dexscreener.com/solana/{address}"

    msg = (
        f"⏺ | 🪙 *{name}* / `${symbol}`\n"
        f"🆕 New Token Detected on *Solana* via Jupiter Scraper\n"
        f"🆔 `{address}`\n"
        f"🔢 Decimals: `{decimals}`\n"
        f"🌐 Website: {website if website else 'N/A'}\n"
        f"[🖼 Logo]({logo})\n\n"
        f"[📍 View on DexScreener]({dex_link})\n"
        f"[🟢 Swap on Jupiter]({jupiter_link})\n\n"
        f"💰 *Donate:* `{DONATION_WALLET}`"
    )
    return msg

def run_bot():
    send_telegram_message("🚀 Coin Updater Bot Started! (Using Jupiter Pro Scraper)", CHAT_ID, inline_keyboard)

    while True:
        tokens = scrape_tokens_from_jup()
        if not tokens:
            send_telegram_message("⚠️ No tokens found on Jupiter Pro Cooking page.", CHAT_ID, inline_keyboard)

        for token in tokens[:5]:  # Limit to 5 tokens per run
            address = token.get('address')
            if not address or address in posted_tokens:
                continue

            msg = format_token_msg(token)
            send_telegram_message(msg, CHAT_ID, inline_keyboard)
            posted_tokens.append(address)
            time.sleep(3)

        time.sleep(180)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
