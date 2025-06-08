# app.py
from flask import Flask, request, jsonify, render_template
import subprocess
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_fees', methods=['POST'])
def calculate_fees():
    try:
        data = request.json
        token_mint = data.get('tokenMint')
        count = int(data.get('count', 1))
        # Simple fee estimate: 0.000005 SOL per transfer + base fee 0.00001 SOL
        fee_per_transfer = 0.000005
        base_fee = 0.00001
        total_fee = count * fee_per_transfer + base_fee
        return jsonify({"fees": round(total_fee, 8)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/send', methods=['POST'])
def send_tokens():
    try:
        data = request.json
        secret_key = data.get('secretKey')
        token_mint = data.get('tokenMint')
        amount = data.get('amount')
        wallets_raw = data.get('wallets')

        if not all([secret_key, token_mint, amount, wallets_raw]):
            return jsonify({"error": "Missing parameters"}), 400

        # Prepare JSON to send to Node.js
        input_json = json.dumps({
            "secretKey": secret_key,
            "tokenMint": token_mint,
            "amount": amount,
            "wallets": wallets_raw
        })

        # Run the Node.js script (adjust path if needed)
        proc = subprocess.run(
            ["node", "send_tokens.js"],
            input=input_json.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300
        )

        stdout = proc.stdout.decode()
        stderr = proc.stderr.decode()

        if proc.returncode != 0:
            return jsonify({"error": "Node.js script error", "details": stderr}), 500

        # Node.js script returns JSON string
        try:
            result = json.loads(stdout)
            return jsonify(result)
        except json.JSONDecodeError:
            return jsonify({"error": "Failed to parse Node.js output", "raw": stdout}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
