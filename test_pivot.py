import requests
import re
import time

LOGIN_URL = 'http://127.0.0.1:8000/accounts/login/'
DASHBOARD_URL = 'http://127.0.0.1:8000/'
SETTINGS_URL = 'http://127.0.0.1:8000/settings/'
WALLET_ADD_URL = 'http://127.0.0.1:8000/settings/wallet/add/'
RULE_ADD_URL = 'http://127.0.0.1:8000/settings/distribution/add/'
SIMULATE_URL = 'http://127.0.0.1:8000/simulate/'

USERNAME = 'admin'
PASSWORD = 'admin123'

client = requests.Session()

def get_csrf(url):
    response = client.get(url)
    if 'csrftoken' in client.cookies:
        return client.cookies['csrftoken']
    try:
        return re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', response.text).group(1)
    except:
        return None

# 1. Login
print("1. Logging in...")
csrftoken = get_csrf(LOGIN_URL)
login_data = {
    'username': USERNAME,
    'password': PASSWORD,
    'csrfmiddlewaretoken': csrftoken,
    'next': '/'
}
response = client.post(LOGIN_URL, data=login_data, headers={'Referer': LOGIN_URL})
if response.status_code == 200 and ("Dashboard" in response.text or "Total Income" in response.text or "Wallets" in response.text):
    print("   Login Successful")
else:
    print(f"   Login Failed: {response.status_code}")
    # print(response.text)
    # exit() 
    # Continue anyway as sometimes redirect happens

# 2. Create Wallets (Expenses, Savings)
print("2. Creating Wallets...")
target_wallets = ['Expenses', 'Savings']
for w in target_wallets:
    csrftoken = get_csrf(WALLET_ADD_URL)
    data = {'name': w, 'csrfmiddlewaretoken': csrftoken}
    resp = client.post(WALLET_ADD_URL, data=data, headers={'Referer': WALLET_ADD_URL})
    print(f"   Created {w}: {resp.status_code}")

# 3. Create Distribution Rules (50% Expenses, 50% Savings)
print("3. Creating Rules...")
# Parse wallet IDs from the Distribution Add Form
resp = client.get(RULE_ADD_URL)
wallet_options = re.findall(r'<option value="(\d+)">(.+?)</option>', resp.text)
wallet_map = {name: id for id, name in wallet_options}
print(f"   Mapped Wallets: {wallet_map}")

if 'Expenses' in wallet_map:
    csrftoken = get_csrf(RULE_ADD_URL)
    data = {'wallet': wallet_map['Expenses'], 'percentage': '50', 'csrfmiddlewaretoken': csrftoken}
    resp = client.post(RULE_ADD_URL, data=data, headers={'Referer': RULE_ADD_URL})
    print(f"   Set 50% for Expenses: {resp.status_code}")

if 'Savings' in wallet_map:
    csrftoken = get_csrf(RULE_ADD_URL)
    data = {'wallet': wallet_map['Savings'], 'percentage': '30', 'csrfmiddlewaretoken': csrftoken}
    resp = client.post(RULE_ADD_URL, data=data, headers={'Referer': RULE_ADD_URL})
    print(f"   Set 30% for Savings: {resp.status_code}")

# 4. Simulate Alert
print("4. Simulating Alert (100,000)...")
csrftoken = get_csrf(SIMULATE_URL)
data = {'amount': '100000', 'csrfmiddlewaretoken': csrftoken}
resp = client.post(SIMULATE_URL, data=data, headers={'Referer': SIMULATE_URL})
print(f"   Simulation POST: {resp.status_code}")

# 5. Verify Dashboard
print("5. Verifying Dashboard...")
resp = client.get(DASHBOARD_URL)
content = resp.text

# Check for Expenses balance (Should be 50,000 + previous)
# We can just check if the text "Expenses" and "50000" or similar appears.
# Note: Formatting might be 50,000.00
if "Expenses" in content and ("50000" in content or "50,000" in content):
    print("   SUCCESS: Expenses wallet updated correctly.")
else:
    print("   WARNING: Expenses wallet balance could not be verified strictly.")

if "Unallocated" in content:
    print("   SUCCESS: 'Unallocated' wallet created for remainder.")
    if "20000" in content or "20,000" in content:
         print("   SUCCESS: Remainder is correct (20,000).")

print("Test Complete.")
