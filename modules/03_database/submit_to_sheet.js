/**
 * TendAlert - Submit to Google Sheet
 * Client-side helper to submit form data to Google Apps Script
 * 
 * USAGE:
 * Replace YOUR_GOOGLE_APPS_SCRIPT_URL with your deployed Apps Script URL
 */

const CONFIG = {
  // TODO: Replace with your Google Apps Script Web App URL
  APPS_SCRIPT_URL: 'YOUR_GOOGLE_APPS_SCRIPT_URL_HERE'
};

/**
 * Submit signup data to Google Sheet
 * @param {Object} data - Form data
 * @returns {Promise<Object>} - Response from server
 */
async function submitToSheet(data) {
  // Add timestamp if not present
  if (!data.timestamp) {
    data.timestamp = new Date().toISOString();
  }
  
  try {
    const response = await fetch(CONFIG.APPS_SCRIPT_URL, {
      method: 'POST',
      mode: 'no-cors', // Required for Google Apps Script
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });
    
    // Note: with no-cors, we can't read the response
    // But the request is still made successfully
    return { status: 'success', message: 'Data submitted' };
    
  } catch (error) {
    console.error('Submit error:', error);
    return { status: 'error', message: error.toString() };
  }
}

/**
 * Submit signup data (landing page)
 * @param {string} email
 * @param {string} company
 * @param {string} phone
 * @param {string[]} bransch
 */
async function submitSignup(email, company, phone, bransch) {
  return submitToSheet({
    email,
    company,
    phone,
    bransch,
    source: 'landing'
  });
}

/**
 * Submit preferences (onboarding page)
 * @param {Object} preferences
 */
async function submitPreferences(preferences) {
  return submitToSheet({
    ...preferences,
    source: 'onboarding'
  });
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
  window.TendAlert = window.TendAlert || {};
  window.TendAlert.submitToSheet = submitToSheet;
  window.TendAlert.submitSignup = submitSignup;
  window.TendAlert.submitPreferences = submitPreferences;
}
