import httpx
from bs4 import BeautifulSoup

def scrape_wwr_jobs():
    url = "https://weworkremotely.com/remote-jobs.rss"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = httpx.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "xml")
        items = soup.find_all("item")
        
        jobs = []
        for item in items:
            title = item.find("title").text if item.find("title") else "No Title"
            link = item.find("link").text if item.find("link") else None
            description = item.find("description").text if item.find("description") else ""
            
            if link:
                jobs.append({
                    "title": title,
                    "link": link,
                    "description": description
                })
        
        return jobs
    except Exception as e:
        print(f"Scraping error: {e}")
        return []

def scrape_freelancers(keyword):
    # This is a mock implementation as scraping LinkedIn/Freelancer directly 
    # usually requires complex anti-bot bypass or API access.
    # We simulate the scraping results for the demonstration.
    
    # In a real scenario, you'd use something like Selenium or a specialized scraping API.
    print(f"Scouting for: {keyword}")
    
    # Mock data based on the keyword
    mock_results = [
        {"name": f"Expert {keyword} 1", "link": f"https://linkedin.com/in/expert1", "skills": f"{keyword}, Design, Strategy", "source": "LinkedIn"},
        {"name": f"Pro {keyword} 2", "link": f"https://freelancer.com/u/pro2", "skills": f"{keyword}, Development", "source": "Freelancer.com"},
        {"name": f"Senior {keyword} 3", "link": f"https://indeed.com/r/senior3", "skills": f"{keyword}, Management", "source": "Indeed"},
    ]
    
    return mock_results

if __name__ == "__main__":
    jobs = scrape_wwr_jobs()
    print(f"Scraped {len(jobs)} jobs.")
    
    freelancers = scrape_freelancers("Logo Designer")
    print(f"Sourced {len(freelancers)} freelancers.")

