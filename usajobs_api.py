import requests
import json
import re
from utils.config import USAJOBS_API_KEY   # assuming this is correct

class USAJobsAPI:
    def __init__(self):
        self.api_key = USAJOBS_API_KEY
        self.base_url = "https://data.usajobs.gov/api"
        self.headers = {
            "User-Agent": "job_hunt_assistant/1.0",
            "Authorization-Key": self.api_key          # ← FIXED: this is the correct header name
        }

    def search_jobs(self, keyword: str, location: str, results_per_page: int = 10) -> list:
        if not self.api_key:
            print("Error: USAJOBS_API_KEY not configured")
            return []

        params = {
            "Keyword": keyword,
            "LocationName": location,
            "ResultsPerPage": results_per_page,
            "SortField": "DatePosted",
            "SortDirection": "Desc",
        }

        try:
            response = requests.get(f"{self.base_url}/Search", headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("SearchResult", {}).get("SearchResultItems", [])
                parsed_jobs = []
                for job_item in jobs:
                    job_data = self._parse_job_data(job_item)
                    if job_data:
                        parsed_jobs.append(job_data)
                print(f"✓ Found {len(parsed_jobs)} jobs for keyword: '{keyword}' in '{location}'")
                return parsed_jobs
            else:
                print(f"API Request failed with error code {response.status_code} - {response.text[:200]}")
                return []
        except Exception as e:
            print(f"Error searching jobs: {e}")
            return []

    def _parse_job_data(self, job_item: dict) -> dict | None:
        try:
            job = job_item.get("MatchedObjectDescriptor", {})

            # Salary handling
            rem = job.get("PositionRemuneration", [])
            salary = ""
            if rem:
                min_sal = rem[0].get("MinimumRange", "")
                max_sal = rem[0].get("MaximumRange", "")
                salary = f"{min_sal} – {max_sal}" if max_sal else min_sal

            return {
                "id": job.get("PositionID", ""),
                "title": job.get("PositionTitle", ""),
                "agency": job.get("OrganizationName", ""),
                "location": job.get("PositionLocationDisplay", ""),
                "salary": salary,
                "url": job.get("PositionURI", ""),
                "description": self._clean_description(
                    job.get("UserArea", {}).get("Details", {}).get("JobSummary", "")
                ),
                "requirements": job.get("QualificationSummary", ""),
                "posted_date": job.get("PublicationStartDate", ""),
                "closing_date": job.get("ApplicationCloseDate", "")
            }
        except Exception as e:
            print(f"Error parsing job data: {e}")
            return None

    def _clean_description(self, description: str) -> str:
        if not description:
            return ""
        cleaned = re.sub(r'<[^>]*>', ' ', description)   # strip HTML tags
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()   # normalize whitespace
        return cleaned[:2000]

    def get_job_details(self, job_id: str) -> dict:
        try:
            # Note: some use /codelist/positions/ or /Search/Position/ – test which works with your key
            response = requests.get(f"{self.base_url}/positions/{job_id}", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching job details: {response.status_code} - {response.text[:200]}")
                return {}
        except Exception as e:
            print(f"Error getting job details: {e}")
            return {}