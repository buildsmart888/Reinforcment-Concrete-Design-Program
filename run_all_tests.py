#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Runner for RC Beam Calculator
Comprehensive test suite runner with coverage reporting
"""

import unittest
import sys
import os
import time
import importlib.util
from io import StringIO

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test file imports
test_modules = [
    'test_beam_calculations',
    'test_gui_components', 
    'test_integration_scenarios',
    'test_edge_cases'
]

class TestResult:
    """Custom test result class for detailed reporting"""
    
    def __init__(self):
        self.total_tests = 0
        self.successful_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.skipped_tests = 0
        self.test_details = {}
        self.module_results = {}
        
    def add_module_result(self, module_name, result):
        """Add test result for a module"""
        self.module_results[module_name] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
            'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
        }
        
        self.total_tests += result.testsRun
        self.successful_tests += (result.testsRun - len(result.failures) - len(result.errors))
        self.failed_tests += len(result.failures)
        self.error_tests += len(result.errors)
        if hasattr(result, 'skipped'):
            self.skipped_tests += len(result.skipped)


def run_test_module(module_name):
    """Run tests for a specific module"""
    print(f"\n{'='*60}")
    print(f"Running tests for: {module_name}")
    print(f"{'='*60}")
    
    try:
        # Import the test module
        module = importlib.import_module(module_name)
        
        # Create test suite for this module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        # Run tests with custom runner
        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)
        
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # Print results
        print(f"Tests completed in {end_time - start_time:.2f} seconds")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if hasattr(result, 'skipped'):
            print(f"Skipped: {len(result.skipped)}")
            
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        
        # Print failure details if any
        if result.failures:
            print(f"\n❌ FAILURES ({len(result.failures)}):")
            for i, (test, traceback) in enumerate(result.failures, 1):
                print(f"  {i}. {test}")
                # Print only the assertion error message
                lines = traceback.split('\n')
                for line in lines:
                    if 'AssertionError' in line:
                        print(f"     {line.strip()}")
                        break
                        
        # Print error details if any
        if result.errors:
            print(f"\n💥 ERRORS ({len(result.errors)}):")
            for i, (test, traceback) in enumerate(result.errors, 1):
                print(f"  {i}. {test}")
                # Print the error message
                lines = traceback.split('\n')
                for line in lines:
                    if 'Error:' in line or 'Exception:' in line:
                        print(f"     {line.strip()}")
                        break
                        
        return result
        
    except ImportError as e:
        print(f"❌ Could not import test module '{module_name}': {e}")
        return None
    except Exception as e:
        print(f"❌ Error running tests for '{module_name}': {e}")
        return None


def print_overall_summary(test_result):
    """Print overall test summary"""
    print(f"\n{'='*80}")
    print(f"🧪 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*80}")
    
    # Overall statistics
    print(f"📊 OVERALL STATISTICS:")
    print(f"   Total Tests: {test_result.total_tests}")
    print(f"   ✅ Successful: {test_result.successful_tests}")
    print(f"   ❌ Failed: {test_result.failed_tests}")
    print(f"   💥 Errors: {test_result.error_tests}")
    if test_result.skipped_tests > 0:
        print(f"   ⏭️  Skipped: {test_result.skipped_tests}")
    
    overall_success_rate = (test_result.successful_tests / test_result.total_tests * 100) if test_result.total_tests > 0 else 0
    print(f"   🎯 Overall Success Rate: {overall_success_rate:.1f}%")
    
    # Module breakdown
    print(f"\n📋 MODULE BREAKDOWN:")
    for module_name, module_result in test_result.module_results.items():
        status_icon = "✅" if module_result['failures'] == 0 and module_result['errors'] == 0 else "❌"
        print(f"   {status_icon} {module_name}:")
        print(f"      Tests: {module_result['tests_run']}")
        print(f"      Success Rate: {module_result['success_rate']:.1f}%")
        if module_result['failures'] > 0:
            print(f"      Failures: {module_result['failures']}")
        if module_result['errors'] > 0:
            print(f"      Errors: {module_result['errors']}")
    
    # Test coverage assessment
    print(f"\n🎯 TEST COVERAGE ASSESSMENT:")
    coverage_categories = {
        'Core Calculations': test_result.module_results.get('test_beam_calculations', {}).get('success_rate', 0),
        'GUI Components': test_result.module_results.get('test_gui_components', {}).get('success_rate', 0), 
        'Integration Scenarios': test_result.module_results.get('test_integration_scenarios', {}).get('success_rate', 0),
        'Edge Cases': test_result.module_results.get('test_edge_cases', {}).get('success_rate', 0)
    }
    
    for category, success_rate in coverage_categories.items():
        status = "🟢" if success_rate >= 90 else "🟡" if success_rate >= 70 else "🔴"
        print(f"   {status} {category}: {success_rate:.1f}%")
    
    # Quality assessment
    print(f"\n🏆 QUALITY ASSESSMENT:")
    if overall_success_rate >= 95:
        quality = "🥇 EXCELLENT - Production Ready"
    elif overall_success_rate >= 85:
        quality = "🥈 GOOD - Minor Issues to Address"
    elif overall_success_rate >= 70:
        quality = "🥉 FAIR - Significant Issues Need Attention"
    else:
        quality = "🔴 POOR - Major Issues Must Be Fixed"
    
    print(f"   {quality}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if test_result.failed_tests > 0:
        print(f"   • Fix {test_result.failed_tests} failing test(s)")
    if test_result.error_tests > 0:
        print(f"   • Resolve {test_result.error_tests} error(s)")
    if overall_success_rate < 90:
        print(f"   • Improve test coverage and fix issues to reach 90%+ success rate")
    if overall_success_rate >= 95:
        print(f"   • Excellent test coverage! Consider adding edge case tests")
    
    print(f"{'='*80}")


def main():
    """Main test runner function"""
    print("🚀 RC Beam Calculator - Comprehensive Test Suite")
    print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_result = TestResult()
    start_time = time.time()
    
    # Run tests for each module
    for module_name in test_modules:
        result = run_test_module(module_name)
        if result:
            test_result.add_module_result(module_name, result)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Print overall summary
    print_overall_summary(test_result)
    
    print(f"\n⏱️  Total execution time: {total_time:.2f} seconds")
    print(f"🏁 Testing completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return exit code based on test results
    return 0 if (test_result.failed_tests == 0 and test_result.error_tests == 0) else 1


if __name__ == '__main__':
    # Check if we're running individual test modules or the full suite
    if len(sys.argv) > 1:
        # Run specific test module
        module_name = sys.argv[1]
        if module_name in test_modules:
            result = run_test_module(module_name)
            sys.exit(0 if result and result.wasSuccessful() else 1)
        else:
            print(f"❌ Unknown test module: {module_name}")
            print(f"Available modules: {', '.join(test_modules)}")
            sys.exit(1)
    else:
        # Run full test suite
        sys.exit(main())
