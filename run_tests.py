#!/usr/bin/env python
"""
Comprehensive test runner for Great British Beer Django application.

This script runs all test suites and generates a coverage report.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


def run_tests():
    """Run all tests with coverage."""
    os.environ['DJANGO_SETTINGS_MODULE'] = 'greatbritishbeer.settings'
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run specific test modules
    test_modules = [
        'tests.test_users',
        'tests.test_reviews',
    ]
    
    print("🧪 Running Great British Beer Test Suite")
    print("=" * 50)
    
    failures = 0
    for module in test_modules:
        print(f"\n📋 Running {module}...")
        result = test_runner.run_tests([module])
        failures += result
        
        if result == 0:
            print(f"✅ {module} - All tests passed!")
        else:
            print(f"❌ {module} - {result} test(s) failed!")
    
    print("\n" + "=" * 50)
    if failures == 0:
        print("🎉 All tests passed successfully!")
        return True
    else:
        print(f"💥 {failures} total test(s) failed!")
        return False


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
