from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>SPL Token Distributor</title>
<style>
  body { background-color: #121212; color: white; font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: auto; }
  label, input, textarea, select, button { display: block; width: 100%; margin-bottom: 15px; font-size: 16px; }
  input, textarea, select { padding: 10px; border-radius: 5px; border: none; }
  button { padding: 12px; background: linear-gradient(to right, #00ff90, #00d178); color: black; font-weight: bold; border: none; cursor: pointer; border-radius: 5px; }
  #status { margin-top: 15px; font-size: 14px; white-space: pre-wrap; color: #ccc; min-height: 80px; background-color: #222; padding: 10px; border-radius: 5px; }
  h1 { text-align: center; margin-bottom: 25px; }
</style>
</head>
<body>
<h1>🔗 SPL Token Distributor</h1>
<p>Replace this with your full app code...</p>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(debug=True)
