#!/usr/bin/env python3
"""
Lightweight job link scraper for Greenhouse job boards.
Discovers jobs across all greenhouse.io companies targeting specific roles and locations.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime, timedelta
import os
import sys

def discover_greenhouse_job_links(target_roles, target_locations, hours_threshold=2):
    """
    Discover job links across all greenhouse.io without targeting specific companies
    """
    job_links = []
    current_time = datetime.now()

    print("Searching for all available job postings...")

    # Method 1: Search for each role in each location
    for role in target_roles:
        for location in target_locations:
            print(f"Searching for: {role} in {location}")

            try:
                search_url = "https://duckduckgo.com/html/"
                params = {
                    'q': f'site:job-boards.greenhouse.io "{role}" "{location}"'
                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                response = requests.get(search_url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Extract all greenhouse job links
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link.get('href')
                        if href and 'job-boards.greenhouse.io' in href and '/jobs/' in href:

                            # Extract company from URL
                            company = extract_company_from_url(href)

                            # Add all found jobs (no time filter for testing)
                            if True:
                                job_links.append({
                                    'link': href,
                                    'company': company or 'unknown',
                                    'role_matched': role,
                                    'location_searched': location,
                                    'found_at': current_time.strftime('%Y-%m-%d %H:%M:%S')
                                })

                time.sleep(2)  # Be respectful with search requests

            except Exception as e:
                print(f"  Error searching for {role} in {location}: {e}")
                continue

    # Method 2: Enhanced search patterns with US filter only
    search_patterns = [
        'site:job-boards.greenhouse.io "data scientist" "posted" "US"',
        'site:job-boards.greenhouse.io "machine learning" "new" "US"',
        'site:job-boards.greenhouse.io "data analyst" "hiring" "US"',
        'site:job-boards.greenhouse.io "ai engineer" "posted" "US"'
    ]

    for pattern in search_patterns:
        print(f"Searching pattern: {pattern}")
        try:
            search_url = "https://duckduckgo.com/html/"
            params = {'q': pattern}
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    if href and 'job-boards.greenhouse.io' in href and '/jobs/' in href:

                        # Determine which role this matches
                        role_matched = determine_role_from_url(href, target_roles)

                        if role_matched:
                            company = extract_company_from_url(href)

                            # Add all found jobs (no time filter for testing)
                            if True:
                                job_links.append({
                                    'link': href,
                                    'company': company or 'unknown',
                                    'role_matched': role_matched,
                                    'location_searched': 'US',
                                    'found_at': current_time.strftime('%Y-%m-%d %H:%M:%S')
                                })

            time.sleep(1)

        except Exception as e:
            print(f"  Error with pattern {pattern}: {e}")
            continue

    return job_links

def determine_location_from_pattern(pattern, target_locations):
    """Extract location from search pattern"""
    for location in target_locations:
        if location.lower() in pattern.lower():
            return location
    return "unknown"

def extract_company_from_url(url):
    """Extract company name from greenhouse URL"""
    try:
        if 'job-boards.greenhouse.io' in url:
            parts = url.split('/')
            for i, part in enumerate(parts):
                if 'greenhouse.io' in part and i + 1 < len(parts):
                    company = parts[i + 1]
                    if company and company not in ['jobs', 'www', '', 'job-boards']:
                        return company.lower().strip()
        return None
    except:
        return None

def determine_role_from_url(url, target_roles):
    """Determine which role this job matches based on URL content"""
    try:
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            page_text = response.text.lower()

            for role in target_roles:
                if role.lower() in page_text:
                    return role

        return None
    except:
        return None

def is_likely_recent(job_url, hours_threshold):
    """
    Quick check if job is likely recent (simplified version)
    """
    try:
        response = requests.get(job_url, timeout=8)
        if response.status_code != 200:
            return False

        # Quick text search for recent indicators
        page_text = response.text.lower()

        # Look for obvious recent indicators
        recent_indicators = [
            'posted today', 'posted 1 hour', 'posted 2 hour',
            'new posting', 'just posted', '1 hr ago', '2 hrs ago'
        ]

        for indicator in recent_indicators:
            if indicator in page_text:
                return True

        # If no clear indicators, assume it might be recent
        # (This is a simplified check - you can make it more strict)
        return True

    except:
        return False

def remove_duplicates(job_links):
    """
    Remove duplicate job links
    """
    seen_links = set()
    unique_jobs = []

    for job in job_links:
        link = job['link']
        if link not in seen_links:
            seen_links.add(link)
            unique_jobs.append(job)

    return unique_jobs

def load_existing_links(filename):
    """
    Load existing links to avoid duplicates across runs
    """
    existing_links = set()
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_links.add(row['link'])
        except:
            pass

    return existing_links

def save_links_to_csv(job_links, filename='latest_links.csv'):
    """
    Save job links to CSV
    """
    if not job_links:
        print("No new job links to save")
        return

    # Load existing links
    existing_links = load_existing_links(filename)

    # Filter out existing links
    new_links = [job for job in job_links if job['link'] not in existing_links]

    if not new_links:
        print("No new unique links found")
        return

    # Append new links to existing file
    file_exists = os.path.exists(filename)

    with open(filename, 'a' if file_exists else 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header if new file
        if not file_exists:
            writer.writerow(['link', 'company', 'role_matched', 'location_searched', 'found_at'])

        # Write new links
        for job in new_links:
            writer.writerow([
                job['link'],
                job['company'],
                job['role_matched'],
                job.get('location_searched', 'unknown'),
                job['found_at']
            ])

    print(f"Added {len(new_links)} new job links to {filename}")

def cleanup_old_data():
    """
    Remove yesterday's data files
    """
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y%m%d')

    # Remove any files from yesterday
    for filename in os.listdir('.'):
        if filename.startswith(f'links_{yesterday_str}') or filename.startswith(f'jobs_{yesterday_str}'):
            try:
                os.remove(filename)
                print(f"Removed old file: {filename}")
            except:
                pass

def main():
    """
    Main function for lightweight job link scraping
    """
    # Target roles
    target_roles = [
        "data scientist",
        "data analyst",
        "machine learning engineer",
        "ai engineer"
    ]

    # Target locations (full names)
    target_locations = [
        "Atlanta",
        "New York",
        "San Francisco",
        "Boston"
    ]

    print("=" * 50)
    print("LIGHTWEIGHT JOB LINK SCRAPER")
    print("=" * 50)
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Cleanup old data (only on first run of the day)
    current_hour = datetime.now().hour
    if current_hour == 7:  # First run of the day
        cleanup_old_data()

    # Get recent job links from across all greenhouse companies with location targeting
    job_links = discover_greenhouse_job_links(target_roles, target_locations, hours_threshold=2)

    # Remove duplicates
    unique_links = remove_duplicates(job_links)

    print(f"\nFound {len(job_links)} total links")
    print(f"Unique links: {len(unique_links)}")

    # Save to CSV
    save_links_to_csv(unique_links)

    # Show summary
    if unique_links:
        role_counts = {}
        for job in unique_links:
            role = job['role_matched']
            role_counts[role] = role_counts.get(role, 0) + 1

        print("\nNew links by role:")
        for role, count in role_counts.items():
            print(f"  {role}: {count}")

    print(f"Scraping completed at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()