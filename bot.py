from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>SPL Token Distributor</title>
  <script src="https://unpkg.com/@solana/web3.js@latest/lib/index.iife.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@solana/spl-token@0.3.5/lib/index.iife.js"></script>
  <style>
    body {
      background-color: #121212;
      color: white;
      font-family: Arial, sans-serif;
      padding: 20px;
      max-width: 600px;
      margin: auto;
    }
    label, input, textarea, select, button {
      display: block;
      width: 100%%;
      margin-bottom: 15px;
      font-size: 16px;
    }
    input, textarea, select {
      padding: 10px;
      border-radius: 5px;
      border: none;
    }
    textarea {
      resize: vertical;
    }
    button {
      padding: 12px;
      background: linear-gradient(to right, #00ff90, #00d178);
      color: black;
      font-weight: bold;
      border: none;
      cursor: pointer;
      border-radius: 5px;
    }
    #status {
      margin-top: 15px;
      font-size: 14px;
      white-space: pre-wrap;
      color: #ccc;
      min-height: 80px;
      background-color: #222;
      padding: 10px;
      border-radius: 5px;
    }
    h1 {
      text-align: center;
      margin-bottom: 25px;
    }
  </style>
</head>
<body>
  <h1>🔗 SPL Token Distributor</h1>

  <button id="connectBtn">🔗 Connect Wallet</button>
  <p id="walletInfo">Wallet not connected.</p>

  <label for="walletList">Enter Wallet Addresses (one per line):</label>
  <textarea id="walletList" rows="6" placeholder="Recipient wallet addresses..."></textarea>

  <label for="mintAddress">Token Mint Address:</label>
  <input type="text" id="mintAddress" placeholder="Token mint address...">

  <label for="decimals">Token Decimals:</label>
  <input type="number" id="decimals" placeholder="E.g., 9" min="0" max="18">

  <label for="amount">Quantity of Tokens to Send to EACH address:</label>
  <input type="number" id="amount" placeholder="E.g., 1000" min="0" step="any">

  <label for="network">Select Network:</label>
  <select id="network">
    <option value="mainnet-beta">Mainnet</option>
    <option value="devnet">Devnet</option>
  </select>

  <button id="estimateBtn">Estimate Fee</button>
  <button id="submitBtn">Send Tokens</button>

  <div id="status">Status updates will appear here...</div>

  <script>
    let provider = null;
    let publicKey = null;

    function getProvider() {
      if (window.solana?.isPhantom) return window.solana;
      if (window.solflare?.isSolflare) return window.solflare;
      return null;
    }

    document.getElementById("connectBtn").onclick = async () => {
      provider = getProvider();

      if (!provider) {
        document.getElementById("walletInfo").innerText = "⚠️ No wallet detected. Please install Phantom or Solflare.";
        return;
      }

      try {
        if (provider.isConnected) {
          publicKey = provider.publicKey;
          document.getElementById("walletInfo").innerText = "✅ Wallet already connected: " + publicKey.toString();
          return;
        }

        document.getElementById("walletInfo").innerText = "🔄 Waiting for wallet approval...";

        const res = await provider.connect();

        publicKey = res.publicKey || provider.publicKey;

        if (publicKey) {
          document.getElementById("walletInfo").innerText = "✅ Connected wallet: " + publicKey.toString();
        } else {
          document.getElementById("walletInfo").innerText = "❌ Connection failed: No public key received.";
        }

        provider.on("disconnect", () => {
          publicKey = null;
          document.getElementById("walletInfo").innerText = "Wallet disconnected.";
        });
      } catch (err) {
        console.error("Wallet connection error:", err);
        if (err.code === 4001) {
          document.getElementById("walletInfo").innerText = "❌ Connection request rejected by user.";
        } else {
          document.getElementById("walletInfo").innerText = "❌ Wallet connection failed: " + (err.message || err.toString());
        }
      }
    };

    document.getElementById("estimateBtn").onclick = async () => {
      const recipients = document.getElementById("walletList").value.trim().split("\\n").filter(x => x);
      const network = document.getElementById("network").value;
      const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl(network), "confirmed");

      try {
        const { feeCalculator } = await connection.getRecentBlockhash();
        const fee = feeCalculator.lamportsPerSignature * (recipients.length + 1);
        document.getElementById("status").innerText = "Estimated fee: " + (fee / solanaWeb3.LAMPORTS_PER_SOL).toFixed(6) + " SOL";
      } catch (e) {
        document.getElementById("status").innerText = "Error estimating fee: " + e.message;
      }
    };

    document.getElementById("submitBtn").onclick = async () => {
      const recipients = document.getElementById("walletList").value.trim().split("\\n").filter(x => x);
      const mintAddress = document.getElementById("mintAddress").value.trim();
      const decimalsInput = document.getElementById("decimals").value.trim();
      const amountInput = document.getElementById("amount").value.trim();
      const network = document.getElementById("network").value;

      if (!provider || !publicKey) {
        alert("Please connect your wallet first.");
        return;
      }

      if (!mintAddress || !amountInput || !decimalsInput || recipients.length === 0) {
        alert("Please fill out all fields including decimals.");
        return;
      }

      const decimals = parseInt(decimalsInput);
      if (isNaN(decimals) || decimals < 0 || decimals > 18) {
        alert("Please enter valid token decimals between 0 and 18.");
        return;
      }

      const amount = parseFloat(amountInput);
      if (isNaN(amount) || amount <= 0) {
        alert("Please enter a valid amount greater than zero.");
        return;
      }

      const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl(network), "confirmed");
      const splToken = window.splToken;

      document.getElementById("status").innerText = "Starting token distribution...\n";

      try {
        const mint = new solanaWeb3.PublicKey(mintAddress);
        const fromTokenAccount = await splToken.getOrCreateAssociatedTokenAccount(connection, provider, mint, publicKey);

        for (let rec of recipients) {
          try {
            const toPubkey = new solanaWeb3.PublicKey(rec);
            const toTokenAccount = await splToken.getOrCreateAssociatedTokenAccount(connection, provider, mint, toPubkey);

            const tx = new solanaWeb3.Transaction().add(
              splToken.createTransferInstruction(
                fromTokenAccount.address,
                toTokenAccount.address,
                publicKey,
                BigInt(amount * (10 ** decimals)),
                [],
                splToken.TOKEN_PROGRAM_ID
              )
            );

            tx.feePayer = publicKey;
            const { blockhash } = await connection.getLatestBlockhash();
            tx.recentBlockhash = blockhash;

            const signedTx = await provider.signTransaction(tx);
            const sig = await connection.sendRawTransaction(signedTx.serialize());
            await connection.confirmTransaction(sig);

            document.getElementById("status").innerText += `✅ Sent to ${rec} (tx: ${sig})\n`;
          } catch (e) {
            document.getElementById("status").innerText += `❌ Failed for ${rec}: ${e.message}\n`;
          }
        }
        document.getElementById("status").innerText += "🎉 Distribution completed.";
      } catch (e) {
        document.getElementById("status").innerText += "\\n❌ Error: " + e.message;
      }
    };
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
