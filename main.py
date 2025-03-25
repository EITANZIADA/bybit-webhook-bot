from flask import Flask, request
import time
import hmac
import hashlib
import requests
import json
import os

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

BYBIT_API_URL = "https://api.bybit.com"

def generate_signature(params, api_secret):
    sorted_params = sorted(params.items())
    query_string = "&".join([f"{key}={value}" for key, value in sorted_params])
    return hmac.new(
        bytes(api_secret, "utf-8"),
        bytes(query_string, "utf-8"),
        hashlib.sha256
    ).hexdigest()

def place_market_order(side):
    endpoint = "/v2/private/order/create"
    url = BYBIT_API_URL + endpoint

    params = {
        "api_key": API_KEY,
        "symbol": "ETHUSDT",
        "side": side,
        "order_type": "Market",
        "qty": 0.5,
        "time_in_force": "GoodTillCancel",
        "timestamp": int(time.time() * 1000)
    }

    params["sign"] = generate_signature(params, API_SECRET)
    response = requests.post(url, data=params)
    return response.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Received data:", data)

    action = data.get("action")
    if action == "long":
        result = place_market_order("Buy")
    elif action == "short":
        result = place_market_order("Sell")
    else:
        result = {"error": "Invalid action. Use 'long' or 'short'."}

    return json.dumps(result, indent=4)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
