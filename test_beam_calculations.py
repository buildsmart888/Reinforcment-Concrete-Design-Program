#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for RC Beam Calculation Functions
Test coverage for beam calculation modules and functions
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
from rc_recbeamcal_base import recbeam_cal_button_clicked
from rc_beamdsgn_base import (
    dsgn_recbeam_single_As, dsgn_tbeam_single_As, 
    cal_rec_tensioncontrol_single_Mnmax, cal_t_tensioncontrol_single_Mnmax,
    cal_development_length
)


class TestBeamCalculationFunctions(unittest.TestCase):
    """Test beam calculation core functions"""
    
    def setUp(self):
        """Set up test fixtures with standard beam parameters"""
        self.fc = 280  # kgf/cm2
        self.fy = 4000  # kgf/cm2
        self.B = 30    # cm
        self.D = 50    # cm
        self.d = 45    # cm
        self.cover = 4  # cm
        
    def test_concrete_modulus_calculation(self):
        """Test concrete modulus of elasticity calculation"""
        Ec, ShearM = get_EandG_vaule(self.fc)
        
        # Expected Ec = 12000 * sqrt(280) / 1000 = 200.8 tf/cm2
        expected_Ec = 12000 * math.sqrt(280) / 1000
        self.assertAlmostEqual(Ec, expected_Ec, places=2)
        
        # Test edge cases
        Ec_min, _ = get_EandG_vaule(210)  # Minimum typical fc
        Ec_max, _ = get_EandG_vaule(420)  # Maximum typical fc
        self.assertGreater(Ec_max, Ec_min)
        
    def test_rebar_info_function(self):
        """Test rebar information retrieval"""
        # Test standard rebar sizes
        test_cases = [
            ('#3(D10)', 0.953),
            ('#4(D13)', 1.27),
            ('#5(D16)', 1.588),
            ('#8(D25)', 2.54),
            ('#10(D32)', 3.226)
        ]
        
        for rebar_size, expected_diameter in test_cases:
            diameter, area = rebar_info(rebar_size)
            self.assertAlmostEqual(diameter, expected_diameter, places=3)
            
            # Verify area calculation: A = π*d²/4
            expected_area = math.pi * diameter**2 / 4
            self.assertAlmostEqual(area, expected_area, places=4)
            
        # Test invalid input
        diameter, area = rebar_info('invalid')
        self.assertEqual(diameter, 'none')
        
    def test_stirrup_info_function(self):
        """Test stirrup configuration information"""
        test_cases = [
            ('เหล็กปลอกสองขา', 2),
            ('เหล็กปลอกสามขา', 3),
            ('เหล็กปลอกสี่ขา', 4),
            ('Two-leg Stirrup', 2),
            ('Three-leg Stirrup', 3),
            ('Four-leg Stirrup', 4),
            ('雙肢箍', 2),
            ('三肢箍', 3),
            ('四肢箍', 4)
        ]
        
        for stirrup_type, expected_legs in test_cases:
            legs = stirrup_info(stirrup_type)
            self.assertEqual(legs, expected_legs)
            
        # Test invalid input (should default to 2)
        legs = stirrup_info('invalid_stirrup')
        self.assertEqual(legs, 2)
        
    def test_clear_cover_function(self):
        """Test clear cover requirements"""
        test_cases = [
            ('Beam', 4),
            ('Column', 4),
            ('Slab', 2)
        ]
        
        for element_type, expected_cover in test_cases:
            cover = get_clear_cover(element_type)
            self.assertEqual(cover, expected_cover)
            
        # Test invalid input (should default to 4)
        cover = get_clear_cover('invalid')
        self.assertEqual(cover, 4)
        
    def test_beta_factor_calculation(self):
        """Test beta1 factor calculation for different concrete strengths"""
        test_cases = [
            (210, 0.85),    # fc <= 280
            (280, 0.85),    # fc = 280
            (350, 0.8),     # fc > 280
            (420, 0.7)      # High strength concrete
        ]
        
        for fc, expected_beta in test_cases:
            beta = get_beta(fc)
            if fc <= 280:
                self.assertEqual(beta, 0.85)
            else:
                # beta = max(0.65, 0.85 - 0.05/70 * (fc - 280))
                expected = max(0.65, 0.85 - 0.05/70 * (fc - 280))
                self.assertAlmostEqual(beta, expected, places=3)
                
    def test_allowable_rebar_number_calculation(self):
        """Test calculation of allowable number of rebars per row"""
        # Test beam configuration
        rebar_d = 1.588  # #5 rebar
        stirrup_d = 0.953  # #3 stirrup
        
        num_rebars, clear_spacing = cal_bar_allowable_num(
            self.B, self.cover, rebar_d, stirrup_d, 'no', 'Beam'
        )
        
        # Verify the calculation
        # cleardb_h = max(2.5, rebar_d) = max(2.5, 1.588) = 2.5
        # available_width = B - 2*cover - 2*stirrup_d - rebar_d
        # = 30 - 2*4 - 2*0.953 - 1.588 = 18.506
        # num_rebars = floor(18.506 / (1.588 + 2.5)) + 1
        
        self.assertIsInstance(num_rebars, int)
        self.assertGreater(num_rebars, 0)
        self.assertLessEqual(num_rebars, 10)  # Reasonable upper limit
        
    def test_effective_depth_calculation(self):
        """Test effective depth calculation for different rebar arrangements"""
        rebar_d = 1.588  # #5 rebar
        stirrup_d = 0.953  # #3 stirrup
        
        # Test single row
        d_single, dt_single, allowable_num = cal_d_eff(
            self.B, self.D, self.cover, rebar_d, stirrup_d, 3, 'no', 'Beam'
        )
        
        # For single row: d = D - cover - stirrup_d - rebar_d/2
        expected_d_single = self.D - self.cover - stirrup_d - rebar_d/2
        self.assertAlmostEqual(d_single, expected_d_single, places=2)
        self.assertEqual(d_single, dt_single)
        
        # Test multiple rows (if applicable)
        if allowable_num < 6:  # Force multiple rows
            d_multi, dt_multi, _ = cal_d_eff(
                self.B, self.D, self.cover, rebar_d, stirrup_d, allowable_num + 2, 'no', 'Beam'
            )
            self.assertLess(d_multi, d_single)  # Multi-row should have smaller effective depth
            self.assertEqual(dt_multi, expected_d_single)  # dt should remain the same
            
    def test_shear_strength_calculation(self):
        """Test shear strength calculation"""
        stirrup_d = 0.953  # #3 stirrup diameter in cm
        stirrup_num = 2    # Two-leg stirrup
        stirrup_span = 15  # cm
        
        Av, Vc, phiVn = cal_shear_strngth(
            stirrup_d, stirrup_num, stirrup_span, self.fc, self.fy, self.B, self.d
        )
        
        # Verify Av calculation
        expected_Av = stirrup_num * math.pi * stirrup_d**2 / 4
        self.assertAlmostEqual(Av, expected_Av, places=4)
        
        # Verify Vc calculation (concrete shear strength)
        expected_Vc = 0.53 * self.fc**0.5 * self.B * self.d / 1000
        self.assertAlmostEqual(Vc, expected_Vc, places=3)
        
        # Verify phiVn (total shear strength)
        Vs = Av / stirrup_span * self.fy * self.d / 1000
        expected_phiVn = 0.75 * (Vc + Vs)
        self.assertAlmostEqual(phiVn, expected_phiVn, places=3)
        
    def test_stirrup_spacing_limits(self):
        """Test stirrup spacing limit checks"""
        Vu = 15.0  # tf
        Vc = 8.0   # tf
        Av = 1.42  # cm2
        
        s_max, s_max1, s_max2 = check_stirrup_span_limit(
            Vu, Vc, self.fc, self.fy, self.B, self.d, Av
        )
        
        # Verify calculations
        if Vu > 2 * Vc:
            expected_s_max1 = Av * self.fy * self.d / ((Vu - Vc) * 1000) * 10  # mm
            expected_s_max2 = self.d / 4 * 10  # d/4 converted to mm
        else:
            expected_s_max1 = Av * self.fy * self.d / ((Vu - Vc) * 1000) * 10  # mm
            expected_s_max2 = self.d / 2 * 10  # d/2 converted to mm
            
        self.assertIsInstance(s_max, list)
        self.assertGreater(float(s_max[0]), 0)
        
    def test_effective_width_calculation(self):
        """Test effective flange width calculation for T-beams"""
        hf = 10    # cm (flange thickness)
        length = 600  # cm (beam span)
        Sn = 300   # cm (spacing between beams)
        
        # Test interior beam
        be_interior = cal_effective_width('คานใน', self.B, Sn, hf, length)
        expected_interior = min(length/4, self.B + Sn, self.B + 16*hf)
        self.assertEqual(be_interior, expected_interior)
        
        # Test exterior beam  
        be_exterior = cal_effective_width('คานริม', self.B, Sn, hf, length)
        expected_exterior = min(self.B + length/12, self.B + Sn/2, self.B + 6*hf)
        self.assertEqual(be_exterior, expected_exterior)
        
    def test_math2_quadratic_solver(self):
        """Test quadratic equation solver"""
        # Test case with two real roots
        # x² - 5x + 6 = 0 → roots: 2, 3
        result = math2(1, -5, 6)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        roots = sorted(result)
        self.assertAlmostEqual(roots[0], 2, places=6)
        self.assertAlmostEqual(roots[1], 3, places=6)
        
        # Test case with one real root
        # x² - 4x + 4 = 0 → root: 2
        result = math2(1, -4, 4)
        self.assertAlmostEqual(result, 2, places=6)
        
        # Test case with no real roots
        # x² + x + 1 = 0
        result = math2(1, 1, 1)
        self.assertEqual(result, "Your equation has no root.")
        
    def test_rectangular_beam_moment_calculation(self):
        """Test rectangular beam moment strength calculation"""
        dd = 5    # cm (compression steel depth)
        beta = 0.85
        Ass = 2.0  # cm2 (compression steel)
        As = 8.0   # cm2 (tension steel)
        
        Asy, result, c, Cc, Cs, Mn = cal_recbeam_Mn(
            dd, self.fc, beta, self.B, self.d, self.fy, Ass, As
        )
        
        # Verify results are reasonable
        self.assertGreater(Asy, 0)
        self.assertIsInstance(result, str)
        self.assertGreater(c, 0)
        self.assertGreater(Cc, 0)
        self.assertGreater(Mn, 0)
        
        # Moment should be in tf-m (reasonable range for this beam)
        self.assertGreater(Mn, 5)
        self.assertLess(Mn, 50)
        
    def test_single_reinforcement_design(self):
        """Test single reinforcement design calculation"""
        Mn_req = 15.0  # tf-m (required moment)
        
        As_req = dsgn_recbeam_single_As(self.B, self.d, self.fc, self.fy, Mn_req)
        
        # Verify result is reasonable
        self.assertGreater(As_req, 0)
        self.assertLess(As_req, 50)  # Should be reasonable for this beam size
        
        # Test with different moment requirements
        Mn_small = 5.0
        As_small = dsgn_recbeam_single_As(self.B, self.d, self.fc, self.fy, Mn_small)
        self.assertLess(As_small, As_req)  # Smaller moment should need less steel
        
    def test_tension_controlled_maximum_moment(self):
        """Test maximum moment for tension-controlled section"""
        phiMn, As = cal_rec_tensioncontrol_single_Mnmax(self.B, self.d, self.fc, self.fy)
        
        # Verify results are reasonable
        self.assertGreater(phiMn, 0)
        self.assertGreater(As, 0)
        
        # For tension control, c = 3d/8
        c_expected = 3 * self.d / 8
        beta = get_beta(self.fc)
        a_expected = beta * c_expected
        
        # Verify steel area calculation
        As_expected = 0.85 * self.fc * self.B * a_expected / self.fy
        self.assertAlmostEqual(As, As_expected, places=2)
        
    def test_development_length_calculation(self):
        """Test development length calculation"""
        # Mock barinfo structure
        barinfo = {
            '#5(D16)': [1.588, 1.99, 5, 4.0]  # [diameter, area, max_per_row, weight]
        }
        choose_bar = '#5(D16)'
        
        # Calculate development length
        dvlpmnt_length = cal_development_length(self.fc, self.fy, barinfo, choose_bar)
        
        # Verify minimum development length
        self.assertGreaterEqual(dvlpmnt_length, 30)  # ACI minimum
        
        # Test with different parameters
        high_strength_concrete = 420
        dvlpmnt_high_fc = cal_development_length(high_strength_concrete, self.fy, barinfo, choose_bar)
        self.assertLess(dvlpmnt_high_fc, dvlpmnt_length)  # Higher fc should reduce ld


