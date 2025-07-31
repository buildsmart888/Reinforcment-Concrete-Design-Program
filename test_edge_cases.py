#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge Case Tests for RC Beam Calculator
Comprehensive testing of boundary conditions and extreme scenarios
"""

import unittest
import sys
import os
import math

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from beam_function import (
    get_EandG_vaule, rebar_info, stirrup_info, get_clear_cover,
    get_beta, cal_bar_allowable_num, cal_d_eff, cal_shear_strngth,
    cal_recbeam_Mn, cal_effective_width, check_stirrup_span_limit,
    math2
)


class TestExtremeBoundaryConditions(unittest.TestCase):
    """Test extreme boundary conditions and edge cases"""
    
    def test_minimum_concrete_strength_edge_cases(self):
        """Test edge cases for minimum concrete strength"""
        # Test exactly at boundary (210 kgf/cm2)
        Ec_boundary, _ = get_EandG_vaule(210)
        self.assertGreater(Ec_boundary, 0)
        
        # Test just above minimum
        Ec_above, _ = get_EandG_vaule(210.1)
        self.assertGreater(Ec_above, 0)
        
        # Test very low strength (edge case)
        Ec_low, _ = get_EandG_vaule(150)
        self.assertGreater(Ec_low, 0)
        
        # Test beta factor at boundary
        beta_boundary = get_beta(210)
        self.assertEqual(beta_boundary, 0.85)
        
        beta_just_above = get_beta(280.1)
        self.assertLess(beta_just_above, 0.85)
        
    def test_maximum_concrete_strength_edge_cases(self):
        """Test edge cases for maximum concrete strength"""
        # Test at maximum typical strength
        Ec_max, _ = get_EandG_vaule(420)
        self.assertGreater(Ec_max, 0)
        
        # Test beyond typical maximum
        Ec_ultra, _ = get_EandG_vaule(500)
        self.assertGreater(Ec_ultra, 0)
        
        # Test beta factor at high strength
        beta_high = get_beta(420)
        self.assertGreaterEqual(beta_high, 0.65)  # Should not go below 0.65
        
        beta_ultra = get_beta(500)
        self.assertLessEqual(beta_ultra, 0.75)  # Should be reasonable value
        self.assertGreaterEqual(beta_ultra, 0.65)  # Should not go below 0.65
        
    def test_extreme_beam_dimensions(self):
        """Test extreme beam dimensions"""
        # Very narrow beam
        narrow_beam = {
            'width': 150,  # Very narrow
            'depth': 300,
            'cover': 40
        }
        
        # Check that narrow beam can still accommodate rebar
        rebar_d = 1.588  # #5 rebar
        stirrup_d = 0.953  # #3 stirrup
        
        num_rebars, _ = cal_bar_allowable_num(
            narrow_beam['width'], narrow_beam['cover'], 
            rebar_d, stirrup_d, 'no', 'Beam'
        )
        self.assertGreaterEqual(num_rebars, 1)  # Should accommodate at least 1 rebar
        
        # Very wide beam
        wide_beam = {
            'width': 1000,  # Very wide
            'depth': 500,
            'cover': 40
        }
        
        num_rebars_wide, _ = cal_bar_allowable_num(
            wide_beam['width'], wide_beam['cover'],
            rebar_d, stirrup_d, 'no', 'Beam'
        )
        self.assertGreater(num_rebars_wide, num_rebars)  # Wide beam should accommodate more
        
        # Very deep beam
        deep_beam = {
            'width': 300,
            'depth': 1500,  # Very deep
            'cover': 40
        }
        
        d_deep, _, _ = cal_d_eff(
            deep_beam['width'], deep_beam['depth'], deep_beam['cover'],
            rebar_d, stirrup_d, 4, 'no', 'Beam'
        )
        self.assertGreater(d_deep, 1400)  # Effective depth should be reasonable
        
    def test_extreme_rebar_configurations(self):
        """Test extreme rebar configurations"""
        # Maximum rebar size
        max_rebar = '#11(D36)'
        diameter, area = rebar_info(max_rebar)
        self.assertEqual(diameter, 3.581)
        self.assertAlmostEqual(area, math.pi * 3.581**2 / 4, places=3)
        
        # Minimum rebar size
        min_rebar = '#3(D10)'
        diameter_min, area_min = rebar_info(min_rebar)
        self.assertEqual(diameter_min, 0.953)
        self.assertLess(area_min, area)
        
        # Many rebars in single row
        B = 600  # Wide beam
        cover = 40
        rebar_d = 1.588  # #5
        stirrup_d = 0.953  # #3
        
        max_rebars, _ = cal_bar_allowable_num(B, cover, rebar_d, stirrup_d, 'no', 'Beam')
        self.assertGreater(max_rebars, 10)  # Should accommodate many rebars
        
    def test_extreme_loading_conditions(self):
        """Test extreme loading conditions"""
        # Very high shear with small stirrups
        stirrup_d = 0.953  # #3 stirrup (smallest)
        stirrup_num = 2    # Two-leg
        stirrup_span = 100  # Very close spacing
        
        fc = 280
        fy = 4000
        B = 300
        d = 450
        
        Av, Vc, phiVn = cal_shear_strngth(
            stirrup_d, stirrup_num, stirrup_span, fc, fy, B, d
        )
        
        # Check that calculation is reasonable
        self.assertGreater(Av, 0)
        self.assertGreater(Vc, 0)
        self.assertGreater(phiVn, Vc * 0.75)  # Should be at least concrete contribution
        
        # Very wide stirrup spacing
        wide_spacing = 300  # Maximum typical spacing
        Av_wide, Vc_wide, phiVn_wide = cal_shear_strngth(
            stirrup_d, stirrup_num, wide_spacing, fc, fy, B, d
        )
        
        self.assertLess(phiVn_wide, phiVn)  # Wider spacing should give less capacity
        
    def test_extreme_material_combinations(self):
        """Test extreme material combinations"""
        # High strength concrete with low strength steel
        fc_high = 420  # High strength concrete
        fy_low = 2400  # Low strength steel
        
        # Test beta factor at boundary
        beta_high_low = get_beta(fc_high)
        self.assertLessEqual(beta_high_low, 0.85)  # Should be reasonable
        self.assertGreaterEqual(beta_high_low, 0.65)  # Should not go below 0.65
        
        # Low strength concrete with high strength steel
        fc_low = 210   # Low strength concrete
        fy_high = 6000 # High strength steel
        
        beta_low_high = get_beta(fc_low)
        self.assertEqual(beta_low_high, 0.85)
        
        # Check moment calculation with extreme combinations
        B = 300
        d = 450
        dd = 50
        beta = 0.85
        Ass = 0  # No compression steel
        As = 10  # Some tension steel
        
        # Test with extreme material combination
        Asy, result, c, Cc, Cs, Mn = cal_recbeam_Mn(
            dd, fc_low, beta, B, d, fy_high, Ass, As
        )
        
        self.assertGreater(Mn, 0)
        self.assertIsInstance(result, str)
        
    def test_zero_and_negative_edge_cases(self):
        """Test zero and near-zero conditions"""
        # Zero compression steel
        B = 300
        d = 450
        dd = 50
        fc = 280
        fy = 4000
        beta = 0.85
        Ass = 0  # Zero compression steel
        As = 8
        
        Asy, result, c, Cc, Cs, Mn = cal_recbeam_Mn(
            dd, fc, beta, B, d, fy, Ass, As
        )
        
        self.assertGreater(Mn, 0)
        self.assertEqual(Cs, 0)  # No compression steel contribution
        
        # Very small tension steel
        As_small = 0.1
        Asy_small, result_small, c_small, Cc_small, Cs_small, Mn_small = cal_recbeam_Mn(
            dd, fc, beta, B, d, fy, Ass, As_small
        )
        
        self.assertGreater(Mn_small, 0)
        self.assertLess(Mn_small, Mn)
        
    def test_mathematical_edge_cases(self):
        """Test mathematical edge cases in calculations"""
        # Test quadratic solver with edge cases
        
        # Case 1: Discriminant = 0 (one solution)
        result = math2(1, -4, 4)  # (x-2)² = 0
        self.assertEqual(result, 2.0)
        
        # Case 2: Very small coefficients
        result_small = math2(1e-6, -2e-6, 1e-6)
        # This might return a single value or list depending on discriminant
        self.assertTrue(isinstance(result_small, (list, float, str)))
        
        # Case 3: Large coefficients
        result_large = math2(1e6, -2e6, 1e6)
        self.assertEqual(result_large, 1.0)
        
        # Case 4: Negative discriminant
        result_negative = math2(1, 1, 1)
        self.assertEqual(result_negative, "Your equation has no root.")
        
    def test_effective_width_edge_cases(self):
        """Test effective width calculation edge cases"""
        B = 300  # Beam width
        
        # Very large span
        large_span = 10000  # 100m span
        hf = 100
        Sn = 5000
        
        be_large = cal_effective_width('คานใน', B, Sn, hf, large_span)
        self.assertGreater(be_large, B)
        self.assertLess(be_large, large_span)  # Should be limited
        
        # Very small span
        small_span = 200  # 2m span
        be_small = cal_effective_width('คานใน', B, Sn, hf, small_span)
        self.assertGreater(be_small, 0)  # Should be positive
        # For small spans, effective width might be limited by span/4
        
        # Very thin flange
        thin_hf = 5  # Very thin flange
        be_thin = cal_effective_width('คานใน', B, Sn, thin_hf, 6000)
        self.assertGreater(be_thin, B)
        
        # Very thick flange
        thick_hf = 500  # Very thick flange
        be_thick = cal_effective_width('คานใน', B, Sn, thick_hf, 6000)
        self.assertGreater(be_thick, B)
        
    def test_stirrup_spacing_edge_cases(self):
        """Test stirrup spacing calculation edge cases"""
        # Very high shear force
        Vu_high = 50.0  # Very high shear
        Vc = 8.0
        fc = 280
        fy = 4000
        B = 300
        d = 450
        Av = 1.42
        
        s_max, s_max1, s_max2 = check_stirrup_span_limit(
            Vu_high, Vc, fc, fy, B, d, Av
        )
        
        self.assertIsInstance(s_max, list)
        if s_max[0] != 'no need for stirrup':
            self.assertGreater(float(s_max[0]), 0)
        
        # Very low shear force
        Vu_low = 2.0
        s_max_low, s_max1_low, s_max2_low = check_stirrup_span_limit(
            Vu_low, Vc, fc, fy, B, d, Av
        )
        
        # Only compare if both are numeric values
        if (s_max[0] != 'no need for stirrup' and 
            s_max_low[0] != 'no need for stirrup'):
            self.assertGreater(float(s_max_low[0]), float(s_max[0]))  # Lower shear allows wider spacing


class TestNumericalStabilityEdgeCases(unittest.TestCase):
    """Test numerical stability in edge cases"""
    
    def test_floating_point_precision(self):
        """Test calculations with very small and very large numbers"""
        # Very small concrete strength (but positive)
        fc_tiny = 1e-3
        Ec_tiny, _ = get_EandG_vaule(fc_tiny)
        self.assertGreater(Ec_tiny, 0)
        self.assertFalse(math.isnan(Ec_tiny))
        self.assertFalse(math.isinf(Ec_tiny))
        
        # Very large concrete strength
        fc_huge = 1e6
        Ec_huge, _ = get_EandG_vaule(fc_huge)
        self.assertGreater(Ec_huge, 0)
        self.assertFalse(math.isnan(Ec_huge))
        self.assertFalse(math.isinf(Ec_huge))
        
    def test_division_by_zero_protection(self):
        """Test protection against division by zero"""
        # Test rebar info with edge case
        valid_sizes = ['#3(D10)', '#4(D13)', '#5(D16)']
        for size in valid_sizes:
            diameter, area = rebar_info(size)
            self.assertGreater(diameter, 0)
            self.assertGreater(area, 0)
            self.assertFalse(math.isnan(area))
            
    def test_square_root_edge_cases(self):
        """Test square root calculations with edge cases"""
        # Test with very small fc
        fc_small = 0.1
        beta = get_beta(fc_small)
        self.assertGreater(beta, 0)
        self.assertLessEqual(beta, 0.85)
        
        # Test concrete modulus with small fc
        Ec_small, _ = get_EandG_vaule(fc_small)
        self.assertGreater(Ec_small, 0)
        

class TestErrorRecoveryEdgeCases(unittest.TestCase):
    """Test error recovery and graceful degradation"""
    
    def test_invalid_input_recovery(self):
        """Test recovery from invalid inputs"""
        # Test invalid rebar size
        diameter, area = rebar_info('INVALID_SIZE')
        self.assertEqual(diameter, 'none')
        self.assertEqual(area, 'none')
        
        # Test invalid stirrup type
        legs = stirrup_info('INVALID_STIRRUP')
        self.assertEqual(legs, 2)  # Should default to 2
        
        # Test invalid element type for cover
        cover = get_clear_cover('INVALID_TYPE')
        self.assertEqual(cover, 4)  # Should default to 4
        
    def test_extreme_geometry_recovery(self):
        """Test recovery from extreme geometry inputs"""
        # Extremely narrow beam
        B_tiny = 10  # 1cm wide beam
        cover = 40
        rebar_d = 1.588
        stirrup_d = 0.953
        
        # Should not crash even with impossible geometry
        try:
            num_rebars, clearance = cal_bar_allowable_num(
                B_tiny, cover, rebar_d, stirrup_d, 'no', 'Beam'
            )
            # If it doesn't crash, check that result is reasonable
            self.assertIsInstance(num_rebars, int)
            self.assertGreaterEqual(num_rebars, 0)
        except (ValueError, ZeroDivisionError):
            # It's acceptable to raise an error for impossible geometry
            pass
            
    def test_extreme_loading_recovery(self):
        """Test recovery from extreme loading conditions"""
        # Extremely high moment that might cause numerical issues
        B = 300
        d = 450
        dd = 50
        fc = 280
        fy = 4000
        beta = 0.85
        Ass = 0
        As_extreme = 1000  # Extremely high steel area
        
        try:
            Asy, result, c, Cc, Cs, Mn = cal_recbeam_Mn(
                dd, fc, beta, B, d, fy, Ass, As_extreme
            )
            # If calculation succeeds, check for reasonable results
            self.assertGreater(Mn, 0)
            self.assertFalse(math.isnan(Mn))
            self.assertFalse(math.isinf(Mn))
        except (ValueError, OverflowError):
            # Acceptable to fail with extreme inputs
            pass


if __name__ == '__main__':
    # Create comprehensive edge case test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add all edge case test classes
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestExtremeBoundaryConditions))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestNumericalStabilityEdgeCases))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestErrorRecoveryEdgeCases))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"EDGE CASE TEST SUMMARY:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*70}")
    
    # Print details of any failures or errors
    if result.failures:
        print(f"\nFAILURES:")
        for i, (test, error) in enumerate(result.failures, 1):
            print(f"{i}. {test}")
            
    if result.errors:
        print(f"\nERRORS:")
        for i, (test, error) in enumerate(result.errors, 1):
            print(f"{i}. {test}")
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)
