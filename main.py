"""
Tender Monitoring SaaS - Main Integration
This file will orchestrate all modules once they are built.

For now, each module is independent and tested separately.
"""

# ============================================
# MODULE INTEGRATION STATUS
# ============================================
MODULE_STATUS = {
    "01_landing": "✅ COMPLETE - Bulletproof",
    "02_onboarding": "⏳ NOT STARTED",
    "03_database": "⏳ NOT STARTED",
    "04_scraper": "⏳ NOT STARTED",
    "05_filter": "⏳ NOT STARTED",
    "06_email": "⏳ NOT STARTED",
    "07_auth": "⏳ NOT STARTED",
}

# ============================================
# WHEN ALL MODULES ARE READY
# ============================================
def run_daily_pipeline():
    """
    Main daily workflow:
    1. Scrape all sources
    2. Store in database
    3. Filter for each customer
    4. Send email alerts
    """
    from modules import (
        scraper,
        database,
        filter_module,
        email_module
    )
    
    # Step 1: Fetch new tenders
    tenders = scraper.fetch_all()
    
    # Step 2: Store in database
    for tender in tenders:
        if not database.exists(tender):
            database.save(tender)
    
    # Step 3: For each customer, check for relevant tenders
    customers = database.get_all_customers()
    
    for customer in customers:
        relevant = filter_module.get_relevant_tenders(
            tender_id=database.get_tenders_since(customer.last_check),
            customer_profile=customer.profile
        )
        
        if relevant:
            email_module.send_alert(
                to=customer.email,
                tenders=relevant,
                customer_name=customer.name
            )
        
        # Update last check time
        database.update_last_check(customer.id)
    
    print(f"✅ Daily pipeline complete. Processed {len(tenders)} tenders.")

# ============================================
# CURRENT STATUS
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("Upphandling24 - Tender Monitoring SaaS")
    print("=" * 50)
    print()
    
    for module, status in MODULE_STATUS.items():
        print(f"  {module}: {status}")
    
    print()
    print("All modules must be bulletproof before integration.")
    print("Run: python -m pytest tests/")
