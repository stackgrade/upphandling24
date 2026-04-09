# Module 04: Scraper - Tender Data Extraction

## Purpose
Scrape public procurement notices from multiple Swedish and EU sources.
Output: List of tenders with title, link, date, description, estimated value.

## Data Sources
1. **TED (EU)** - ted.europa.eu - EU-level public procurement (> thresholds)
2. **OffentligUpphandling.se** - Swedish national platform
3. **Visma Procurement** - visma.com/procurement

## Output Format
```python
{
    "source": "ted_europa",
    "title": "string",
    "url": "string", 
    "publication_date": "YYYY-MM-DD",
    "deadline": "YYYY-MM-DD",
    "description": "string",
    "estimated_value": "SEK amount or null",
    "country": "SE"  # ISO code
}
```

## Technical Approach
- Python + Playwright (headless browser via GitHub Actions)
- YAML config for source URLs and selectors
- Scheduled via GitHub Actions (cron: 0 6 * * *)
- Results stored in Google Sheets (via Module 03)

## Files
- scraper.py - Main scraper logic
- sources.py - Source-specific extraction
- config.yaml - Source URLs and selectors  
- test_scraper.py - Test suite

## Status
⏳ In Progress