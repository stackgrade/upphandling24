# Module 03: Database (Google Sheets)

## Overview
Google Sheets as a free database for storing signup data and user preferences.

## Architecture
```
Landing Page → Form Submit → Google Apps Script → Google Sheet
                                       ↑
Onboarding Page → Preferences → Google Apps Script → Google Sheet
```

## Setup Instructions

### 1. Create Google Sheet
1. Go to sheets.google.com
2. Create new spreadsheet named "TendAlert - Signups"
3. Add headers in row 1:
   - A: timestamp
   - B: email
   - C: company
   - D: phone
   - E: region
   - F: bransch (comma-separated)
   - G: frequency
   - H: keywords
   - I: source (landing/onboarding)

### 2. Create Google Apps Script
1. In the sheet, go to Extensions → Apps Script
2. Replace the default code with the contents of `apps_script.js`
3. Save the project
4. Click Deploy → New deployment
5. Select "Web app"
6. Set "Execute as" = Me
7. Set "Who has access" = Anyone
8. Copy the deployment URL

### 3. Update Form URLs
Replace `YOUR_GOOGLE_APPS_SCRIPT_URL` in:
- `submit_to_sheet.js`
- Landing page form handler
- Onboarding page form handler

## Files
- `apps_script.js` - Google Apps Script code (paste into Google Apps Script editor)
- `submit_to_sheet.js` - Client-side submission helper
- `sheet_config.js` - Configuration for sheet columns

## Sheet Structure
| Column | Field | Type |
|--------|-------|------|
| A | timestamp | ISO string |
| B | email | string |
| C | company | string |
| D | phone | string |
| E | region | string |
| F | bransch | comma-separated |
| G | frequency | instant/daily/weekly |
| H | keywords | string |
| I | source | landing/onboarding |
