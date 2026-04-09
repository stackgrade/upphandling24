#!/bin/bash
# TendAlert Scraper Runner
# Runs tender scrape → filter → (email when ready)
# Add to crontab: 0 6 * * * /home/larry/projects/tender-system/run_scraper.sh

PROJECT_DIR="/home/larry/projects/tender-system"
LOG_FILE="$PROJECT_DIR/logs/scraper.log"

mkdir -p "$PROJECT_DIR/logs"

echo "=== $(date) - Starting TendAlert scrape ===" >> "$LOG_FILE"

# Run scraper
cd "$PROJECT_DIR/modules/04_scraper"
python3 scraper.py >> "$LOG_FILE" 2>&1

# Run filter
cd "$PROJECT_DIR/modules/05_filter"  
python3 filter.py >> "$LOG_FILE" 2>&1

echo "=== $(date) - Done ===" >> "$LOG_FILE"