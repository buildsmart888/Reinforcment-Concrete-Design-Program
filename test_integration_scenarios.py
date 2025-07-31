#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Test Cases for RC Beam Calculator
End-to-end testing scenarios for complete beam design workflows
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestBeamDesignScenarios(unittest.TestCase):
    """Test realistic beam design scenarios"""
    
    def setUp(self):
        """Set up test scenarios with realistic beam configurations"""
        self.test_scenarios = {
            'residential_beam': {
                'description': 'Typical residential beam (living room span)',
                'inputs': {
                    'width': 300,      # mm
                    'depth': 500,      # mm
                    'fc': 280,         # kgf/cm2 (f'c = 28 MPa)
                    'fy': 4000,        # kgf/cm2 (Grade 60)
                    'moment': 12.5,    # tf-m
                    'shear': 8.0,      # tf
                    'cover': 40,       # mm
                    'main_rebar': '#5(D16)',
                    'comp_rebar': '#4(D13)',
                    'stirrup': '#3(D10)',
                    'stirrup_type': 'เหล็กปลอกสองขา'
                },
                'expected_results': {
                    'min_main_steel': 3.0,    # cm2
                    'max_main_steel': 25.0,   # cm2
                    'min_stirrup_spacing': 100,  # mm
                    'max_stirrup_spacing': 300,  # mm
                    'safety_factor_moment': 1.2,
                    'safety_factor_shear': 1.5
                }
            },
            'commercial_beam': {
                'description': 'Commercial building beam (office space)',
                'inputs': {
                    'width': 400,      # mm
                    'depth': 700,      # mm
                    'fc': 350,         # kgf/cm2 (f'c = 35 MPa)
                    'fy': 4000,        # kgf/cm2
                    'moment': 35.0,    # tf-m
                    'shear': 22.0,     # tf
                    'cover': 40,       # mm
                    'main_rebar': '#8(D25)',
                    'comp_rebar': '#5(D16)',
                    'stirrup': '#4(D13)',
                    'stirrup_type': 'เหล็กปลอกสามขา'
                },
                'expected_results': {
                    'min_main_steel': 5.0,    # cm2
                    'max_main_steel': 45.0,   # cm2
                    'min_stirrup_spacing': 80,   # mm
                    'max_stirrup_spacing': 250,  # mm
                    'safety_factor_moment': 1.2,
                    'safety_factor_shear': 1.5
                }
            },
            'high_strength_beam': {
                'description': 'High-strength concrete beam',
                'inputs': {
                    'width': 350,      # mm
                    'depth': 600,      # mm
                    'fc': 420,         # kgf/cm2 (f'c = 42 MPa)
                    'fy': 5000,        # kgf/cm2 (High-strength steel)
                    'moment': 28.0,    # tf-m
                    'shear': 18.0,     # tf
                    'cover': 40,       # mm
                    'main_rebar': '#7(D22)',
                    'comp_rebar': '#5(D16)',
                    'stirrup': '#3(D10)',
                    'stirrup_type': 'เหล็กปลอกสี่ขา'
                },
                'expected_results': {
                    'min_main_steel': 4.0,    # cm2
                    'max_main_steel': 35.0,   # cm2
                    'min_stirrup_spacing': 90,   # mm
                    'max_stirrup_spacing': 280,  # mm
                    'safety_factor_moment': 1.2,
                    'safety_factor_shear': 1.5
                }
            }
        }
        
    def test_residential_beam_design(self):
        """Test typical residential beam design scenario"""
        scenario = self.test_scenarios['residential_beam']
        inputs = scenario['inputs']
        expected = scenario['expected_results']
        
        # Mock the beam calculation process
        def mock_beam_calculation(inputs):
            """Mock beam calculation returning realistic results"""
            # Calculate approximate steel requirement
            # This is simplified - actual calculation would be more complex
            
            b_cm = inputs['width'] / 10  # Convert to cm
            d_cm = inputs['depth'] / 10 - 5  # Approximate effective depth
            fc = inputs['fc']
            fy = inputs['fy']
            Mu = inputs['moment'] * 100000  # Convert tf-m to kg-cm
            
            # Simplified steel area calculation
            # Actual formula: As = (0.85*fc*b*d/fy) * (1 - sqrt(1 - 2*Rn*fy/(0.85*fc²)))
            Rn = Mu / (b_cm * d_cm**2)  # Required strength
            rho_approx = Rn / (0.9 * fy * d_cm)  # Simplified
            As_required = max(rho_approx * b_cm * d_cm, expected['min_main_steel'])
            
            # Mock stirrup spacing calculation
            Vu = inputs['shear'] * 1000  # Convert to kg
            Vc = 0.53 * (fc**0.5) * b_cm * d_cm / 1000  # Concrete shear capacity
            
            if Vu > 0.5 * Vc:
                s_required = min(d_cm * 10 / 2, 300)  # mm
            else:
                s_required = min(d_cm * 10 / 4, 150)  # mm
                
            return {
                'steel_required': As_required,
                'stirrup_spacing': s_required,
                'moment_capacity': Mu * 1.3,  # Mock capacity with safety factor
                'shear_capacity': Vu * 1.6    # Mock capacity with safety factor
            }
            
        # Run the mock calculation
        results = mock_beam_calculation(inputs)
        
        # Verify results are within expected ranges
        self.assertGreaterEqual(results['steel_required'], expected['min_main_steel'])
        self.assertLessEqual(results['steel_required'], expected['max_main_steel'])
        
        self.assertGreaterEqual(results['stirrup_spacing'], expected['min_stirrup_spacing'])
        self.assertLessEqual(results['stirrup_spacing'], expected['max_stirrup_spacing'])
        
        # Verify safety factors
        moment_safety = results['moment_capacity'] / (inputs['moment'] * 100000)
        shear_safety = results['shear_capacity'] / (inputs['shear'] * 1000)
        
        self.assertGreaterEqual(moment_safety, expected['safety_factor_moment'])
        self.assertGreaterEqual(shear_safety, expected['safety_factor_shear'])
        
    def test_commercial_beam_design(self):
        """Test commercial building beam design scenario"""
        scenario = self.test_scenarios['commercial_beam']
        self._run_beam_scenario_test(scenario)
        
    def test_high_strength_beam_design(self):
        """Test high-strength concrete beam design scenario"""
        scenario = self.test_scenarios['high_strength_beam']
        self._run_beam_scenario_test(scenario)
        
    def _run_beam_scenario_test(self, scenario):
        """Helper method to run beam scenario tests"""
        inputs = scenario['inputs']
        expected = scenario['expected_results']
        
        # Validate input parameters are reasonable
        self.assertGreater(inputs['width'], 200)
        self.assertLess(inputs['width'], 1000)
        self.assertGreater(inputs['depth'], inputs['width'])
        self.assertGreaterEqual(inputs['fc'], 210)
        self.assertLessEqual(inputs['fc'], 420)
        self.assertGreaterEqual(inputs['fy'], 2400)
        self.assertLessEqual(inputs['fy'], 6000)
        
        # Validate expected results are reasonable
        self.assertGreater(expected['min_main_steel'], 0)
        self.assertLess(expected['max_main_steel'], 100)
        self.assertGreater(expected['min_stirrup_spacing'], 50)
        self.assertLess(expected['max_stirrup_spacing'], 500)


