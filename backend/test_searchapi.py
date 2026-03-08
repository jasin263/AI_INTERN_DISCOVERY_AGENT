import requests
import json

api_key = "AoJbdMGh6GNZ7DZpDAffXsj9"
url = "https://www.searchapi.io/api/v1/search"

params = {
  "engine": "google_jobs",
  "q": "software engineering internship 2026 india",
  "api_key": api_key
}

try:
    print(f"Testing as SearchAPI.io key (Google Jobs engine)...")
    response = requests.get(url, params=params)
    print(f"Status: {response.status_code}")
    data = response.json()
    if response.status_code == 200:
        jobs = data.get("jobs_results", [])
        print(f"Found {len(jobs)} jobs via SearchAPI!")
        if jobs:
            print(f"First Job: {jobs[0].get('title')} at {jobs[0].get('company_name')}")
    else:
        print(f"Response: {json.dumps(data, indent=2)}")
except Exception as e:
    print(f"Error: {e}")
