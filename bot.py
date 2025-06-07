<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Solana Token Distributor</title>
<script src="https://cdn.jsdelivr.net/npm/@solana/web3.js@1.73.0/lib/index.iife.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@solana/spl-token@0.3.5/lib/index.iife.min.js"></script>
<style>
  body { font-family: Arial, sans-serif; max-width: 600px; margin: 20px auto; }
  textarea { width: 100%; height: 80px; }
  input, select, button { width: 100%; margin: 6px 0; padding: 8px; font-size: 1em; }
  #status { white-space: pre-wrap; min-height: 80px; background: #eee; padding: 10px; margin-top: 10px; }
</style>
</head>
<body>

<h2>Solana Token Distributor</h2>

<label for="walletList">Recipient Wallet Addresses (one per line):</label>
<textarea id="walletList" placeholder="Paste one wallet address per line"></textarea>

<label for="mintAddress">Token Mint Address:</label>
<input id="mintAddress" placeholder="Token mint address (e.g. USDC mint)" />

<label for="decimals">Token Decimals (e.g. 6 for USDC):</label>
<input id="decimals" type="number" min="0" max="18" value="6" />

<label for="amount">Amount per Recipient:</label>
<input id="amount" type="number" step="any" min="0" placeholder="Amount to send" />

<label for="network">Select Network:</label>
<select id="network">
  <option value="mainnet-beta">Mainnet Beta</option>
  <option value="devnet">Devnet</option>
  <option value="testnet">Testnet</option>
</select>

<button id="connectBtn">Connect Wallet</button>
<button id="submitBtn" disabled>Send Tokens</button>

<div id="status"></div>

<script>
  let provider = null;
  let publicKey = null;

  const connectBtn = document.getElementById("connectBtn");
  const claimBtn = document.getElementById("submitBtn");
  const status = document.getElementById("status");
  const networkSelect = document.getElementById("network");

  connectBtn.addEventListener('click', async () => {
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    const isDesktop = !isIOS && !/Android/.test(navigator.userAgent);

    if (window.solana?.isPhantom) {
      provider = window.solana;
    } else if (window.solflare?.isSolflare) {
      provider = window.solflare;
    } else {
      if (isIOS) {
        status.innerText = "📱 Please open this site inside the Phantom or Solflare mobile app browser.";
      } else if (isDesktop) {
        status.innerText = "💻 Please install the Phantom or Solflare browser extension and refresh this page.";
      } else {
        status.innerText = "⚠️ No wallet detected. Use Phantom or Solflare.";
      }
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
    const recipientsText = document.getElementById("walletList").value.trim();
    const mintAddress = document.getElementById("mintAddress").value.trim();
    const decimalsInput = document.getElementById("decimals").value.trim();
    const amountInput = document.getElementById("amount").value.trim();

    if (!recipientsText) {
      alert("Please enter at least one recipient wallet address.");
      return;
    }
    if (!mintAddress) {
      alert("Please enter the token mint address.");
      return;
    }
    if (!decimalsInput || isNaN(decimalsInput)) {
      alert("Please enter valid token decimals.");
      return;
    }
    if (!amountInput || isNaN(amountInput) || Number(amountInput) <= 0) {
      alert("Please enter a valid amount greater than zero.");
      return;
    }

    const decimals = parseInt(decimalsInput, 10);
    const amount = parseFloat(amountInput);
    const recipients = recipientsText.split('\n').map(r => r.trim()).filter(r => r.length > 0);

    const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl(network), "confirmed");
    const splToken = window.splToken;

    status.innerText = "Starting token distribution...\n";

    try {
      const mint = new solanaWeb3.PublicKey(mintAddress);
      // get sender's associated token account
      const fromTokenAccount = await splToken.getOrCreateAssociatedTokenAccount(
        connection,
        provider,
        mint,
        publicKey
      );

      for (const rec of recipients) {
        try {
          const toPubkey = new solanaWeb3.PublicKey(rec);
          // get or create recipient ATA
          const toTokenAccount = await splToken.getOrCreateAssociatedTokenAccount(
            connection,
            provider,
            mint,
            toPubkey
          );

          const tx = new solanaWeb3.Transaction().add(
            splToken.createTransferInstruction(
              fromTokenAccount.address,
              toTokenAccount.address,
              publicKey,
              BigInt(amount * Math.pow(10, decimals)),
              [],
              splToken.TOKEN_PROGRAM_ID
            )
          );

          tx.feePayer = publicKey;
          const { blockhash } = await connection.getLatestBlockhash();
          tx.recentBlockhash = blockhash;

          // sign and send transaction
          const signedTx = await provider.signTransaction(tx);
          const signature = await connection.sendRawTransaction(signedTx.serialize());
          await connection.confirmTransaction(signature);

          status.innerText += `✅ Sent to ${rec} (tx: ${signature})\n`;
        } catch (err) {
          status.innerText += `❌ Failed for ${rec}: ${err.message}\n`;
        }
      }
      status.innerText += "🎉 Distribution completed.";
    } catch (err) {
      status.innerText += `\n❌ Error: ${err.message}`;
    }
  });
</script>

</body>
</html>
