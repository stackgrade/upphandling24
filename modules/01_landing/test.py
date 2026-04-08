"""
Test suite for Module 01: Landing Page
Run: python test.py
"""

import os
import sys
from pathlib import Path

def test_file_exists():
    """Test that landing page file exists"""
    assert (Path(__file__).parent / "index.html").exists(), "index.html missing"
    print("✅ index.html exists")

def test_html_valid_structure():
    """Test that HTML has required elements"""
    html = (Path(__file__).parent / "index.html").read_text()
    
    required = [
        "<form",
        'type="email"',
        'type="submit"',
        'id="signup-form"',
        'id="success-message"',
    ]
    
    for item in required:
        assert item in html, f"Missing required element: {item}"
    
    print("✅ HTML has all required form elements")

def test_has_svenska():
    """Test that page is in Swedish"""
    html = (Path(__file__).parent / "index.html").read_text()
    assert "Aldrig missa" in html, "Missing Swedish headline"
    assert "Upphandling" in html, "Missing Swedish content"
    print("✅ Page is in Swedish")

def test_form_fields():
    """Test form has all required fields"""
    html = (Path(__file__).parent / "index.html").read_text()
    
    fields = [
        'name="email"',
        'name="company"',
        'name="phone"',
        'name="bransch"',
        'name="region"',
    ]
    
    for field in fields:
        assert field in html, f"Missing form field: {field}"
    
    print("✅ All form fields present")

def test_mobile_responsive():
    """Test that page has mobile styling"""
    html = (Path(__file__).parent / "index.html").read_text()
    assert "@media" in html, "Missing media queries"
    print("✅ Page has mobile responsiveness")

def test_localStorage_usage():
    """Test that page saves to localStorage"""
    html = (Path(__file__).parent / "index.html").read_text()
    assert "localStorage" in html, "No localStorage usage"
    print("✅ Uses localStorage for demo storage")

if __name__ == "__main__":
    print("\n🧪 Testing Module 01: Landing Page\n")
    
    tests = [
        test_file_exists,
        test_html_valid_structure,
        test_has_svenska,
        test_form_fields,
        test_mobile_responsive,
        test_localStorage_usage,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✅ MODULE 01 IS BULLETPROOF!")
    else:
        print("\n⚠️ Some tests failed - needs fixing")
        sys.exit(1)
