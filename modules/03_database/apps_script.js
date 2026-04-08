/**
 * TendAlert - Google Apps Script Web App
 * Handles form submissions and writes to Google Sheet
 * 
 * SETUP:
 * 1. Create new Google Sheet with headers in row 1:
 *    A: timestamp, B: email, C: company, D: phone, E: region, 
 *    F: bransch, G: frequency, H: keywords, I: source
 * 2. Extensions → Apps Script
 * 3. Paste this code
 * 4. Deploy → New deployment → Web app
 * 5. Execute as: Me, Who has access: Anyone
 * 6. Copy URL
 */

// Configuration
const SHEET_NAME = 'Sheet1';

// Main doPost handler (receives form data)
function doPost(e) {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    
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
        message: 'Data saved' 
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
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  
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
  Logger.log('Test row added');
}

// Manual setup function to add headers
function setupHeaders() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  
  const headers = [
    'timestamp',
    'email',
    'company',
    'phone',
    'region',
    'bransch',
    'frequency',
    'keywords',
    'source'
  ];
  
  // Clear existing and add headers
  sheet.clear();
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  
  // Format headers
  sheet.getRange(1, 1, 1, headers.length)
    .setFontWeight('bold')
    .setBackground('#1e3a5f')
    .setFontColor('white');
  
  // Set column widths
  sheet.setColumnWidth(1, 180); // timestamp
  sheet.setColumnWidth(2, 200); // email
  sheet.setColumnWidth(3, 150); // company
  sheet.setColumnWidth(4, 140); // phone
  sheet.setColumnWidth(5, 120); // region
  sheet.setColumnWidth(6, 200); // bransch
  sheet.setColumnWidth(7, 80);  // frequency
  sheet.setColumnWidth(8, 200); // keywords
  sheet.setColumnWidth(9, 100); // source
  
  Logger.log('Headers set up successfully');
}

// Get all signups (for admin/dashboard)
function getAllSignups() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  const data = sheet.getDataRange().getValues();
  
  // Skip header row
  return data.slice(1).map(row => ({
    timestamp: row[0],
    email: row[1],
    company: row[2],
    phone: row[3],
    region: row[4],
    bransch: row[5],
    frequency: row[6],
    keywords: row[7],
    source: row[8]
  }));
}

// Simple GET handler for testing
function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ 
      status: 'ok', 
      message: 'TendAlert API is running',
      signups: getAllSignups().length
    }))
    .setMimeType(ContentService.MimeType.JSON);
}
