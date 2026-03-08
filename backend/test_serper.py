import requests
import json

api_key = "AoJbdMGh6GNZ7DZpDAffXsj9"
url = "https://google.serper.dev/search"

payload = json.dumps({
  "q": "software engineering internship 2026 india"
})
headers = {
  'X-API-KEY': api_key,
  'Content-Type': 'application/json'
}

try:
    print(f"Testing as Serper key...")
    response = requests.request("POST", url, headers=headers, data=payload)
    print(f"Status: {response.status_code}")
    print(f"Response Snippet: {json.dumps(response.json(), indent=2)[:500]}...")
except Exception as e:
    print(f"Error: {e}")
