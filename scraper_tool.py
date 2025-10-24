import requests
from bs4 import BeautifulSoup

def scrape_jobs(keyword: str, location: str):
    """
    Scrape basic job listings from Indeed based on keyword and location.
    Returns a short summary of job results.
    """
    url = f"https://www.indeed.com/jobs?q={keyword}&l={location}"
    print(f"Scraping: {url}")
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for job in soup.select(".job_seen_beacon")[:5]:  # limit to 5 for quick test
        title = job.select_one("h2 span")
        company = job.select_one(".companyName")
        if title:
            results.append(f"{title.text.strip()} at {company.text.strip() if company else 'N/A'}")

    if not results:
        return "No jobs found or blocked by Indeed. Try again later."
    
    return "\n".join(results)
