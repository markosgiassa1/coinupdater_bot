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
      font-size: 1rem;
    }
    button {
      background: linear-gradient(to right, #00ff90, #00d178);
      color: black;
      font-weight: bold;
      cursor: pointer;
      transition: background 0.3s ease;
    }
    button:hover {
      background: linear-gradient(to right, #00d178, #00ff90);
    }
    #status {
      background: #222;
      padding: 10px;
      border-radius: 5px;
      white-space: pre-wrap;
      min-height: 80px;
      font-family: monospace;
      overflow-y: auto;
      max-height: 250px;
    }
    h1 {
      text-align: center;
      margin-bottom: 20px;
      user-select: none;
    }
  </style>
</head>
<body>
  <h1>🔗 SPL Token Distributor</h1>

  <button id="connectBtn">🔗 Connect Wallet</button>
  <p id="walletStatus">Wallet not connected.</p>

  <label for="recipients">Recipient Wallets (one per line):</label>
  <textarea id="recipients" rows="6" placeholder="Enter recipient addresses here..."></textarea>

  <label for="mintAddress">Token Mint Address:</label>
  <input type="text" id="mintAddress" placeholder="Enter mint address">

  <label for="decimals">Token Decimals:</label>
  <input type="number" id="decimals" placeholder="Decimals (e.g., 9)">

  <label for="amount">Amount to Send to EACH Address:</label>
  <input type="number" id="amount" step="any" placeholder="E.g. 1000">

  <label for="network">Network:</label>
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
    "devnet": "https://api.devnet.solana.com"
  };

  connectBtn.onclick = async () => {
    console.log("Connect button clicked");
    if (window.solana?.isPhantom) {
      provider = window.solana;
      console.log("Phantom wallet detected");
    } else if (window.solflare?.isSolflare) {
      provider = window.solflare;
      console.log("Solflare wallet detected");
    } else {
      walletStatus.innerText = "⚠️ No supported wallet found. Please install Phantom or Solflare.";
      console.warn("No wallet detected");
      return;
    }

    try {
      const resp = await provider.connect();
      userPublicKey = resp.publicKey ?? resp;
      walletStatus.innerText = "✅ Connected: " + userPublicKey.toBase58();
      console.log("Wallet connected:", userPublicKey.toBase58());
    } catch (err) {
      walletStatus.innerText = "❌ Wallet connection failed: " + err.message;
      console.error(err);
    }
  };

  sendBtn.onclick = async () => {
    if (!provider || !userPublicKey) {
      alert("Connect your wallet first!");
      return;
    }

    const recipientsRaw = document.getElementById("recipients").value.trim();
    if (!recipientsRaw) {
      alert("Please enter at least one recipient address.");
      return;
    }
    const recipients = recipientsRaw.split("\n").map(r => r.trim()).filter(r => r.length > 0);

    const mintAddress = document.getElementById("mintAddress").value.trim();
    const decimalsStr = document.getElementById("decimals").value.trim();
    const amountStr = document.getElementById("amount").value.trim();
    const network = document.getElementById("network").value;

    if (!mintAddress || !decimalsStr || !amountStr) {
      alert("Please fill all required fields: mint address, decimals, amount.");
      return;
    }

    const decimals = parseInt(decimalsStr);
    const amount = parseFloat(amountStr);

    if (isNaN(decimals) || isNaN(amount) || amount <= 0) {
      alert("Decimals must be a number and amount must be a positive number.");
      return;
    }

    statusBox.innerText = "Connecting to network...\n";
    const connection = new solanaWeb3.Connection(heliusRPC[network], "confirmed");
    const mint = new solanaWeb3.PublicKey(mintAddress);

    try {
      // Get sender's associated token account for the mint
      const fromTokenAccount = await splToken.getAssociatedTokenAddress(mint, userPublicKey);
      statusBox.innerText += `Using token account: ${fromTokenAccount.toBase58()}\n\n`;

      for (const recipient of recipients) {
        try {
          statusBox.innerText += `Sending to ${recipient} ...\n`;
          const toPubKey = new solanaWeb3.PublicKey(recipient);

          // Get or create recipient associated token account
          const toTokenAccount = await splToken.getOrCreateAssociatedTokenAccount(
            connection,
            userPublicKey, // payer
            mint,
            toPubKey
          );

          const amountRaw = BigInt(Math.floor(amount * (10 ** decimals)));

          // Build transfer instruction
          const transferIx = splToken.createTransferInstruction(
            fromTokenAccount,
            toTokenAccount.address,
            userPublicKey,
            amountRaw,
            [],
            splToken.TOKEN_PROGRAM_ID
          );

          const tx = new solanaWeb3.Transaction().add(transferIx);
          tx.feePayer = userPublicKey;

          const { blockhash } = await connection.getLatestBlockhash();
          tx.recentBlockhash = blockhash;

          // Sign transaction
          let signedTx;
          if (provider.isPhantom || provider.isSolflare) {
            signedTx = await provider.signTransaction(tx);
          } else {
            throw new Error("Unsupported wallet provider");
          }

          // Send transaction
          const signature = await connection.sendRawTransaction(signedTx.serialize());
          await connection.confirmTransaction(signature, "confirmed");

          statusBox.innerText += `✅ Sent to ${recipient} (tx: ${signature})\n\n`;
        } catch (err) {
          statusBox.innerText += `❌ Error sending to ${recipient}: ${err.message}\n\n`;
          console.error(`Error for recipient ${recipient}`, err);
        }
      }
      statusBox.innerText += "🎉 All transfers attempted.";
    } catch (err) {
      statusBox.innerText += `❌ Fatal error: ${err.message}`;
      console.error(err);
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
