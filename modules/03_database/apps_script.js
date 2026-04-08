/**
 * TendAlert - Google Apps Script Web App
 * Handles form submissions and writes to Google Sheet
 * 
 * SETUP:
 * 1. Create new Google Sheet with headers in row 1:
 *    A: timestamp, B: email, C: company, D: phone, E: region, 
 *    F: bransch, G: frequency, H: keywords, I: source
 * 2. Extensions → Apps Script (or go to script.google.com)
 * 3. Paste this code
 * 4. Replace 'YOUR_SHEET_ID_HERE' with your spreadsheet ID
 * 5. Save (Ctrl+S)
 * 6. Deploy → New deployment → Web app
 * 7. Execute as: Me, Who has access: Anyone
 * 8. Copy the deployment URL
 */

// Configuration - REPLACE THIS WITH YOUR SPREADSHEET ID
const SHEET_ID = '1Wd4BwnV6s2LonuByKnPzewadwK1kypEL6Rqp65dHoxQ';
const SHEET_NAME = 'Sheet1';

// Main doPost handler (receives form data)
function doPost(e) {
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME);
    
    // Parse the incoming data
    let data;
    
    if (e.postData && e.postData.contents) {
      data = JSON.parse(e.postData.contents);
    } else if (e.parameter) {
      data = e.parameter;
    } else {
      throw new Error('No data received');
    }
    
    // Prepare row data
    const row = [
      data.timestamp || new Date().toISOString(),
      data.email || '',
      data.company || '',
      data.phone || '',
      data.region || '',
      Array.isArray(data.bransch) ? data.bransch.join(', ') : (data.bransch || ''),
      data.frequency || '',
      data.keywords || '',
      data.source || 'unknown'
    ];
    
    // Append to sheet
    sheet.appendRow(row);
    
    // Return success response
    return ContentService
      .createTextOutput(JSON.stringify({ 
        status: 'success', 
        message: 'Data saved to TendAlert spreadsheet' 
      }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    // Return error response
    return ContentService
      .createTextOutput(JSON.stringify({ 
        status: 'error', 
        message: error.toString() 
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Test function - add some sample data
function testAppend() {
  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME);
  
  const testRow = [
    new Date().toISOString(),
    'test@example.com',
    'Test Företag AB',
    '+46 70 123 4567',
    'stockholm',
    'bygg,it',
    'instant',
    'offentlig upphandling',
    'test'
  ];
  
  sheet.appendRow(testRow);
  Logger.log('Test row added to TendAlert spreadsheet');
}

// Simple GET handler for testing
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ 
      status: 'ok', 
      message: 'TendAlert API is running',
      spreadsheetId: SHEET_ID
    }))
    .setMimeType(ContentService.MimeType.JSON);
}
