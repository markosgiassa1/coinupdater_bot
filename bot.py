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
POSTED_TOKENS_FILE = "posted_tokens.txt"

def load_posted_tokens():
    if not os.path.exists(POSTED_TOKENS_FILE):
        return set()
    with open(POSTED_TOKENS_FILE, "r") as f:
        tokens = f.read().splitlines()
    return set(tokens)

def save_posted_tokens(tokens):
    with open(POSTED_TOKENS_FILE, "w") as f:
        f.write("\n".join(tokens))

def send_telegram_message(text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    resp = requests.post(url, json=payload)
    if resp.status_code != 200:
        print(f"⚠️ Telegram send failed: {resp.text}")
    else:
        print("✅ Message sent")

def fetch_tradable_tokens():
    url = "https://price.jup.ag/v4/tradableTokens"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"❌ Error fetching tokens: {e}")
        return []

def fetch_token_data(address):
    url = f"https://price.jup.ag/v4/token/{address}"
    try:
        response = requests.get(url)
        return response.json().get("data", {})
    except Exception as e:
        print(f"❌ Error fetching token data: {e}")
        return {}

def format_token_message(token, info):
    name = token.get("name", "Unknown")
    symbol = token.get("symbol", "N/A")
    address = token.get("address", "N/A")

    price_native = info.get("priceNative")
    price_usd = info.get("priceUsd")
    fdv = info.get("fdv")
    volume_24h = info.get("volume", {}).get("h24")
    liquidity = info.get("liquidity", {}).get("base")
    holders = info.get("holders")

    # Format numbers nicely
    def fmt(x):
        if x is None:
            return "N/A"
        if isinstance(x, float):
            return f"{x:,.4f}"
        return str(x)

    msg = (
        f"*{name}* ({symbol})\n"
        f"Address: `{address}`\n\n"
        f"Price: {fmt(price_native)} SOL | ${fmt(price_usd)}\n"
        f"FDV: ${fmt(fdv)}\n"
        f"24h Volume: ${fmt(volume_24h)}\n"
        f"Liquidity: {fmt(liquidity)} SOL\n"
        f"Holders: {fmt(holders)}\n\n"
        f"[View on Solana Explorer](https://explorer.solana.com/address/{address})"
    )
    return msg

def main_loop():
    print("🚀 Meme Token Updater Bot started!")

    posted_tokens = load_posted_tokens()

    # Welcome message with buttons
    welcome_text = (
        "👋 Welcome to *Meme Token Updater Bot*!\n\n"
        "Get the latest new tokens on Solana as they pop up.\n"
        "Use the buttons below to refer friends or join our group."
    )
    buttons = {
        "inline_keyboard": [
            [{"text": "🔗 Refer Friends", "switch_inline_query": "invite "}],
            [{"text": "📢 Join Our Group", "url": "https://t.me/digistoryan"}],
        ]
    }
    send_telegram_message(welcome_text, reply_markup=buttons)

    while True:
        tokens = fetch_tradable_tokens()
        print(f"🔍 Fetched {len(tokens)} tokens")

        new_tokens = [t for t in tokens if t.get("address") not in posted_tokens]

        if not new_tokens:
            print("ℹ️ No new tokens found.")
        else:
            print(f"✨ Found {len(new_tokens)} new tokens!")

        for token in new_tokens:
            address = token.get("address")
            token_info = fetch_token_data(address)
            message = format_token_message(token, token_info)
            send_telegram_message(message)
            posted_tokens.add(address)
            save_posted_tokens(posted_tokens)
            time.sleep(3)  # Telegram rate limit safety

        print("⏳ Waiting 3 minutes before checking again...\n")
        time.sleep(180)

if __name__ == "__main__":
    main_loop()
