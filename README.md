# Greenhouse Job Links

A lightweight job link scraper that automatically collects job postings from Greenhouse job boards and updates them on weekdays.

## Features

- Scrapes job links from Greenhouse-powered job boards
- Saves results to CSV format with timestamps
- Automated weekday runs via GitHub Actions
- Lightweight and fast
- Handles duplicate removal

## File Structure

```
greenhouse-job-links/
├── scraper.py              # Lightweight link scraper
├── requirements.txt        # requests, beautifulsoup4
├── latest_links.csv        # Current day's links (auto-updated)
├── .github/workflows/
│   └── weekday-job-scraper.yml
└── README.md
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure target job boards in `.github/workflows/weekday-job-scraper.yml`

3. Run manually:
   ```bash
   python scraper.py <greenhouse_job_board_url>
   ```

## Usage

### Manual Scraping

```bash
python scraper.py https://jobs.lever.co/company
```

### Automated Scraping

The GitHub Action runs automatically Monday-Friday at 9 AM UTC. To customize:

1. Edit `.github/workflows/weekday-job-scraper.yml`
2. Add your target job board URLs in the "Run job scraper" step
3. Adjust the cron schedule if needed

### Output

Results are saved to `latest_links.csv` with columns:
- `title`: Job title
- `url`: Direct link to job posting
- `company`: Company domain
- `scraped_date`: When the job was scraped

## Configuration

To add multiple companies, update the workflow file:

```yaml
- name: Run job scraper
  run: |
    python scraper.py https://jobs.lever.co/company1
    python scraper.py https://boards.greenhouse.io/company2
```

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
