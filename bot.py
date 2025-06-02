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
POSTED_FILE = "posted_tokens.json"


def load_posted_tokens():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_posted_tokens(posted_tokens):
    with open(POSTED_FILE, "w") as f:
        json.dump(list(posted_tokens), f)


def safe_str(x):
    if x is None:
        return "N/A"
    if isinstance(x, float):
        return f"{x:,.4f}"
    # Escape markdown special chars for Telegram
    x = str(x)
    for ch in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
        x = x.replace(ch, f"\\{ch}")
    return x


def fetch_new_tokens():
    url = "https://price.jup.ag/v4/allTokens"
    try:
        r = requests.get(url)
        data = r.json()
        tokens = data.get("tokens", [])
        print(f"Fetched {len(tokens)} tokens from Jupiter")
        return tokens
    except Exception as e:
        print(f"Error fetching new tokens: {e}")
        return []


def fetch_token_data(address):
    url = f"https://price.jup.ag/v4/token/{address}"
    try:
        r = requests.get(url)
        data = r.json()
        if "data" not in data or not data["data"]:
            print(f"⚠️ No detailed data for token {address}")
            return None
        return data["data"]
    except Exception as e:
        print(f"Error fetching token data for {address}: {e}")
        return None


def format_token_message(token, info):
    name = safe_str(token.get("name", "Unknown"))
    symbol = safe_str(token.get("symbol", "N/A"))
    address = safe_str(token.get("address", "N/A"))

    price_native = info.get("priceNative")
    price_usd = info.get("priceUsd")
    fdv = info.get("fdv")
    volume_24h = info.get("volume", {}).get("h24")
    liquidity = info.get("liquidity", {}).get("base")
    holders = info.get("holders")

    msg = (
        f"*{name}* ({symbol})\n"
        f"Address: `{address}`\n\n"
        f"Price: {safe_str(price_native)} SOL | ${safe_str(price_usd)}\n"
        f"FDV: ${safe_str(fdv)}\n"
        f"24h Volume: ${safe_str(volume_24h)}\n"
        f"Liquidity: {safe_str(liquidity)} SOL\n"
        f"Holders: {safe_str(holders)}\n\n"
        f"[View on Solana Explorer](https://explorer.solana.com/address/{address})"
    )
    return msg


def send_telegram_message(text, parse_mode="MarkdownV2"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(url, json=payload)
        result = resp.json()
        if not result.get("ok"):
            print(f"Telegram API error: {result}")
        else:
            print("Message sent successfully")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")


def main_loop():
    print("🚀 Meme Token Updater Bot started!")

    # Send a test message on startup
    send_telegram_message("*Test message* \\- Bot started successfully!")

    posted_tokens = load_posted_tokens()

    while True:
        tokens = fetch_new_tokens()

        # Filter new tokens not posted yet
        new_tokens = [t for t in tokens if t.get("address") not in posted_tokens]

        if not new_tokens:
            print("No new tokens found. Waiting 60 seconds...")
            time.sleep(60)
            continue

        print(f"Found {len(new_tokens)} new tokens.")

        for token in new_tokens:
            address = token.get("address")
            if not address:
                continue

            print(f"Fetching data for token: {token.get('symbol')} ({address})")
            token_info = fetch_token_data(address)
            if not token_info:
                print(f"Skipping token {address} due to missing info.")
                continue

            message = format_token_message(token, token_info)
            print(f"Sending message for token: {token.get('symbol')}")
            send_telegram_message(message)

            posted_tokens.add(address)
            save_posted_tokens(posted_tokens)

            # Avoid spamming Telegram API limits
            time.sleep(3)

        print("Cycle complete. Waiting 60 seconds before next check...")
        time.sleep(60)


if __name__ == "__main__":
    main_loop()
