import os
import requests
from bs4 import BeautifulSoup
from typing import Any, Callable, Set
import urllib.parse
from dotenv import load_dotenv

# Load token from environment file
load_dotenv()
TOKEN = os.getenv("SCRAPE_DO_TOKEN")

def scrape_jobs(keyword: str, location: str) -> str:
    """Scrape Indeed job listings via Scrape.do API (with fallback selectors)."""

    if not TOKEN:
        return "SCRAPE_DO_TOKEN is missing from your .env file."

    keyword = keyword.replace(" ", "+")
    location = location.replace(" ", "+")
    target_url = f"https://www.indeed.com/jobs?q={keyword}&l={location}"
    encoded_url = urllib.parse.quote(target_url)
    proxy_url = f"http://api.scrape.do/?token={TOKEN}&url={encoded_url}"

    print(f"Scraping via Scrape.do: {target_url}")

    response = requests.get(proxy_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    })
    if response.status_code != 200:
        return f"Failed to fetch page: HTTP {response.status_code}"

    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    job_cards = soup.select("div.job_seen_beacon, div.cardOutline")

    if not job_cards:
        return "No job cards found. Indeed may have changed its structure."

    for job in job_cards[:10]:
        title_el = job.select_one("h2.jobTitle span")
        company_el = (
            job.select_one("span.companyName")
            or job.select_one("span[data-testid='company-name']")
            or job.select_one("div[data-company-name']")
        )
        location_el = (
            job.select_one("div.companyLocation")
            or job.select_one("span[data-testid='text-location']")
        )

        title = title_el.text.strip() if title_el else "Unknown Title"
        company = company_el.text.strip() if company_el else "Unknown Company"
        location_name = location_el.text.strip() if location_el else location

        jobs.append(f"{title} at {company} — {location_name}")

    if not jobs:
        return "No jobs found on this page."

    return "\n".join(jobs)

# Export the callable set
scrap_functions: Set[Callable[..., Any]] = { scrape_jobs }
