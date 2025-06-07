from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>SPL Token Sender</title>
  <script src="https://unpkg.com/@solana/web3.js@latest/lib/index.iife.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@solana/spl-token@0.3.5/lib/index.iife.js"></script>
  <style>
    body {
      background-color: #121212;
      color: white;
      font-family: Arial, sans-serif;
      padding: 20px;
    }
    input, textarea, select, button {
      margin: 10px 0;
      padding: 10px;
      width: 100%%;
      font-size: 16px;
      border-radius: 5px;
    }
    button {
      background: linear-gradient(to right, #00ff90, #00d178);
      color: black;
      font-weight: bold;
      border: none;
      cursor: pointer;
    }
    #status {
      margin-top: 15px;
      font-size: 14px;
      white-space: pre-wrap;
      color: #ccc;
    }
  </style>
</head>
<body>
  <h1>🔗 SPL Token Distributor</h1>

  <button id="connectBtn">Connect Wallet</button>
  <p id="walletInfo">Wallet not connected.</p>

  <label>Enter Wallet Addresses (one per line):</label>
  <textarea id="walletList" rows="6" placeholder="Recipient wallet addresses..."></textarea>

  <label>Token Mint Address:</label>
  <input type="text" id="mintAddress" placeholder="Token mint address...">

  <label>Decimals of the Token:</label>
  <input type="number" id="decimals" placeholder="E.g., 9" min="0" max="18" value="9">

  <label>Quantity of Tokens to Send to EACH address:</label>
  <input type="number" id="amount" placeholder="E.g., 1000" min="0" step="any">

  <label>Select Network:</label>
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

    document.getElementById("connectBtn").onclick = async () => {
      if (window.solana?.isPhantom) {
        provider = window.solana;
      } else {
        alert("Please install the Phantom wallet extension.");
        return;
      }

      try {
        const resp = await provider.connect();
        publicKey = resp.publicKey;
        document.getElementById("walletInfo").innerText = "Connected wallet: " + publicKey.toString();
      } catch (err) {
        document.getElementById("walletInfo").innerText = "Connection failed.";
      }
    };

    document.getElementById("estimateBtn").onclick = async () => {
      const recipients = document.getElementById("walletList").value.trim().split("\\n").filter(x => x);
      const network = document.getElementById("network").value;
      const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl(network), "confirmed");

      try {
        const { feeCalculator } = await connection.getRecentBlockhash();
        const fee = feeCalculator.lamportsPerSignature * (recipients.length + 1); // rough estimate
        document.getElementById("status").innerText = "Estimated fee: " + (fee / solanaWeb3.LAMPORTS_PER_SOL).toFixed(6) + " SOL";
      } catch (e) {
        document.getElementById("status").innerText = "Error estimating fee: " + e.message;
      }
    };

    document.getElementById("submitBtn").onclick = async () => {
      const recipients = document.getElementById("walletList").value.trim().split("\\n").filter(x => x);
      const mintAddress = document.getElementById("mintAddress").value.trim();
      const amountInput = document.getElementById("amount").value.trim();
      const decimalsInput = document.getElementById("decimals").value.trim();
      const network = document.getElementById("network").value;

      if (!provider || !publicKey) {
        alert("Please connect your wallet first.");
        return;
      }

      if (!mintAddress || !amountInput || recipients.length === 0 || decimalsInput === "") {
        alert("Please fill out all fields.");
        return;
      }

      const amount = parseFloat(amountInput);
      const decimals = parseInt(decimalsInput);

      if (isNaN(amount) || amount <= 0) {
        alert("Please enter a valid amount greater than 0.");
        return;
      }
      if (isNaN(decimals) || decimals < 0 || decimals > 18) {
        alert("Please enter valid decimals between 0 and 18.");
        return;
      }

      const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl(network), "confirmed");

      try {
        const mint = new solanaWeb3.PublicKey(mintAddress);
        // 'provider' acts as the signer and payer for ATA creation, so we pass provider.publicKey and signTransaction.
        // The splToken methods expect a 'payer' Keypair, but Phantom wallet only signs, so we must use the provider for signing.

        // Load SPL Token namespace
        const splToken = window.splToken;

        // Get or create sender's associated token account
        const fromTokenAccount = await splToken.getOrCreateAssociatedTokenAccount(
          connection,
          provider, // payer/signing provider
          mint,
          publicKey
        );

        document.getElementById("status").innerText = `Sender ATA: ${fromTokenAccount.address.toBase58()}`;

        for (const rec of recipients) {
          try {
            const toPubkey = new solanaWeb3.PublicKey(rec);

            // Get or create recipient ATA
            const toTokenAccount = await splToken.getOrCreateAssociatedTokenAccount(
              connection,
              provider,
              mint,
              toPubkey
            );

            const rawAmount = BigInt(Math.floor(amount * (10 ** decimals)));

            const tx = new solanaWeb3.Transaction().add(
              splToken.createTransferInstruction(
                fromTokenAccount.address,
                toTokenAccount.address,
                publicKey,
                rawAmount,
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

            document.getElementById("status").innerText += `\\n✅ Sent to ${rec} | TX: ${sig}`;
          } catch (err) {
            document.getElementById("status").innerText += `\\n❌ Failed to send to ${rec}: ${err.message}`;
          }
        }
      } catch (err) {
        document.getElementById("status").innerText += `\\n❌ Error: ${err.message}`;
      }
    };
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
