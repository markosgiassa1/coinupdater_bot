import requests

BOT_TOKEN = "7639604753:AAH6_rlQAFgoPr2jlShOA5SKgLT57Br_BxU"
CHAT_ID = "7639604753"

msg = "✅ Test message from Python!"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": msg,
    "parse_mode": "Markdown",
    "disable_web_page_preview": True
}

response = requests.post(url, json=payload)  # << use `json=` not `data=`
print(response.status_code)
print(response.text)
