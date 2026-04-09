#!/usr/bin/env python3
"""
DEMO: Full customer flow simulation
Shows how TendAlert works end-to-end with a fake customer.
"""

import json
import sys
import os

# Fake customer profile
DEMO_CUSTOMER = {
    "name": "Erik Lindström",
    "email": "erik.bygg@villafi.se", 
    "company": "Lindström Bygg AB",
    "industries": ["Construction", "Building", "Renovation"],
    "regions": ["SE", "DK", "NO"],
    "keywords_positive": ["construction", "building", "renovation"],
    "keywords_negative": ["military", "defense", "IT services"],
    "min_value": 100000
}

def match_tender(tender, profile):
    """Simple keyword matching like our filter."""
    score = 0.3
    reasons = []
    text = f"{tender.get('title', '')} {tender.get('description', '')}".lower()
    
    for ind in profile['industries']:
        if ind.lower() in text:
            score += 0.25
            reasons.append(f"Bransch: {ind}")
    
    for kw in profile['keywords_positive']:
        if kw.lower() in text:
            score += 0.15
            reasons.append(f"Keyword: {kw}")
    
    for kw in profile['keywords_negative']:
        if kw.lower() in text:
            score -= 0.3
    
    if tender.get('country') in profile['regions']:
        score += 0.1
    
    score = max(0, min(1, score))
    return score, reasons

def run_demo():
    print("=" * 60)
    print("TENDALERT DEMO - Full Customer Flow")
    print("=" * 60)
    
    print(f"\n📝 STEG 1: {DEMO_CUSTOMER['name']} anmäler sig")
    print(f"   Företag: {DEMO_CUSTOMER['company']}")
    print(f"   Branscher: {', '.join(DEMO_CUSTOMER['industries'])}")
    
    # Load tenders
    with open("/home/larry/projects/tender-system/data/tenders_cache.json") as f:
        tenders = json.load(f)
    
    print(f"\n🔍 STEG 2: Matchar {len(tenders)} tendrar...")
    
    matched = []
    for t in tenders:
        score, reasons = match_tender(t, DEMO_CUSTOMER)
        if score >= 0.4:
            matched.append({
                'tender_title': t.get('title', '')[:80],
                'tender_url': t.get('url', ''),
                'relevance_score': score,
                'match_reasons': reasons,
                'country': t.get('country', ''),
                'buyer': t.get('buyer', 'N/A')
            })
    
    matched.sort(key=lambda x: x['relevance_score'], reverse=True)
    print(f"   Matchade: {len(matched)} tendrar")
    
    print(f"\n📋 STEG 3: Top 5:")
    for i, t in enumerate(matched[:5], 1):
        print(f"\n   {i}. [{t['country']}] {t['tender_title']}")
        print(f"      Match: {int(t['relevance_score']*100)}% | {', '.join(t['match_reasons'][:2])}")
    
    # Save matched to file for email_sender.py to use
    demo_dir = "/home/larry/projects/tender-system/data/demo_emails"
    os.makedirs(demo_dir, exist_ok=True)
    
    with open("/home/larry/projects/tender-system/data/matched_demo.json", "w") as f:
        json.dump(matched[:10], f, ensure_ascii=False, indent=2)
    
    print(f"\n📧 STEG 4: Skapar email...")
    
    # Run email sender
    os.system("cd /home/larry/projects/tender-system/modules/06_email && python3 email_sender.py 2>&1 | head -10")
    
    print(f"\n✅ DEMO KLAR!")
    print(f"   Erik fick {len(matched)} matchande tendrar")
    print(f"   Email sparad i demo_emails/")
    print(f"\n🎯 Nästa: Alexor fixar SMTP så vi kan skicka på riktigt!")

if __name__ == "__main__":
    run_demo()