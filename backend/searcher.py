import requests
import json
import os
from bs4 import BeautifulSoup
from typing import List
from internship import Internship

class Searcher:
    """
    Searcher module to find internship opportunities from various sources.
    Automates discovery across LinkedIn, Indeed, Internshala, Wellfound, and Tech Giants.
    """
    def __init__(self, api_key: str = "AoJbdMGh6GNZ7DZpDAffXsj9"):
        self.api_key = api_key
        self.base_url = "https://www.searchapi.io/api/v1/search"
        self.db_path = os.path.join(os.path.dirname(__file__), "discovered_jobs.json")

    def automated_search(self, role: str, batch: str = "2026") -> List[Internship]:
        """
        Performs a live web sweep using SearchAPI.io (Google Jobs engine).
        Automatically saves new results to the local database.
        """
        query = f"{role} internship {batch} batch india"
        print(f"Live searching SearchAPI for: {query}")

        params = {
            "engine": "google_jobs",
            "q": query,
            "api_key": self.api_key,
            "location": "India"
        }

        live_jobs = []
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                results = data.get("jobs_results", [])
                print(f"SearchAPI found {len(results)} live results.")
                
                for res in results:
                    title = res.get("title", f"{role} Intern")
                    company = res.get("company_name", "Unknown Company")
                    location = res.get("location", "Remote / India")
                    link = res.get("job_id", "#")
                    
                    apply_options = res.get("apply_options", [])
                    if apply_options:
                        link = apply_options[0].get("link", link)

                    live_jobs.append(Internship(
                        role_title=title,
                        company_name=company,
                        location=location,
                        application_link=link,
                        required_skills=[role],
                        batch=batch,
                        posted_date=res.get("detected_extensions", {}).get("posted_at", "Recently")
                    ))
                
                print(f"Parsed {len(live_jobs)} live jobs from SearchAPI.")
                # Save new findings to DB
                if live_jobs:
                    self.save_discovered_jobs(live_jobs)
            else:
                print(f"SearchAPI Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"SearchAPI Request Error: {e}")

        # Return combined and deduplicated results (Local + Live)
        return self.get_discovered_jobs()

    def save_discovered_jobs(self, new_jobs: List[Internship]):
        """
        Saves new internship results to the local database with deduplication.
        """
        existing_jobs = self.get_discovered_jobs()
        
        # Deduplicate using application_link
        seen_links = {job.application_link for job in existing_jobs}
        
        added_count = 0
        for job in new_jobs:
            if job.application_link not in seen_links:
                existing_jobs.insert(0, job) # Add new jobs to the TOP
                seen_links.add(job.application_link)
                added_count += 1
        
        if added_count > 0:
            try:
                # Limit size to prevent JSON blooming infinitely (e.g., keep last 500)
                json_data = [item.__dict__ for item in existing_jobs[:500]]
                with open(self.db_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=4)
                print(f"Database updated: Added {added_count} new jobs. Total records: {len(json_data)}")
            except Exception as e:
                print(f"Error saving jobs: {e}")

    def get_discovered_jobs(self) -> List[Internship]:
        """
        Returns verified discovered results from the local database.
        """
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Convert dicts back to Internship objects
                    return [Internship(**item) for item in data]
            except Exception as e:
                print(f"Error loading discovered jobs: {e}")
        
        return []