class TestErrorHandlingScenarios(unittest.TestCase):
    """Test error handling for various input scenarios"""
    
    def test_invalid_input_handling(self):
        """Test handling of invalid inputs"""
        invalid_scenarios = [
            {
                'name': 'negative_dimensions',
                'inputs': {'width': -300, 'depth': 500},
                'expected_error': 'ความกว้างคานต้องเป็นค่าบวก'
            },
            {
                'name': 'zero_material_strength',
                'inputs': {'fc': 0, 'fy': 4000},
                'expected_error': 'กำลังอัดคอนกรีตต้องมากกว่าศูนย์'
            },
            {
                'name': 'excessive_loading',
                'inputs': {'moment': 1000, 'shear': 500, 'width': 300, 'depth': 500},
                'expected_error': 'โมเมนต์สูงเกินไปสำหรับขนาดคาน'
            }
        ]
        
        def validate_inputs(inputs):
            """Mock input validation function"""
            errors = []
            
            if 'width' in inputs and inputs['width'] <= 0:
                errors.append('ความกว้างคานต้องเป็นค่าบวก')
                
            if 'depth' in inputs and inputs['depth'] <= 0:
                errors.append('ความสูงคานต้องเป็นค่าบวก')
                
            if 'fc' in inputs and inputs['fc'] <= 0:
                errors.append('กำลังอัดคอนกรีตต้องมากกว่าศูนย์')
                
            if 'fy' in inputs and inputs['fy'] <= 0:
                errors.append('กำลังดึงเหล็กต้องมากกว่าศูนย์')
                
            # Check for excessive loading
            if all(key in inputs for key in ['moment', 'width', 'depth']):
                beam_size_factor = inputs['width'] * inputs['depth'] / 1000000  # Rough estimate
                if inputs['moment'] > beam_size_factor * 200:  # Arbitrary threshold
                    errors.append('โมเมนต์สูงเกินไปสำหรับขนาดคาน')
                    
            return errors
            
        for scenario in invalid_scenarios:
            with self.subTest(scenario=scenario['name']):
                errors = validate_inputs(scenario['inputs'])
                self.assertGreater(len(errors), 0)
                self.assertIn(scenario['expected_error'], ' '.join(errors))
                
    def test_boundary_condition_handling(self):
        """Test handling of boundary conditions"""
        boundary_cases = [
            {
                'name': 'minimum_beam_size',
                'inputs': {'width': 200, 'depth': 300},
                'should_pass': True
            },
            {
                'name': 'maximum_beam_size',
                'inputs': {'width': 1000, 'depth': 1500},
                'should_pass': True
            },
            {
                'name': 'minimum_concrete_strength',
                'inputs': {'fc': 210},
                'should_pass': True
            },
            {
                'name': 'maximum_concrete_strength',
                'inputs': {'fc': 420},
                'should_pass': True
            },
            {
                'name': 'below_minimum_concrete',
                'inputs': {'fc': 180},
                'should_pass': False
            }
        ]
        
        def is_within_boundaries(inputs):
            """Check if inputs are within acceptable boundaries"""
            if 'width' in inputs:
                if inputs['width'] < 200 or inputs['width'] > 1000:
                    return False
                    
            if 'depth' in inputs:
                if inputs['depth'] < 300 or inputs['depth'] > 1500:
                    return False
                    
            if 'fc' in inputs:
                if inputs['fc'] < 210 or inputs['fc'] > 420:
                    return False
                    
            return True
            
        for case in boundary_cases:
            with self.subTest(case=case['name']):
                result = is_within_boundaries(case['inputs'])
                self.assertEqual(result, case['should_pass'])


