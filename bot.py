# app.py
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>SPL Token Distributor</title>
  <script src="https://unpkg.com/@solana/web3.js@1.73.3/lib/index.iife.js"></script>
  <script src="https://unpkg.com/@solana/spl-token@0.4.0/lib/index.iife.js"></script>
  <style>
    body {
      background: #121212;
      color: white;
      font-family: Arial, sans-serif;
      padding: 20px;
      max-width: 600px;
      margin: auto;
    }
    input, textarea, select, button {
      width: 100%;
      margin-bottom: 15px;
      padding: 10px;
      border-radius: 5px;
      background-color: #222;
      color: white;
      border: none;
    }
    button {
      background: linear-gradient(to right, #00ff90, #00d178);
      color: black;
      font-weight: bold;
      cursor: pointer;
    }
    #status {
      background: #222;
      padding: 10px;
      border-radius: 5px;
      white-space: pre-wrap;
      min-height: 80px;
    }
    h1 {
      text-align: center;
      margin-bottom: 20px;
    }
  </style>
</head>
<body>
  <h1>🔗 SPL Token Distributor</h1>

  <button id="connectBtn">🔗 Connect Wallet</button>
  <p id="walletStatus">Wallet not connected.</p>

  <label>Recipient Wallets (one per line):</label>
  <textarea id="recipients" rows="6"></textarea>

  <label>Token Mint Address:</label>
  <input type="text" id="mintAddress" placeholder="Mint address">

  <label>Token Decimals:</label>
  <input type="number" id="decimals" placeholder="Decimals (e.g., 9)">

  <label>Amount to Send to EACH Address:</label>
  <input type="number" id="amount" step="any" placeholder="E.g. 1000">

  <label>Network:</label>
  <select id="network">
    <option value="mainnet-beta">Mainnet</option>
    <option value="devnet" selected>Devnet</option>
  </select>

  <button id="sendBtn">🚀 Send Tokens</button>
  <div id="status">Status will appear here.</div>

<script>
  const connectBtn = document.getElementById("connectBtn");
  const sendBtn = document.getElementById("sendBtn");
  const walletStatus = document.getElementById("walletStatus");
  const statusBox = document.getElementById("status");

  let provider = null;
  let userPublicKey = null;

  // Helius RPC URLs for networks
  const heliusApiKey = "9867d904-fdcc-46b7-b5b1-c9ae880bd41d";
  const heliusRPC = {
    "mainnet-beta": `https://mainnet.helius-rpc.com/?api-key=${heliusApiKey}`,
    "devnet": `"devnet": "https://api.devnet.solana.com"`
  };

  connectBtn.onclick = async () => {
    // Detect Phantom or Solflare wallet provider
    if (window.solana?.isPhantom) {
      provider = window.solana;
    } else if (window.solflare?.isSolflare) {
      provider = window.solflare;
    } else {
      walletStatus.innerText = "⚠️ No supported wallet found. Please install Phantom or Solflare.";
      return;
    }

    try {
      const resp = await provider.connect();
      userPublicKey = resp.publicKey || resp; // Solflare returns PublicKey directly sometimes
      walletStatus.innerText = "✅ Connected: " + userPublicKey.toBase58();
    } catch (err) {
      walletStatus.innerText = "❌ Wallet connection failed.";
      console.error(err);
    }
  };

  sendBtn.onclick = async () => {
    if (!provider || !userPublicKey) {
      alert("Connect your wallet first!");
      return;
    }

    const recipients = document.getElementById("recipients").value.trim().split("\\n").filter(x => x);
    const mintAddress = document.getElementById("mintAddress").value.trim();
    const decimals = parseInt(document.getElementById("decimals").value);
    const amount = parseFloat(document.getElementById("amount").value);
    const network = document.getElementById("network").value;

    if (!mintAddress || isNaN(decimals) || isNaN(amount) || recipients.length === 0) {
      alert("Please fill in all fields correctly.");
      return;
    }

    const connection = new solanaWeb3.Connection(heliusRPC[network], "confirmed");
    const mint = new solanaWeb3.PublicKey(mintAddress);

    statusBox.innerText = "Starting token transfers...\n";

    try {
      const fromTokenAccount = await splToken.getAssociatedTokenAddress(
        mint,
        userPublicKey
      );

      for (const recipient of recipients) {
        try {
          const toPubKey = new solanaWeb3.PublicKey(recipient);
          const toTokenAccount = await splToken.getOrCreateAssociatedTokenAccount(
            connection,
            userPublicKey, // payer
            mint,
            toPubKey
          );

          const tx = new solanaWeb3.Transaction().add(
            splToken.createTransferInstruction(
              fromTokenAccount,
              toTokenAccount.address,
              userPublicKey,
              BigInt(amount * (10 ** decimals)),
              [],
              splToken.TOKEN_PROGRAM_ID
            )
          );

          tx.feePayer = userPublicKey;
          const { blockhash } = await connection.getLatestBlockhash();
          tx.recentBlockhash = blockhash;

          // Solflare may require signAllTransactions; Phantom uses signTransaction
          let signedTx;
          if (provider.isPhantom) {
            signedTx = await provider.signTransaction(tx);
          } else if (provider.isSolflare) {
            signedTx = await provider.signTransaction(tx);
          } else {
            throw new Error("Unsupported wallet provider");
          }

          const sig = await connection.sendRawTransaction(signedTx.serialize());
          await connection.confirmTransaction(sig, "confirmed");

          statusBox.innerText += `✅ Sent to ${recipient} (tx: ${sig})\\n`;
        } catch (err) {
          statusBox.innerText += `❌ Error for ${recipient}: ${err.message}\\n`;
        }
      }

      statusBox.innerText += "🎉 All transfers attempted.";
    } catch (err) {
      statusBox.innerText += `\\n❌ Global error: ${err.message}`;
    }
  };
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
