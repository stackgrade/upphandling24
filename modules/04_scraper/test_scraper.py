#!/usr/bin/env python3
"""
Test suite for Module 04: Scraper
"""

import unittest
import sys
import os

# Add module path
sys.path.insert(0, os.path.dirname(__file__))

from scraper import TenderScraper, Tender

class TestScraper(unittest.TestCase):
    
    def setUp(self):
        self.scraper = TenderScraper()
    
    def test_tender_dataclass(self):
        """Test Tender dataclass creation."""
        t = Tender(
            source="test",
            title="Test Tender",
            url="https://example.com",
            publication_date="2026-04-09",
            deadline=None,
            description="A test tender",
            estimated_value="100000 SEK",
            country="SE"
        )
        self.assertEqual(t.source, "test")
        self.assertEqual(t.title, "Test Tender")
        self.assertEqual(t.country, "SE")
    
    def test_scrape_ted(self):
        """Test TED scraping (requires network)."""
        tenders = self.scraper.scrape_ted()
        self.assertIsInstance(tenders, list)
        for t in tenders:
            self.assertIsInstance(t, Tender)
    
    def test_scrape_swedish(self):
        """Test Swedish source scraping."""
        tenders = self.scraper._scrape_mercell()
        self.assertIsInstance(tenders, list)
    
    def test_output_format(self):
        """Test that output is properly formatted."""
        results = self.scraper.scrape_all()
        self.assertIsInstance(results, list)
        
        for r in results:
            self.assertIn('source', r)
            self.assertIn('title', r)
            self.assertIn('url', r)
            self.assertIn('country', r)
            self.assertEqual(r['country'], 'SE')

class TestTenderData(unittest.TestCase):
    
    def test_swedish_country_code(self):
        """Verify country code is SE."""
        t = Tender(source="test", title="t", url="u", 
                   publication_date="d", deadline=None, 
                   description="d", estimated_value=None, country="SE")
        self.assertEqual(t.country, "SE")
    
    def test_url_format(self):
        """Verify URLs are valid."""
        t = Tender(source="test", title="t", url="https://ted.europa.eu/test",
                   publication_date="d", deadline=None, 
                   description="d", estimated_value=None)
        self.assertTrue(t.url.startswith('https://'))

if __name__ == "__main__":
    # Run with -v for verbose output
    unittest.main(argv=[''], verbosity=2, exit=False)