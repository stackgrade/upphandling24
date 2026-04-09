#!/usr/bin/env python3
"""
Test suite for Module 05: AI Filter
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from filter import TenderFilter, MatchResult

class TestFilter(unittest.TestCase):
    
    def setUp(self):
        self.filter = TenderFilter()
        self.sample_tender = {
            "url": "https://ted.europa.eu/test",
            "title": "IT Services for Government Agency",
            "description": "Software development and consulting services for Swedish public sector",
            "country": "SE",
            "buyer": "Swedish Government Office"
        }
        self.sample_profile = {
            "industries": ["IT", "Software", "Consulting"],
            "regions": ["SE", "DE"],
            "keywords_positive": ["IT", "software", "consulting"],
            "keywords_negative": ["military", "defense"],
            "min_value": 50000
        }
    
    def test_match_result_creation(self):
        """Test MatchResult dataclass."""
        result = MatchResult(
            tender_url="https://example.com",
            tender_title="Test Tender",
            relevance_score=0.85,
            match_reasons=["Industry match", "Keyword match"],
            filter_reason=None
        )
        self.assertEqual(result.relevance_score, 0.85)
        self.assertIsNone(result.filter_reason)
    
    def test_filter_reason_when_filtered(self):
        """Test that filter_reason is set when filtered."""
        result = MatchResult(
            tender_url="https://example.com",
            tender_title="Test Tender",
            relevance_score=0.3,
            match_reasons=[],
            filter_reason="Below relevance threshold"
        )
        self.assertIsNotNone(result.filter_reason)
    
    def test_simple_scoring(self):
        """Test simple keyword scoring."""
        score, reasons = self.filter._simple_score(
            self.sample_tender["title"],
            self.sample_tender["description"],
            self.sample_tender["buyer"],
            self.sample_profile["industries"],
            self.sample_profile["keywords_positive"],
            self.sample_profile["keywords_negative"]
        )
        self.assertGreater(score, 0.5)
        self.assertGreater(len(reasons), 0)
    
    def test_negative_keywords(self):
        """Test that negative keywords reduce score."""
        tender_bad = {
            "title": "Military defense IT system",
            "description": "Defense contractor services",
            "buyer": "Defense Ministry"
        }
        score, reasons = self.filter._simple_score(
            tender_bad["title"],
            tender_bad["description"],
            tender_bad["buyer"],
            self.sample_profile["industries"],
            self.sample_profile["keywords_positive"],
            self.sample_profile["keywords_negative"]
        )
        self.assertLess(score, 0.5)

class TestFilterIntegration(unittest.TestCase):
    
    def test_filter_tenders_returns_list(self):
        """Test that filter_tenders returns a list."""
        filter_obj = TenderFilter()
        tenders = [
            {"url": "https://test.com/1", "title": "IT Services", "description": "IT consulting"},
            {"url": "https://test.com/2", "title": "Building Work", "description": "Construction"},
        ]
        profile = {"industries": ["IT"], "regions": [], "keywords_positive": [], "keywords_negative": [], "min_value": 0}
        results = filter_obj.filter_tenders(tenders, profile)
        self.assertIsInstance(results, list)

if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2)