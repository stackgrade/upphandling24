# Module 05: AI Filter - Tender Matching

## Purpose
Match scraped tenders against customer preferences using AI (Gemini).
Output: Relevance score (0-1) and ranked list of matching tenders.

## Input
- Customer preferences: industries, regions, keywords, budget ranges
- Tender data from Module 04

## Output Format
```python
{
    "tender_id": "url_hash",
    "tender_url": "string",
    "relevance_score": 0.85,  # 0-1
    "match_reasons": ["keyword X matches", "industry Y relevant"],
    "filter_reason": "Too general - no specific match" or None  # null if matched
}
```

## Technical Approach
- Gemini Flash for fast scoring
- Batch processing (1500 requests/day free tier)
- Compare tender fields against customer profile
- Store results for email module (Module 06)

## Files
- filter.py - Main matching logic with Gemini
- config.yaml - Filter thresholds and weights
- test_filter.py - Test suite

## Status
⏳ In Progress