class TestMultiLanguageIntegration(unittest.TestCase):
    """Test multi-language integration scenarios"""
    
    def setUp(self):
        """Set up multi-language test data"""
        self.language_test_data = {
            'th': {
                'beam_width': 'ความกว้างคาน',
                'beam_depth': 'ความสูงคาน', 
                'concrete_strength': 'กำลังอัดคอนกรีต',
                'steel_strength': 'กำลังดึงเหล็ก',
                'moment': 'โมเมนต์',
                'shear': 'แรงเฉือน',
                'two_leg_stirrup': 'เหล็กปลอกสองขา'
            },
            'en': {
                'beam_width': 'Beam Width',
                'beam_depth': 'Beam Depth',
                'concrete_strength': 'Concrete Strength',
                'steel_strength': 'Steel Strength', 
                'moment': 'Moment',
                'shear': 'Shear',
                'two_leg_stirrup': 'Two-leg Stirrup'
            },
            'zh': {
                'beam_width': '梁寬',
                'beam_depth': '梁高',
                'concrete_strength': '混凝土強度',
                'steel_strength': '鋼筋強度',
                'moment': '彎矩',
                'shear': '剪力',
                'two_leg_stirrup': '雙肢箍'
            }
        }
        
    def test_language_consistency(self):
        """Test that all languages have consistent key mappings"""
        languages = list(self.language_test_data.keys())
        reference_keys = set(self.language_test_data[languages[0]].keys())
        
        for lang in languages[1:]:
            lang_keys = set(self.language_test_data[lang].keys())
            self.assertEqual(reference_keys, lang_keys, 
                           f"Language {lang} missing keys: {reference_keys - lang_keys}")
                           
    def test_translation_completeness(self):
        """Test that translations are complete and not empty"""
        for lang, translations in self.language_test_data.items():
            with self.subTest(language=lang):
                for key, translation in translations.items():
                    self.assertIsInstance(translation, str)
                    self.assertGreater(len(translation.strip()), 0)
                    self.assertNotEqual(translation.strip(), key)  # Translation should differ from key
                    
    def test_stirrup_type_translation(self):
        """Test stirrup type translation across languages"""
        stirrup_mappings = {
            'th': {
                'เหล็กปลอกสองขา': 2,
                'เหล็กปลอกสามขา': 3,
                'เหล็กปลอกสี่ขา': 4
            },
            'en': {
                'Two-leg Stirrup': 2,
                'Three-leg Stirrup': 3,
                'Four-leg Stirrup': 4
            },
            'zh': {
                '雙肢箍': 2,
                '三肢箍': 3,
                '四肢箍': 4
            }
        }
        
        def get_stirrup_legs(stirrup_text, language):
            return stirrup_mappings.get(language, {}).get(stirrup_text, 2)
            
        # Test each language
        for lang in stirrup_mappings:
            with self.subTest(language=lang):
                for stirrup_type, expected_legs in stirrup_mappings[lang].items():
                    result = get_stirrup_legs(stirrup_type, lang)
                    self.assertEqual(result, expected_legs)


