import requests
from solana.rpc.api import Client
import time
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    Update, InlineQueryResultArticle, InputTextMessageContent
)
from telegram.ext import (
    Updater, CommandHandler, InlineQueryHandler, CallbackContext
)
import logging
import uuid

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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def get_token_metadata(mint):
    url = f"https://mainnet.helius-rpc.com/v0/tokens/metadata?api-key={API_KEY}"
    try:
        resp = requests.post(url, json={"mintAccounts": [mint]}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0]
        logger.warning(f"No metadata found for mint {mint}")
        return None
    except Exception as e:
        logger.error(f"Error fetching metadata for {mint}: {e}")
        return None

def get_largest_accounts(mint):
    try:
        resp = client.get_token_largest_accounts(mint)
        if resp.get("result"):
            return resp["result"]["value"]
        return []
    except Exception as e:
        logger.error(f"Error fetching largest accounts for {mint}: {e}")
        return []

def get_supply(mint):
    try:
        resp = client.get_token_supply(mint)
        if resp.get("result"):
            return resp["result"]["value"]
        return {}
    except Exception as e:
        logger.error(f"Error fetching supply for {mint}: {e}")
        return {}

def format_token_message(mint):
    meta = get_token_metadata(mint)
    if not meta:
        return f"⚠️ No metadata found for token `{mint}`"

    supply = get_supply(mint)
    holders = get_largest_accounts(mint)

    decimals = int(supply.get("decimals", 0))
    amount_raw = int(supply.get("amount", 0)) if supply.get("amount") else 0
    total_supply = amount_raw / (10 ** decimals) if decimals else 0

    holders_str = ""
    for h in holders[:5]:
        amt_raw = int(h.get("amount", 0))
        amt = amt_raw / (10 ** decimals) if decimals else 0
        holders_str += f"- `{h.get('address', '')[:8]}...`: {amt:.2f}\n"

    offchain = meta.get('offChainData') or {}

    msg = (
        f"🆕 *New Solana Token Detected!*\n\n"
        f"📛 *Name:* {meta.get('name', 'N/A')}\n"
        f"💠 *Symbol:* {meta.get('symbol', 'N/A')}\n"
        f"🔗 [Solana Explorer](https://explorer.solana.com/address/{mint})\n\n"
        f"📦 *Total Supply:* {total_supply:,.2f}\n"
        f"🔢 *Decimals:* {decimals}\n\n"
        f"🏦 *Top Holders:*\n{holders_str}\n"
        f"🌐 *Website:* {offchain.get('external_url', 'N/A')}\n"
        f"📝 *Description:* {offchain.get('description', 'N/A')}\n"
        f"🖼 *Image:* {offchain.get('image', 'N/A')}"
    )
    return msg

def get_recent_solana_tokens():
    url = "https://quote-api.jup.ag/v1/tokens"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            tokens = []
            for token in data.get('tokens', []):
                if token.get('chainId') == 101:  # 101 = Solana Mainnet
                    tokens.append(token['address'])
            return tokens
        else:
            logger.warning(f"Jupiter API error: {resp.status_code}")
            return []
    except Exception as e:
        logger.error(f"Exception in fetching tokens from Jupiter: {e}")
        return []

def start(update: Update, context: CallbackContext):
    """Send a welcome message with referral info on /start"""
    user = update.effective_user
    msg = (
        f"👋 Hi {user.first_name if user else 'there'}!\n\n"
        "Welcome to the Solana Token Bot.\n"
        "I will keep you updated about new Solana tokens detected on-chain.\n\n"
        "Use the 🔗 Refer Friends button below to invite friends and grow the community!\n\n"
        "Join our group for updates and discussion:"
    )
    update.message.reply_text(msg, reply_markup=inline_keyboard)

def inlinequery(update: Update, context: CallbackContext):
    """Handle inline queries for referral button"""
    query = update.inline_query.query.lower()

    results = []
    if query.startswith("invite"):
        # Provide a referral invite message
        invite_text = (
            "Join this awesome Solana token tracker bot! Stay updated with new tokens and get exclusive info. "
            "Use this link to start: https://t.me/YourBotUsername"
        )
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="Invite your friends!",
                input_message_content=InputTextMessageContent(invite_text),
                description="Send an invite message to your friends."
            )
        )
    update.inline_query.answer(results, cache_time=60, is_personal=True)

def run_bot():
    print("Bot started. Scanning for new tokens...")

    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(InlineQueryHandler(inlinequery))

    # Start polling in background (so bot can receive inline queries and commands)
    updater.start_polling()

    bot = updater.bot

    while True:
        tokens = get_recent_solana_tokens()
        if not tokens:
            logger.info("No tokens fetched, retrying after 10 minutes.")
            time.sleep(600)
            continue

        new_tokens = [t for t in tokens if t not in posted_tokens]
        logger.info(f"Found {len(new_tokens)} new tokens to check...")

        for mint in new_tokens:
            logger.info(f"Processing token: {mint}")
            msg = format_token_message(mint)
            try:
                bot.send_message(
                    chat_id=CHAT_ID,
                    text=msg,
                    parse_mode="Markdown",
                    disable_web_page_preview=False,
                    reply_markup=inline_keyboard
                )
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
            posted_tokens.add(mint)
            time.sleep(2)  # To avoid Telegram flood control

        logger.info("Sleeping for 10 minutes before next scan...")
        time.sleep(600)


if __name__ == "__main__":
    run_bot()
