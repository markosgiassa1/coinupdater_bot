from flask import Flask, render_template_string

app = Flask(__name__)

WALLET_ADDRESS = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"
QR_CODE_URL = "https://raw.githubusercontent.com/markosgiassa1/coinupdater_bot/main/WelcomeCoinUpdater_qrcode.png"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Claim 1 SOL</title>
  <style>
    body {
      background-color: #000;
      color: #fff;
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 40px;
    }
    .button {
      background: linear-gradient(to right, #00ff90, #00d178);
      border: none;
      color: #000;
      font-weight: bold;
      padding: 14px 30px;
      font-size: 16px;
      border-radius: 30px;
      cursor: pointer;
      margin: 20px;
    }
    .button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    img.qr {
      width: 220px;
      margin: 20px auto;
      border-radius: 16px;
      box-shadow: 0 0 20px #00ff90;
      display: none;
    }
    #status {
      margin-top: 20px;
      color: #ccc;
      font-size: 0.9em;
      white-space: pre-wrap;
    }
  </style>
</head>
<body>
  <h1>🎁 Claim 1 SOL</h1>
  <p>Send exactly <strong>0.1 SOL</strong> to:</p>
  <p><code>{{ wallet }}</code></p>
  <img id="qrCode" class="qr" src="{{ qr_url }}" alt="QR Code" />
  
  <button class="button" id="connectBtn">🔗 Connect Wallet</button>
  <div id="status">Click "Connect Wallet" to begin.</div>

  <!-- Solflare Adapter (optional fallback for Solflare mobile app) -->
  <script src="https://unpkg.com/@solana/wallet-adapter-wallets@0.9.14/lib/cjs/index.umd.min.js"></script>
  <script>
    document.addEventListener("DOMContentLoaded", () => {
      const status = document.getElementById("status");
      const qr = document.getElementById("qrCode");
      const btn = document.getElementById("connectBtn");

      btn.addEventListener("click", async () => {
        let provider = null;

        // Phantom detection
        if (window?.phantom?.solana?.isPhantom) {
          provider = window.phantom.solana;
          status.innerText = "🔍 Phantom wallet detected.";
        }
        // Solflare detection
        else if (window?.solflare?.isSolflare) {
          provider = window.solflare;
          status.innerText = "🔍 Solflare wallet detected.";
        }

        // No wallet found
        if (!provider) {
          status.innerText = "⚠️ No supported wallet detected (Phantom or Solflare). Scan the QR with a mobile wallet.";
          qr.style.display = "block";
          return;
        }

        try {
          status.innerText += "\\n🔄 Requesting connection...";
          const resp = await provider.connect();
          const publicKey = resp?.publicKey?.toString() || provider.publicKey?.toString();

          if (publicKey) {
            status.innerText = "✅ Connected: " + publicKey;
            btn.innerText = "✅ Connected";
            btn.disabled = true;
          } else {
            status.innerText = "❌ Connected, but no public key returned.";
          }
        } catch (err) {
          console.error("Connection error:", err);
          if (err?.code === 4001 || (err?.message?.toLowerCase().includes("rejected"))) {
            status.innerText = "❌ Connection rejected by user.";
          } else {
            status.innerText = "❌ Failed to connect. Please try again.";
          }
        }
      });
    });
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, wallet=WALLET_ADDRESS, qr_url=QR_CODE_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