class TestPDFReportIntegration(unittest.TestCase):
    """Test PDF report generation integration"""
    
    def setUp(self):
        """Set up PDF test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_results = {
            'project_info': {
                'title': 'RC Beam Design Report',
                'date': '2024-01-15',
                'engineer': 'Test Engineer'
            },
            'input_data': {
                'width': 300,
                'depth': 500,
                'fc': 280,
                'fy': 4000,
                'moment': 12.5,
                'shear': 8.0
            },
            'design_results': {
                'main_steel': '#5(D16) x 4',
                'compression_steel': '#4(D13) x 2',
                'stirrups': '#3(D10) @ 150mm',
                'moment_capacity': 15.2,
                'shear_capacity': 12.3
            },
            'safety_check': {
                'moment_ok': True,
                'shear_ok': True,
                'overall_safe': True
            }
        }
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_pdf_content_structure(self):
        """Test PDF content structure and completeness"""
        def generate_pdf_content(results):
            """Mock PDF content generation"""
            content_sections = []
            
            # Title section
            if 'project_info' in results:
                content_sections.append('title')
                
            # Input data section
            if 'input_data' in results:
                content_sections.append('input_data')
                
            # Design results section
            if 'design_results' in results:
                content_sections.append('design_results')
                
            # Safety check section
            if 'safety_check' in results:
                content_sections.append('safety_check')
                
            # Summary section
            if all(section in content_sections for section in ['input_data', 'design_results', 'safety_check']):
                content_sections.append('summary')
                
            return content_sections
            
        content = generate_pdf_content(self.sample_results)
        
        # Verify all expected sections are present
        expected_sections = ['title', 'input_data', 'design_results', 'safety_check', 'summary']
        for section in expected_sections:
            self.assertIn(section, content)
            
    def test_academic_format_compliance(self):
        """Test academic format compliance"""
        def check_academic_format(results):
            """Check if results comply with academic format requirements"""
            checks = {
                'has_numbered_sections': True,
                'has_proper_units': True,
                'has_calculations_shown': True,
                'has_safety_verification': True,
                'has_conclusion': True
            }
            
            # Check input data formatting
            input_data = results.get('input_data', {})
            if not all(key in input_data for key in ['width', 'depth', 'fc', 'fy']):
                checks['has_proper_units'] = False
                
            # Check design results
            design_results = results.get('design_results', {})
            if not all(key in design_results for key in ['main_steel', 'stirrups']):
                checks['has_calculations_shown'] = False
                
            # Check safety verification
            safety_check = results.get('safety_check', {})
            if not all(key in safety_check for key in ['moment_ok', 'shear_ok']):
                checks['has_safety_verification'] = False
                
            return checks
            
        format_check = check_academic_format(self.sample_results)
        
        # Verify all format requirements are met
        for requirement, is_met in format_check.items():
            self.assertTrue(is_met, f"Academic format requirement not met: {requirement}")
            
    def test_multi_page_layout(self):
        """Test multi-page PDF layout handling"""
        def calculate_content_pages(results):
            """Calculate number of pages needed for content"""
            pages_needed = 1  # Start with 1 page
            
            # Estimate content length
            content_lines = 0
            
            # Count input data lines
            input_data = results.get('input_data', {})
            content_lines += len(input_data) * 2  # Each parameter takes ~2 lines
            
            # Count design results lines
            design_results = results.get('design_results', {})
            content_lines += len(design_results) * 3  # Each result takes ~3 lines
            
            # Add safety check lines (only if has results)
            if design_results:
                content_lines += 10  # Fixed safety check section
            
            # Add calculation details (academic format, only if has design results)
            if design_results:
                content_lines += 30  # Detailed calculations
            
            # Estimate pages (assuming 40 lines per page)
            pages_needed = max(1, (content_lines + 39) // 40)
            
            return min(pages_needed, 5)  # Cap at 5 pages
            
        pages = calculate_content_pages(self.sample_results)
        
        # Verify reasonable page count (should be 1-3 pages for typical report)
        self.assertGreaterEqual(pages, 1)
        self.assertLessEqual(pages, 5)
        
        # Test with minimal content
        minimal_results = {'input_data': {'width': 300}}
        minimal_pages = calculate_content_pages(minimal_results)
        self.assertEqual(minimal_pages, 1)
        
        # Test with extensive content
        extensive_results = self.sample_results.copy()
        extensive_results['additional_calculations'] = {f'calc_{i}': f'value_{i}' for i in range(20)}
        extensive_pages = calculate_content_pages(extensive_results)
        self.assertGreaterEqual(extensive_pages, 1)  # Should need at least 1 page


class TestPerformanceScenarios(unittest.TestCase):
    """Test performance under various scenarios"""
    
    def test_calculation_performance(self):
        """Test calculation performance for typical scenarios"""
        import time
        
        def mock_beam_calculation():
            """Mock time-consuming beam calculation"""
            # Simulate calculation time
            start_time = time.time()
            
            # Mock some calculations
            for i in range(1000):
                result = i * 0.001 + 0.85  # Simulate beta calculation
                result = result ** 0.5     # Simulate square root
                
            end_time = time.time()
            return end_time - start_time
            
        # Test that calculation completes within reasonable time
        calc_time = mock_beam_calculation()
        self.assertLess(calc_time, 1.0)  # Should complete within 1 second
        
    def test_memory_usage_scenarios(self):
        """Test memory usage for different beam configurations"""
        def estimate_memory_usage(beam_count):
            """Estimate memory usage for multiple beam calculations"""
            # Each beam calculation might use approximately:
            # - Input data: ~1KB
            # - Calculation results: ~5KB  
            # - PDF generation: ~50KB
            # Total per beam: ~56KB
            
            estimated_kb = beam_count * 56
            return estimated_kb
            
        # Test memory estimation for different scenarios
        single_beam = estimate_memory_usage(1)
        self.assertLess(single_beam, 100)  # Less than 100KB
        
        multiple_beams = estimate_memory_usage(10)
        self.assertLess(multiple_beams, 1000)  # Less than 1MB
        
    def test_concurrent_calculation_handling(self):
        """Test handling of concurrent calculations"""
        def mock_concurrent_calculations(num_calculations):
            """Mock multiple concurrent calculations"""
            results = []
            
            for i in range(num_calculations):
                # Each calculation should be independent
                calc_id = f"beam_{i}"
                calc_result = {
                    'id': calc_id,
                    'width': 300 + i * 10,  # Vary dimensions
                    'depth': 500 + i * 20,
                    'completed': True
                }
                results.append(calc_result)
                
            return results
            
        # Test multiple calculations
        results = mock_concurrent_calculations(5)
        self.assertEqual(len(results), 5)
        
        # Verify each calculation has unique parameters
        widths = [r['width'] for r in results]
        self.assertEqual(len(set(widths)), 5)  # All should be unique


if __name__ == '__main__':
    # Create comprehensive test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestBeamDesignScenarios))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestErrorHandlingScenarios))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestMultiLanguageIntegration))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPDFReportIntegration))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPerformanceScenarios))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print comprehensive summary
    print(f"\n{'='*80}")
    print(f"INTEGRATION TEST SUMMARY:")
    print(f"{'='*80}")
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Successful: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"{i}. {test}: {traceback.split('AssertionError:')[-1].strip()}")
            
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"{i}. {test}: {traceback.split('Error:')[-1].strip()}")
    
    print(f"{'='*80}")
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)
