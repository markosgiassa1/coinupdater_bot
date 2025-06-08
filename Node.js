const fs = require('fs');
const solanaWeb3 = require('@solana/web3.js');
const {
  getOrCreateAssociatedTokenAccount,
  createTransferInstruction,
  TOKEN_PROGRAM_ID
} = require('@solana/spl-token');

async function sendSPLToken(connection, senderKeypair, mintPubkey, recipientPubkey, amount) {
  const senderATA = await getOrCreateAssociatedTokenAccount(connection, senderKeypair, mintPubkey, senderKeypair.publicKey);
  const recipientATA = await getOrCreateAssociatedTokenAccount(connection, senderKeypair, mintPubkey, recipientPubkey);

  const transferIx = createTransferInstruction(
    senderATA.address,
    recipientATA.address,
    senderKeypair.publicKey,
    amount,
    [],
    TOKEN_PROGRAM_ID
  );

  const transaction = new solanaWeb3.Transaction().add(transferIx);
  transaction.feePayer = senderKeypair.publicKey;

  const { blockhash } = await connection.getLatestBlockhash();
  transaction.recentBlockhash = blockhash;

  const signature = await solanaWeb3.sendAndConfirmTransaction(connection, transaction, [senderKeypair]);
  return signature;
}

async function main() {
  // Read input JSON from stdin
  const input = await new Promise((resolve, reject) => {
    let data = '';
    process.stdin.on('data', chunk => data += chunk);
    process.stdin.on('end', () => resolve(data));
    process.stdin.on('error', err => reject(err));
  });

  let params;
  try {
    params = JSON.parse(input);
  } catch (e) {
    console.error(JSON.stringify({ error: 'Invalid JSON input' }));
    process.exit(1);
  }

  const { secretKey, tokenMint, amount, wallets } = params;

  let secretKeyArray;
  try {
    secretKeyArray = JSON.parse(secretKey);
  } catch (e) {
    console.error(JSON.stringify({ error: 'Invalid secretKey JSON array' }));
    process.exit(1);
  }

  const senderKeypair = solanaWeb3.Keypair.fromSecretKey(Uint8Array.from(secretKeyArray));
  const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl('mainnet-beta'), 'confirmed');
  const mintPubkey = new solanaWeb3.PublicKey(tokenMint);
  const amtBigInt = BigInt(amount) * BigInt(10 ** 9); // Assuming decimals=9, could add input if needed
  const walletList = wallets.split('\n').map(w => w.trim()).filter(Boolean);

  const results = [];
  for (const wallet of walletList) {
    try {
      const recipientPubkey = new solanaWeb3.PublicKey(wallet);
      const sig = await sendSPLToken(connection, senderKeypair, mintPubkey, recipientPubkey, amtBigInt);
      results.push({ wallet, status: "success", signature: sig });
      await new Promise(r => setTimeout(r, 2000)); // avoid flooding
    } catch (error) {
      results.push({ wallet, status: "failed", error: error.message });
    }
  }

  // Output results as JSON string to stdout
  console.log(JSON.stringify({ results }));
  process.exit(0);
}

main().catch(e => {
  console.error(JSON.stringify({ error: e.message }));
  process.exit(1);
});
