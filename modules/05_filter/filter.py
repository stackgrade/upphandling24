#!/usr/bin/env python3
"""
Module 05: AI Filter - Tender Matching
Uses Gemini to match tenders against customer preferences.
"""

import json
import time
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

@dataclass
class MatchResult:
    """Result of matching a tender against customer preferences."""
    tender_url: str
    tender_title: str
    relevance_score: float  # 0-1
    match_reasons: List[str]
    filter_reason: Optional[str] = None  # null if matched, string if filtered

class TenderFilter:
    """AI-powered tender matching using Gemini."""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.matches = []
        self.filtered_out = []
        
        if GEMINI_AVAILABLE and gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            # Try to use from config
            try:
                from config import GEMINI_API_KEY
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except:
                self.model = None
                print("⚠️ Gemini not configured - using simple keyword matching")
    
    def filter_tenders(self, tenders: List[dict], customer_profile: dict) -> List[dict]:
        """Filter and score tenders against customer preferences."""
        print(f"🔍 Filtering {len(tenders)} tenders for customer...")
        
        matched = []
        
        for tender in tenders:
            try:
                result = self._score_tender(tender, customer_profile)
                if result:
                    if result.filter_reason is None:
                        # Passed filter
                        matched.append(asdict(result))
                        print(f"  ✓ {tender.get('title', 'unknown')[:50]}... score={result.relevance_score:.2f}")
                    else:
                        # Filtered out
                        self.filtered_out.append(asdict(result))
            except Exception as e:
                print(f"  ✗ Error scoring tender: {e}")
                continue
        
        print(f"✅ Matched: {len(matched)}, Filtered: {len(self.filtered_out)}")
        return matched
    
    def _score_tender(self, tender: dict, profile: dict) -> Optional[MatchResult]:
        """Score a single tender against customer profile."""
        
        tender_url = tender.get('url', '')
        tender_title = tender.get('title', '')
        tender_desc = tender.get('description', '')[:300]
        tender_country = tender.get('country', '')
        tender_buyer = tender.get('buyer', '')[:100]
        
        # Customer preferences
        industries = profile.get('industries', [])
        regions = profile.get('regions', [])
        keywords_positive = profile.get('keywords_positive', [])
        keywords_negative = profile.get('keywords_negative', [])
        min_value = profile.get('min_value', 0)
        
        # Simple keyword matching as fallback
        if not self.model:
            score, reasons = self._simple_score(
                tender_title, tender_desc, tender_buyer,
                industries, keywords_positive, keywords_negative
            )
            filter_reason = None if score >= 0.5 else "Low relevance score"
            return MatchResult(
                tender_url=tender_url,
                tender_title=tender_title[:100],
                relevance_score=score,
                match_reasons=reasons,
                filter_reason=filter_reason
            )
        
        # Gemini AI scoring
        try:
            prompt = f"""Score this public procurement tender for a Swedish company.

TENDER:
- Title: {tender_title}
- Description: {tender_desc}
- Buyer: {tender_buyer}
- Country: {tender_country}

CUSTOMER PROFILE:
- Interested industries: {', '.join(industries) if industries else 'Any'}
- Preferred regions: {', '.join(regions) if regions else 'All EU'}
- Positive keywords: {', '.join(keywords_positive) if keywords_positive else 'None'}
- Negative keywords: {', '.join(keywords_negative) if keywords_negative else 'None'}
- Min contract value: {min_value} SEK

Score from 0 to 1 where:
- 0.9-1.0: Perfect match, high value, relevant industry
- 0.7-0.9: Good match, should send alert
- 0.5-0.7: Decent match, maybe relevant
- 0.0-0.5: Poor match, filter out

Respond ONLY with JSON:
{{"score": 0.85, "reasons": ["reason1", "reason2"], "should_send": true/false}}

Do not include any other text."""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON response
            if response_text.startswith('```'):
                response_text = response_text.strip('`').strip('json\n')
            
            result_data = json.loads(response_text)
            
            score = result_data.get('score', 0.5)
            reasons = result_data.get('reasons', [])
            should_send = result_data.get('should_send', True)
            
            return MatchResult(
                tender_url=tender_url,
                tender_title=tender_title[:100],
                relevance_score=score,
                match_reasons=reasons,
                filter_reason=None if should_send else "Below relevance threshold"
            )
            
        except Exception as e:
            print(f"  ⚠️ Gemini error: {e}, using fallback")
            score, reasons = self._simple_score(
                tender_title, tender_desc, tender_buyer,
                industries, keywords_positive, keywords_negative
            )
            return MatchResult(
                tender_url=tender_url,
                tender_title=tender_title[:100],
                relevance_score=score,
                match_reasons=reasons,
                filter_reason=None if score >= 0.5 else "Low relevance score"
            )
    
    def _simple_score(self, title: str, desc: str, buyer: str,
                     industries: List[str], pos_kw: List[str], neg_kw: List[str]) -> tuple:
        """Simple keyword-based scoring as fallback."""
        score = 0.5
        reasons = []
        
        text = f"{title} {desc} {buyer}".lower()
        
        # Positive keywords boost score
        for kw in pos_kw:
            if kw.lower() in text:
                score += 0.15
                reasons.append(f"Matches keyword: {kw}")
        
        # Negative keywords reduce score
        for kw in neg_kw:
            if kw.lower() in text:
                score -= 0.3
                reasons.append(f"Contains excluded: {kw}")
        
        # Industry match
        for ind in industries:
            if ind.lower() in text:
                score += 0.1
                reasons.append(f"Industry match: {ind}")
        
        # Clamp score
        score = max(0, min(1, score))
        
        return score, reasons


def main():
    """Main entry point for testing."""
    # Load tenders from cache
    cache_file = "/home/larry/projects/tender-system/data/tenders_cache.json"
    try:
        with open(cache_file) as f:
            tenders = json.load(f)
    except:
        print("❌ No tenders cache found - run scraper first")
        return []
    
    # Sample customer profile
    profile = {
        "industries": ["IT", "Software", "Consulting", "Construction"],
        "regions": ["SE", "DE", "DK"],
        "keywords_positive": ["IT services", "software development", "consulting"],
        "keywords_negative": ["military", "defense", "security"],
        "min_value": 50000
    }
    
    # Run filter
    filter_obj = TenderFilter()
    matches = filter_obj.filter_tenders(tenders, profile)
    
    print(f"\n📊 Results: {len(matches)} matched tenders")
    
    # Save matches
    import os
    os.makedirs("/home/larry/projects/tender-system/data", exist_ok=True)
    with open("/home/larry/projects/tender-system/data/matched_tenders.json", "w") as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    
    print("💾 Saved to data/matched_tenders.json")
    
    return matches

if __name__ == "__main__":
    main()