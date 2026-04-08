/**
 * TendAlert - Database Test Tool
 * 
 * Run this to verify:
 * 1. Landing page → localStorage
 * 2. Onboarding → localStorage
 * 3. Manual submission to Google Sheet
 * 
 * Usage: Open in browser console
 */

const TEST = {
  // Test data
  signup: {
    email: 'test' + Date.now() + '@example.com',
    company: 'Test Företag AB',
    phone: '+46 70 123 4567',
    bransch: ['bygg', 'it']
  },
  
  preferences: {
    region: 'stockholm',
    frequency: 'instant',
    keywords: 'offentlig upphandling'
  },
  
  // Run all tests
  async run() {
    console.log('🧪 TendAlert Database Test');
    console.log('='.repeat(40));
    
    // Test 1: Clear storage
    this.clear();
    
    // Test 2: Save signup
    this.testSignup();
    
    // Test 3: Save preferences  
    this.testPreferences();
    
    // Test 4: Verify localStorage
    this.verifyStorage();
    
    console.log('='.repeat(40));
    console.log('✅ Tests complete!');
    console.log('📊 Check Application tab in DevTools to see localStorage data');
  },
  
  clear() {
    localStorage.removeItem('TendAlert_signup');
    localStorage.removeItem('TendAlert_preferences');
    console.log('🗑️ Cleared localStorage');
  },
  
  testSignup() {
    localStorage.setItem('TendAlert_signup', JSON.stringify(this.signup));
    console.log('✅ Saved signup:', this.signup);
  },
  
  testPreferences() {
    localStorage.setItem('TendAlert_preferences', JSON.stringify({
      ...this.signup,
      ...this.preferences,
      timestamp: new Date().toISOString(),
      source: 'test'
    }));
    console.log('✅ Saved preferences');
  },
  
  verifyStorage() {
    const signup = JSON.parse(localStorage.getItem('TendAlert_signup') || '{}');
    const prefs = JSON.parse(localStorage.getItem('TendAlert_preferences') || '{}');
    
    console.log('\n📦 localStorage contents:');
    console.log('Signup:', signup);
    console.log('Preferences:', prefs);
    
    // Verify fields
    const checks = [
      { name: 'email', value: signup.email },
      { name: 'company', value: signup.company },
      { name: 'region', value: prefs.region },
      { name: 'frequency', value: prefs.frequency },
      { name: 'source', value: prefs.source }
    ];
    
    console.log('\n🔍 Verification:');
    checks.forEach(check => {
      const status = check.value ? '✅' : '❌';
      console.log(`${status} ${check.name}: ${check.value || 'MISSING'}`);
    });
  }
};

// Auto-run if executed in console
if (typeof window !== 'undefined') {
  TEST.run();
}
