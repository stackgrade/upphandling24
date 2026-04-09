#!/usr/bin/env python3
"""
Module 04: Tender Scraper - Production Version
Scrapes public procurement notices from TED (EU) with full details.
"""

import json
import time
import re
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
import os

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

@dataclass
class Tender:
    """Represents a public procurement notice."""
    source: str
    title: str
    url: str
    publication_date: str
    deadline: Optional[str]
    description: str
    estimated_value: Optional[str]
    country: str
    buyer: Optional[str] = None
    cpv_codes: Optional[str] = None
    raw_data: Optional[dict] = None

class TenderScraper:
    """Scrapes tenders from TED (EU public procurement)."""
    
    def __init__(self):
        self.tenders = []
        self.errors = []
        self.cache_dir = "/home/larry/projects/tender-system/data"
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def scrape_all(self) -> List[dict]:
        """Run all scrapers and return combined results."""
        print("🔍 Starting tender scrape...")
        
        # TED EU Tenders with full details
        ted_tenders = self.scrape_ted_detailed(max_notices=10)
        print(f"  TED: {len(ted_tenders)} tenders with details")
        self.tenders.extend(ted_tenders)
        
        # Save to cache
        self._save_cache()
        
        print(f"✅ Total: {len(self.tenders)} tenders scraped")
        return [asdict(t) for t in self.tenders]
    
    def scrape_ted_detailed(self, max_notices: int = 10) -> List[Tender]:
        """Scrape TED with full notice details."""
        tenders = []
        
        if not PLAYWRIGHT_AVAILABLE:
            print("  ⚠️ Playwright not available")
            return tenders
        
        try:
            # First get the search results
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto(
                    "https://ted.europa.eu/en/search/result?query=&search-scope=ALL",
                    timeout=30000
                )
                page.wait_for_load_state('networkidle', timeout=20000)
                time.sleep(2)
                
                # Get notice URLs
                notice_links = page.locator('a[href*="/en/notice/-/detail/"]')
                count = notice_links.count()
                print(f"    Found {count} notices")
                
                notice_urls = []
                for i in range(min(count, max_notices)):
                    try:
                        href = notice_links.nth(i).get_attribute('href')
                        if href:
                            full_url = f"https://ted.europa.eu{href}" if href.startswith('/') else href
                            notice_urls.append(full_url)
                    except:
                        continue
                
                browser.close()
            
            print(f"    Fetching details for {len(notice_urls)} notices...")
            
            # Now scrape each notice in detail
            for url in notice_urls:
                try:
                    tender = self._scrape_ted_notice_full(url)
                    if tender:
                        tenders.append(tender)
                        print(f"    ✓ {tender.title[:60]}...")
                except Exception as e:
                    print(f"    ✗ Error: {e}")
                    continue
                    
        except Exception as e:
            print(f"    ❌ TED error: {e}")
            self.errors.append({"source": "ted", "error": str(e)})
        
        return tenders
    
    def _scrape_ted_notice_full(self, url: str) -> Optional[Tender]:
        """Scrape a single TED notice with full details."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto(url, timeout=20000)
                page.wait_for_load_state('networkidle', timeout=15000)
                time.sleep(2)
                
                body = page.inner_text('body')
                lines = body.split('\n')
                
                # Extract title - it's the first long line after "Competition"
                # Structure is: notice number, then "Competition", then "Country: title", then actual title
                title = ""
                deadline = None
                buyer = None
                country_code = "EU"
                
                # Find title: look for line starting with country name and a longer description
                for i, line in enumerate(lines):
                    line = line.strip()
                    # Line format: "Germany: Installation of windows" or "Sweden: Service contract"
                    match = re.match(r'^(Germany|Sweden|Finland|Denmark|Norway|Austria|Belgium|Netherlands|France|Spain|Italy|Portugal|Poland|Czech|Hungary|Romania|Bulgaria|Croatia|Slovakia|Slovenia|Estonia|Latvia|Lithuania):\s*(.+)', line)
                    if match:
                        country_full = match.group(1)
                        title = match.group(2).strip()
                        # Map country to code
                        country_codes = {
                            "Germany": "DE", "Sweden": "SE", "Finland": "FI", 
                            "Denmark": "DK", "Norway": "NO", "Austria": "AT",
                            "Belgium": "BE", "Netherlands": "NL", "France": "FR",
                            "Spain": "ES", "Italy": "IT", "Portugal": "PT",
                            "Poland": "PL", "Czech": "CZ", "Hungary": "HU"
                        }
                        country_code = country_codes.get(country_full, country_full[:2].upper())
                        break
                
                # If no country:title pattern, find the longest non-empty line in title area
                if not title:
                    for i, line in enumerate(lines):
                        if len(line) > 50 and not line.startswith(' ') and 'Notice' not in line:
                            title = line.strip()
                            break
                
                # Get title from next line if still not found
                if not title or len(title) < 20:
                    for i, line in enumerate(lines):
                        if len(line) > 60:
                            title = line.strip()
                            break
                
                # Extract deadline
                deadline_match = re.search(r'Deadline for receipt of tenders:\s*([^\n]+)', body)
                if deadline_match:
                    deadline = deadline_match.group(1).strip()
                
                # Extract buyer
                buyer_match = re.search(r'Buyer:\s*([^\n]+)', body)
                if buyer_match:
                    buyer = buyer_match.group(1).strip()
                
                # Extract description - paragraphs after title
                description_parts = []
                found_title_area = False
                for line in lines:
                    line = line.strip()
                    if title and title in line:
                        found_title_area = True
                        continue
                    if found_title_area and len(line) > 50:
                        description_parts.append(line)
                        if len(description_parts) >= 2:
                            break
                
                description = ' '.join(description_parts)[:500] if description_parts else title
                
                browser.close()
                
                if title:
                    return Tender(
                        source="ted_europa",
                        title=title[:200],
                        url=url,
                        publication_date=datetime.now().strftime("%Y-%m-%d"),
                        deadline=deadline,
                        description=description[:500],
                        estimated_value=None,
                        country=country_code,
                        buyer=buyer
                    )
                
        except Exception as e:
            pass
        
        return None
    
    def _save_cache(self):
        """Save scraped tenders to cache file."""
        cache_file = f"{self.cache_dir}/tenders_cache.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump([asdict(t) for t in self.tenders], f, ensure_ascii=False, indent=2)
            print(f"  💾 Cached {len(self.tenders)} tenders")
        except Exception as e:
            print(f"  ⚠️ Cache error: {e}")

def main():
    """Main entry point."""
    scraper = TenderScraper()
    results = scraper.scrape_all()
    
    print(f"\n📊 Scraped {len(results)} tenders")
    
    # Output sample
    if results:
        print("\n📋 Sample tenders:")
        for t in results[:3]:
            print(f"   [{t['country']}] {t['title'][:70]}")
            print(f"   Deadline: {t['deadline'] or 'N/A'}")
            print(f"   Buyer: {t['buyer'] or 'N/A'}")
            print()
    
    return results

if __name__ == "__main__":
    main()