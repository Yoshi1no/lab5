import json
import re
import requests
import sys
import os

API_TOKEN = "Apii"

def fetch_data(endpoint):
    request_url = f"https://api.ataix.kz{endpoint}"
    request_headers = {
        "accept": "application/json",
        "X-API-Key": API_TOKEN
    }
    resp = requests.get(request_url, headers=request_headers, timeout=20)
    return resp.json() if resp.status_code == 200 else f"Error: {resp.status_code}, {resp.text}"

def extract_unique_currencies(raw_text, keyword):
    word_list = re.findall(r'\b\w+\b', raw_text)
    currency_set = set()
    for idx in range(len(word_list) - 1):
        if word_list[idx] == keyword:
            cleaned_word = re.sub(r'[^a-zA-Zа-яА-Я]', '', word_list[idx + 1])
            currency_set.add(cleaned_word)
    return currency_set

currency_names = extract_unique_currencies(json.dumps(fetch_data("/api/symbols")), "base")
print("Available balance in USDT tokens:")
for curr in currency_names:
    balance_data = fetch_data(f"/api/user/balances/{curr}")
    balance_match = re.search(r"'available':\s*'([\d.]+)'", str(balance_data))
    if balance_match:
        print(f"{curr:<10} {balance_match.group(1)}")

def extract_trading_pairs(text_data, key):
    matches = re.findall(r'\b\w+(?:/\w+)?\b', text_data)
    pairs = []
    for i in range(len(matches) - 1):
        if matches[i] == key:
            pairs.append(matches[i + 1])
    return pairs

def extract_price_values(text_data, key):
    regex = rf'{key}[\s\W]*([-+]?\d*\.\d+|\d+)'
    price_values = re.findall(regex, text_data)
    return price_values

low_price_pairs = []
low_price_dict = {}
trading_pairs = extract_trading_pairs(json.dumps(fetch_data("/api/symbols")), "symbol")
price_values = extract_price_values(json.dumps(fetch_data("/api/prices")), "lastTrade")

print("\nTrading pairs with USDT where price <= 0.6 USDT:")
for idx in range(len(trading_pairs)):
    if "USDT" in trading_pairs[idx] and float(price_values[idx]) <= 0.6:
        print(f"{trading_pairs[idx]:<15} {price_values[idx]}")
        low_price_pairs.append(trading_pairs[idx])
        low_price_dict[trading_pairs[idx]] = price_values[idx]

while True:
    selected_pair = input("Select trading pair (TRX, IMX, 1INCH) --> ").upper()
    full_pair = f"{selected_pair}/USDT"
    if full_pair in low_price_pairs:
        selected_currency = selected_pair
        selected_price = low_price_dict[full_pair]
        break
    elif selected_pair == "EXIT":
        sys.exit()
    else:
        print("This trading pair is not in the list")

print(f"{selected_currency:<10} {selected_price}")
price_2pct = round(float(selected_price) * 0.98, 4)
price_5pct = round(float(selected_price) * 0.95, 4)
price_8pct = round(float(selected_price) * 0.92, 4)
print(f"Next, three buy orders will be created for {selected_currency},\n"
      f"1 token each at reduced prices:\n2% ({price_2pct}$), 5% ({price_5pct}$), 8% ({price_8pct}$)\n"
      f"Type 'yes' to proceed")

while True:
    confirmation = input("--> ")
    if confirmation == "yes":
        break
    elif confirmation == "exit":
        sys.exit()

def create_order(pair_symbol, order_price):
    order_url = "https://api.ataix.kz/api/orders"
    order_headers = {
        "accept": "application/json",
        "X-API-Key": API_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "symbol": pair_symbol,
        "side": "buy",
        "type": "limit",
        "quantity": 1,
        "price": order_price
    }
    response = requests.post(order_url, headers=order_headers, json=payload, timeout=20)
    return response.json() if response.status_code == 200 else f"Error: {response.status_code}, {response.text}"

order_2pct_resp = create_order(f"{selected_currency}/USDT", price_2pct)
order_5pct_resp = create_order(f"{selected_currency}/USDT", price_5pct)
order_8pct_resp = create_order(f"{selected_currency}/USDT", price_8pct)

orders_to_save = [order_2pct_resp, order_5pct_resp, order_8pct_resp]
output_file = "orders_data.json"

existing_orders = []
if os.path.exists(output_file):
    with open(output_file, "r") as f:
        try:
            existing_orders = json.load(f)
        except json.JSONDecodeError:
            existing_orders = []

for order_resp in orders_to_save:
    order_info = {
        "orderID": order_resp["result"]["orderID"],
        "price": order_resp["result"]["price"],
        "quantity": order_resp["result"]["quantity"],
        "symbol": order_resp["result"]["symbol"],
        "created": order_resp["result"]["created"],
        "status": order_resp["result"].get("status", "NEW")
    }
    existing_orders.append(order_info)

with open(output_file, "w") as f:
    json.dump(existing_orders, f, indent=4)

print(f"[+] Orders successfully created. Check results on ATAIX website under 'My Orders'.\n"
      f"Data saved to {output_file}")
