import requests
from config import GROK_API_KEY
headers = {"Authorization": f"Bearer {GROK_API_KEY}", "Content-Type": "application/json"}
payload = {
    "model": "grok-beta",
    "messages": [{"role": "user", "content": "Fetch details for the song 'Bohemian Rhapsody' by Queen"}]
}
response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload)
print(response.json())