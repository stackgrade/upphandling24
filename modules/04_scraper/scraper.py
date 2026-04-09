#!/usr/bin/env python3
"""
Module 04: Tender Scraper - MAXED v3 (CLEAN)
Only returns tenders with REAL titles, no garbage.
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
    document_type: Optional[str] = None

class TenderScraper:
    """MAXED scraper - only real tenders, no garbage."""
    
    def __init__(self):
        self.tenders = []
        self.errors = []
        self.cache_dir = "/home/larry/projects/tender-system/data"
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def scrape_all(self) -> List[dict]:
        """Run scraper and return clean results."""
        print("🚀 MAXED SCRAPE v3 - Clean data only...")
        
        tenders = self.scrape_ted_max(50)
        self.tenders = tenders
        
        self._save_cache()
        
        print(f"✅ TOTAL: {len(self.tenders)} clean tenders")
        return [asdict(t) for t in self.tenders]
    
    def scrape_ted_max(self, max_notices: int = 50) -> List[Tender]:
        """Scrape notices, only return clean ones."""
        tenders = []
        
        if not PLAYWRIGHT_AVAILABLE:
            print("  ⚠️ Playwright not available")
            return tenders
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            # Get search results
            page = browser.new_page()
            page.goto(
                "https://ted.europa.eu/en/search/result?query=&search-scope=ALL",
                timeout=30000
            )
            page.wait_for_load_state('networkidle', timeout=20000)
            time.sleep(2)
            
            # Accept cookies
            try:
                page.locator('text=Accept all cookies').first.click(timeout=3000)
                time.sleep(1)
            except:
                pass
            
            # Get notice URLs
            notice_links = page.locator('a[href*="/en/notice/-/detail/"]')
            count = notice_links.count()
            
            urls = []
            for i in range(min(count, max_notices)):
                try:
                    href = notice_links.nth(i).get_attribute('href')
                    if href and '/en/notice/-/detail/' in href:
                        full_url = f"https://ted.europa.eu{href}" if href.startswith('/') else href
                        if full_url not in urls:
                            urls.append(full_url)
                except:
                    continue
            
            print(f"    Processing {len(urls)} notices...")
            page.close()
            
            # Fetch each notice
            for idx, url in enumerate(urls):
                try:
                    tender = self._fetch_notice(browser, url)
                    if tender and self._is_valid_tender(tender):
                        tenders.append(tender)
                        if (idx + 1) % 10 == 0:
                            print(f"    📥 {idx + 1}/{len(urls)} done ({len(tenders)} valid)...")
                except:
                    continue
            
            browser.close()
        
        return tenders
    
    def _is_valid_tender(self, tender: Tender) -> bool:
        """Check if tender has real content (not garbage)."""
        if not tender.title:
            return False
        if len(tender.title) < 15:
            return False
        if tender.title.startswith('An official website'):
            return False
        if 'This site uses cookies' in tender.title:
            return False
        if tender.country not in ['SE', 'DE', 'DK', 'FI', 'NO', 'PL', 'FR', 'ES', 'IT', 'NL', 'BE', 'AT', 'PT', 'CZ', 'HU', 'RO', 'BG', 'HR', 'SK', 'SI', 'EE', 'LV', 'LT', 'IE', 'MT', 'CY', 'LU', 'EU']:
            return False
        return True
    
    def _fetch_notice(self, browser, url: str) -> Optional[Tender]:
        """Fetch single notice with full details."""
        page = browser.new_page()
        page.goto(url, timeout=25000)
        page.wait_for_load_state('networkidle', timeout=15000)
        time.sleep(1.5)
        
        body = page.inner_text('body')
        page.close()
        
        if body.count('\n') < 50:
            return None
        
        # Extract title - look for first meaningful line
        title = ""
        country_code = "EU"
        
        # Try country:title pattern
        country_match = re.search(
            r'^(Germany|Sweden|Finland|Denmark|Norway|Austria|Belgium|Netherlands|France|Spain|Italy|Portugal|Poland|Czech|Hungary|Romania|Bulgaria|Croatia|Slovakia|Slovenia|Estonia|Latvia|Lithuania|Ireland|Malta|Cyprus|Luxembourg):\s*(.+)',
            body, re.MULTILINE
        )
        if country_match:
            country_full = country_match.group(1)
            title = country_match.group(2).strip()
            country_map = {
                "Germany": "DE", "Sweden": "SE", "Finland": "FI",
                "Denmark": "DK", "Norway": "NO", "Austria": "AT",
                "Belgium": "BE", "Netherlands": "NL", "France": "FR",
                "Spain": "ES", "Italy": "IT", "Portugal": "PT",
                "Poland": "PL", "Czech": "CZ", "Hungary": "HU",
            }
            country_code = country_map.get(country_full, "EU")
        
        # Fallback: first long line
        if not title or len(title) < 15:
            for line in body.split('\n'):
                line = line.strip()
                if 40 < len(line) < 200:
                    if not any(x in line for x in ['Notice', 'Buyer', 'Procedure', 'Deadline', 'Language', 'PDF', 'Email', 'help_outline']):
                        title = line
                        break
        
        # Deadline
        deadline = None
        dm = re.search(r'Deadline for receipt of tenders:\s*([^\n]+)', body)
        if dm:
            deadline = re.sub(r'\s*\(UTC[^)]*\)', '', dm.group(1)).strip()
        
        # Buyer
        buyer = None
        bm = re.search(r'Buyer:\s*([^\n]+)', body)
        if bm:
            buyer = bm.group(1).strip()
        
        # Description
        desc_lines = []
        after_title = False
        for line in body.split('\n'):
            if title[:20] in line:
                after_title = True
                continue
            if after_title and len(line.strip()) > 60:
                desc_lines.append(line.strip())
                if len(desc_lines) >= 3:
                    break
        description = ' '.join(desc_lines[:3])[:800] if desc_lines else title
        
        # Estimated value
        estimated_value = None
        vm = re.search(r'Estimated value:\s*([^\n]+)', body)
        if vm:
            estimated_value = vm.group(1).strip()
        
        # Document type
        doc_type = None
        dtm = re.search(r'^(Contract notice|Competition|result|Planning)', body, re.MULTILINE | re.IGNORECASE)
        if dtm:
            doc_type = dtm.group(1)
        
        if title and len(title) > 10:
            return Tender(
                source="ted_europa",
                title=title[:200],
                url=url,
                publication_date=datetime.now().strftime("%Y-%m-%d"),
                deadline=deadline,
                description=description[:800],
                estimated_value=estimated_value,
                country=country_code,
                buyer=buyer,
                document_type=doc_type
            )
        
        return None
    
    def _save_cache(self):
        """Save to cache."""
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
    
    print(f"\n📊 Scraped {len(results)} clean tenders")
    
    if results:
        print("\n📋 SAMPLE (first 5):")
        for t in results[:5]:
            print(f"\n   [{t['country']}] {t['title'][:70]}")
            print(f"   🏢 {t['buyer'] or 'N/A'}")
            print(f"   📅 {t['deadline'] or 'N/A'}")
    
    return results

if __name__ == "__main__":
    main()