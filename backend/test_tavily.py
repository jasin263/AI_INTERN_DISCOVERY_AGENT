import requests
import json

api_key = "AoJbdMGh6GNZ7DZpDAffXsj9"
base_url = "https://api.tavily.com/search"

payload = {
    "api_key": api_key,
    "query": "software internship 2026",
    "search_depth": "basic",
    "max_results": 5
}

try:
    print(f"Testing Tavily with query: {payload['query']}")
    response = requests.post(base_url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
