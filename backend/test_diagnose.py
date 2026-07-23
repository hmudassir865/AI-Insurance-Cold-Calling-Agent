import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

print(f"Space: [{settings.SIGNALWIRE_SPACE}]")
print(f"Project: [{settings.SIGNALWIRE_PROJECT_ID}]")
print(f"Token: {settings.SIGNALWIRE_AUTH_TOKEN[:10]}..." if settings.SIGNALWIRE_AUTH_TOKEN else "EMPTY")
print(f"Phone: [{settings.SIGNALWIRE_PHONE_NUMBER}]")
print(f"Webhook: [{settings.SIGNALWIRE_WEBHOOK_BASE_URL}]")

if not all([settings.SIGNALWIRE_SPACE, settings.SIGNALWIRE_PROJECT_ID, settings.SIGNALWIRE_AUTH_TOKEN]):
    print("ERROR: SignalWire credentials missing in .env")
    exit(1)

clean = settings.SIGNALWIRE_SPACE.replace(".signalwire.com", "")
base_url = f"https://{clean}.signalwire.com/api/twilio"
print(f"Base URL: {base_url}")

import requests
url = f"{base_url}/2010-04-01/Accounts/{settings.SIGNALWIRE_PROJECT_ID}/Calls.json"
print(f"Testing: {url}")
r = requests.get(url, auth=(settings.SIGNALWIRE_PROJECT_ID, settings.SIGNALWIRE_AUTH_TOKEN), timeout=15)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Calls count: {len(data.get('calls', []))}")
    print(f"Account name: {data.get('account_sid', 'N/A')}")
else:
    print(f"Response: {r.text[:1000]}")
