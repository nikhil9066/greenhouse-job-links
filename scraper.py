#!/usr/bin/env python3
"""
Lightweight job link scraper for Greenhouse job boards.
Scrapes job links and saves them to latest_links.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import sys
from urllib.parse import urljoin, urlparse

def scrape_greenhouse_jobs(company_url):
    """
    Scrape job links from a Greenhouse job board.

    Args:
        company_url (str): URL to the company's Greenhouse job board

    Returns:
        list: List of dictionaries containing job information
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(company_url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        jobs = []

        # Find job links (common Greenhouse selectors)
        job_links = soup.find_all('a', href=True)

        for link in job_links:
            href = link.get('href')
            if href and ('/jobs/' in href or '/job/' in href):
                # Make absolute URL
                full_url = urljoin(company_url, href)

                # Extract job title
                title = link.get_text(strip=True)
                if title and len(title) > 3:  # Filter out short/empty titles
                    jobs.append({
                        'title': title,
                        'url': full_url,
                        'company': urlparse(company_url).netloc,
                        'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

        # Remove duplicates based on URL
        seen_urls = set()
        unique_jobs = []
        for job in jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)

        return unique_jobs

    except Exception as e:
        print(f"Error scraping {company_url}: {str(e)}")
        return []

def save_to_csv(jobs, filename='latest_links.csv'):
    """
    Save job data to CSV file.

    Args:
        jobs (list): List of job dictionaries
        filename (str): Output CSV filename
    """
    if not jobs:
        print("No jobs to save")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'url', 'company', 'scraped_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for job in jobs:
            writer.writerow(job)

    print(f"Saved {len(jobs)} jobs to {filename}")

def main():
    """Main function to run the scraper."""
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <greenhouse_job_board_url>")
        print("Example: python scraper.py https://jobs.lever.co/company")
        sys.exit(1)

    company_url = sys.argv[1]

    print(f"Scraping jobs from: {company_url}")
    jobs = scrape_greenhouse_jobs(company_url)

    if jobs:
        save_to_csv(jobs)
        print(f"Found {len(jobs)} unique job postings")
    else:
        print("No jobs found")

if __name__ == "__main__":
    main()