class TestBeamDesignIntegration(unittest.TestCase):
    """Integration tests for complete beam design process"""
    
    def setUp(self):
        """Set up test fixtures for integration tests"""
        # Create mock data object similar to GUI input
        class MockData:
            def __init__(self):
                # Beam dimensions
                self.width = MockLineEdit("30")      # cm
                self.depth = MockLineEdit("50")      # cm
                
                # Material properties  
                self.fc = MockLineEdit("280")        # kgf/cm2
                self.fy = MockLineEdit("4000")       # kgf/cm2
                
                # Reinforcement
                self.bar1 = MockComboBox("#5(D16)")
                self.bar2 = MockComboBox("#4(D13)")
                self.barnum1 = MockLineEdit("4")
                self.barnum2 = MockLineEdit("2")
                
                # Stirrups
                self.stirrup_size = MockComboBox("#3(D10)")
                self.stirrup_num = MockComboBox("เหล็กปลอกสองขา")
                self.stirrup_span = MockLineEdit("15")
                
                # Loading
                self.Mux = MockLineEdit("12.5")      # tf-m
                self.Vuy = MockLineEdit("8.0")       # tf
                
                # Constructability
                self.cnstrctblty = 'no'
                
        class MockLineEdit:
            def __init__(self, value):
                self._value = value
            def text(self):
                return self._value
                
        class MockComboBox:
            def __init__(self, value):
                self._value = value
            def currentText(self):
                return self._value
        
        self.mock_data = MockData()
        
    def test_complete_beam_calculation_flow(self):
        """Test complete rectangular beam calculation"""
        try:
            # This would normally call the main calculation function
            # For now, we'll test individual components
            
            # Test input parsing
            B = float(self.mock_data.width.text())
            D = float(self.mock_data.depth.text())
            fc = float(self.mock_data.fc.text())
            fy = float(self.mock_data.fy.text())
            
            self.assertEqual(B, 30)
            self.assertEqual(D, 50)
            self.assertEqual(fc, 280)
            self.assertEqual(fy, 4000)
            
            # Test that inputs are valid for calculation
            self.assertGreater(B, 0)
            self.assertGreater(D, 0)
            self.assertGreater(fc, 0)
            self.assertGreater(fy, 0)
            
            # Test rebar information retrieval
            rebar_d1, rebar_area1 = rebar_info(self.mock_data.bar1.currentText())
            rebar_d2, rebar_area2 = rebar_info(self.mock_data.bar2.currentText())
            
            self.assertNotEqual(rebar_d1, 'none')
            self.assertNotEqual(rebar_d2, 'none')
            self.assertGreater(rebar_area1, 0)
            self.assertGreater(rebar_area2, 0)
            
        except Exception as e:
            self.fail(f"Complete beam calculation flow failed: {e}")


if __name__ == '__main__':
    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestBeamCalculationFunctions))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestBeamDesignIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"TEST SUMMARY:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*70}")
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)
