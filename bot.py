import requests
from solana.rpc.api import Client
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater

# === CONFIG ===
API_KEY = "9867d904-fdcc-46b7-b5b1-c9ae880bd41d"
RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={API_KEY}"
BOT_TOKEN = "7639604753:AAH6_rlQAFgoPr2jlShOA5SKgLT57Br_BxU"
CHAT_ID = "7639604753"

client = Client(RPC_URL)
posted_tokens = set()

# Create inline keyboard with referral and group join buttons
inline_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔗 Refer Friends", switch_inline_query="invite ")],
    [InlineKeyboardButton("📢 Join Our Group", url="https://t.me/digistoryan")]
])

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
        # We cannot send InlineKeyboardMarkup via Telegram API raw POST easily,
        # so we use telegram python library Updater to send messages with keyboards.
        # But to keep it consistent, we will switch to Updater for sending messages.
    }
    # Since requests.post can't handle reply_markup easily, we'll send messages with python-telegram-bot library instead.
    # This function will be redefined below to use Updater's bot.send_message.

def get_token_metadata(mint):
    url = f"https://mainnet.helius.xyz/v0/tokens/metadata?api-key={API_KEY}"
    resp = requests.post(url, json={"mintAccounts": [mint]})
    if resp.status_code == 200 and resp.json():
        return resp.json()[0]
    return None

def get_largest_accounts(mint):
    resp = client.get_token_largest_accounts(mint)
    if resp.get("result"):
        return resp["result"]["value"]
    return []

def get_supply(mint):
    resp = client.get_token_supply(mint)
    if resp.get("result"):
        return resp["result"]["value"]
    return {}

def format_token_message(mint):
    meta = get_token_metadata(mint)
    if not meta:
        return f"⚠️ No metadata found for token `{mint}`"

    supply = get_supply(mint)
    holders = get_largest_accounts(mint)

    decimals = int(supply.get("decimals", 0))
    total_supply = int(supply.get("amount", 0)) / (10 ** decimals) if decimals else 0

    holders_str = ""
    for h in holders[:5]:
        amt = int(h["amount"]) / (10 ** decimals) if decimals else 0
        holders_str += f"- `{h['address'][:8]}...`: {amt:.2f}\n"

    msg = (
        f"🆕 *New Solana Token Detected!*\n\n"
        f"📛 *Name:* {meta.get('name')}\n"
        f"💠 *Symbol:* {meta.get('symbol')}\n"
        f"🔗 [Solana Explorer](https://explorer.solana.com/address/{mint})\n\n"
        f"📦 *Total Supply:* {total_supply:,.2f}\n"
        f"🔢 *Decimals:* {decimals}\n\n"
        f"🏦 *Top Holders:*\n{holders_str}\n"
        f"🌐 *Website:* {meta.get('offChainData', {}).get('external_url', 'N/A')}\n"
        f"📝 *Description:* {meta.get('offChainData', {}).get('description', 'N/A')}\n"
        f"🖼 *Image:* {meta.get('offChainData', {}).get('image', 'N/A')}"
    )
    return msg

def get_recent_solana_tokens():
    url = "https://api.dexscreener.com/latest/dex/tokens/solana"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            tokens = []
            for pair in data.get('pairs', []):
                token = pair.get('token')
                if token and token.get('address'):
                    tokens.append(token['address'])
            return list(set(tokens))
        else:
            print(f"DexScreener API error: {resp.status_code}")
            return []
    except Exception as e:
        print(f"Exception in fetching tokens: {e}")
        return []

def run_bot():
    print("Bot started. Scanning for new tokens...")
    
    # Setup telegram Updater for sending messages with inline keyboard
    updater = Updater(BOT_TOKEN)
    bot = updater.bot
    
    while True:
        tokens = get_recent_solana_tokens()
        if not tokens:
            print("No tokens fetched, retrying after 10 minutes.")
            time.sleep(600)
            continue

        new_tokens = [t for t in tokens if t not in posted_tokens]
        print(f"Found {len(new_tokens)} new tokens to check...")

        for mint in new_tokens:
            print(f"Processing token: {mint}")
            msg = format_token_message(mint)
            try:
                bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown", disable_web_page_preview=False, reply_markup=inline_keyboard)
            except Exception as e:
                print(f"Failed to send message: {e}")
            posted_tokens.add(mint)
            time.sleep(2)  # To avoid Telegram flood control

        print("Sleeping for 10 minutes before next scan...")
        time.sleep(600)

if __name__ == "__main__":
    run_bot()
