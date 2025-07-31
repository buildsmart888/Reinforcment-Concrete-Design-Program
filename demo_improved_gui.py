#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script สำหรับทดสอบ GUI ใหม่
เปรียบเทียบกับ GUI เดิม
"""

import sys
import os
import json
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QHBoxLayout, QFileDialog

# เพิ่ม path สำหรับ import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import Rectangle, Circle
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    import numpy as np
    
    # ตั้งค่า font สำหรับภาษาไทยและสัญลักษณ์พิเศษ
    import matplotlib.font_manager as fm
    
    # ใช้ฟอนต์ที่รองรับสัญลักษณ์กรีกและไทย
    plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans', 'Liberation Sans', 'TH Sarabun New']
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['mathtext.default'] = 'regular'  # ใช้ฟอนต์ปกติสำหรับ math text
    
    # ฟังก์ชันตั้งค่าฟอนต์สำหรับ PDF export
    def setup_font_for_pdf():
        """ตั้งค่าฟอนต์ที่รองรับสัญลักษณ์พิเศษสำหรับ PDF export"""
        try:
            # หาฟอนต์ที่รองรับสัญลักษณ์กรีกและไทย
            preferred_fonts = [
                'Arial Unicode MS',     # รองรับสัญลักษณ์กรีกและไทย
                'DejaVu Sans',         # รองรับสัญลักษณ์กรีก
                'Liberation Sans',     # รองรับสัญลักษณ์กรีก
                'Noto Sans',          # รองรับหลากหลายสัญลักษณ์
                'Segoe UI',           # รองรับสัญลักษณ์พิเศษ
                'TH Sarabun New'      # สำหรับไทย (แต่ไม่รองรับกรีก)
            ]
            
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            best_font = None
            
            for font in preferred_fonts:
                if font in available_fonts:
                    best_font = font
                    break
            
            if best_font:
                # ตั้งค่าฟอนต์ที่รองรับสัญลักษณ์พิเศษ
                plt.rcParams['font.family'] = [best_font, 'Arial Unicode MS', 'DejaVu Sans']
                print(f"Using font for symbols: {best_font}")
            else:
                # ใช้ฟอนต์สำรองที่รองรับ Unicode
                plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
                print("Using fallback Unicode font for symbols")
                
            # ตั้งค่าเพิ่มเติมสำหรับสัญลักษณ์พิเศษ
            plt.rcParams['font.size'] = 12
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['text.usetex'] = False
            plt.rcParams['mathtext.default'] = 'regular'
            plt.rcParams['mathtext.fontset'] = 'dejavusans'  # ใช้ DejaVu สำหรับ math symbols
            
            return best_font or 'Arial Unicode MS'
            
        except Exception as e:
            print(f"Font setup error: {e}")
            plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans', 'sans-serif']
            return 'Arial Unicode MS'
    
    # เรียกใช้ฟังก์ชันตั้งค่าฟอนต์เริ่มต้น
    setup_font_for_pdf()
    
except ImportError as e:
    print(f"Warning: Optional dependencies not found: {e}")
    plt = None
    mpatches = None
    Rectangle = None
    Circle = None
    FigureCanvas = None
    np = None

# เพิ่ม path สำหรับ import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ui_rc_recbeamcal_improved import Ui_RcRecBeamCalImproved, ModernInputValidator
    from language_manager import lang_manager
    from beam_function import (get_section_info, cal_recbeam_Mn, cal_phi, cal_shear_strngth, 
                              check_stirrup_span_limit, rebar_info, stirrup_info, get_clear_cover)
    from rc_recbeamcal_base import recbeam_cal_button_clicked
except ImportError as e:
    print(f"ไม่สามารถ import module ได้: {e}")
    print("กรุณาตรวจสอบว่าไฟล์ที่จำเป็นอยู่ในโฟลเดอร์เดียวกัน")


class ImprovedRCBeamCalculator(QtWidgets.QMainWindow):
    """
    คลาสหลักสำหรับเครื่องคำนวณคาน RC แบบปรับปรุง
    """
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_RcRecBeamCalImproved()
        self.ui.setupUi(self)
        self.setup_connections()
        self.setup_validators()
        self.load_sample_data()
        
        # Setup window properties
        self.setWindowIcon(QtGui.QIcon(":/icons/calculator.png"))
        self.setMinimumSize(1000, 700)
        
        # Center window on screen
        self.center_window()
        
        # Show welcome message
        QTimer.singleShot(500, self.show_welcome_message)
    
    def center_window(self):
        """Center the window on screen"""
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def calculate_effective_depth(self):
        """คำนวณความลึกมีประสิทธิภาพอัตโนมัติตามหลักวิศวกรรม"""
        try:
            # ดึงค่าจาก UI
            depth = float(self.ui.depth.text())
            cover = float(self.ui.cover.text())
            
            # ดึงขนาดเหล็กรับแรงดึง
            main_rebar_text = self.ui.main_rebar_size.currentText()
            main_diameter = self.extract_rebar_diameter(main_rebar_text)
            
            # ดึงขนาดเหล็กปลอก
            stirrup_text = self.ui.stirrup_size.currentText()
            stirrup_diameter = self.extract_rebar_diameter(stirrup_text)
            
            # คำนวณความลึกมีประสิทธิภาพ
            # d = D - cover - stirrup_diameter - main_diameter/2
            effective_depth = depth - cover - stirrup_diameter - (main_diameter / 2)
            
            # อัปเดต UI display
            self.ui.d_display.setText(f"{effective_depth:.0f} มม.")
            
            return effective_depth
            
        except (ValueError, AttributeError) as e:
            # ถ้าไม่สามารถคำนวณได้ ให้ใช้ค่าเริ่มต้น
            default_d = 450
            self.ui.d_display.setText(f"{default_d:.0f} มม. (ค่าเริ่มต้น)")
            return default_d
    
    def setup_connections(self):
        """เชื่อมต่อ signals และ slots"""
        # Connect buttons
        self.ui.btn_calculate.clicked.connect(self.calculate_beam)
        self.ui.btn_clear.clicked.connect(self.clear_inputs)
        self.ui.btn_export_pdf.clicked.connect(self.export_pdf)
        self.ui.btn_save.clicked.connect(self.save_data)
        
        # Connect input validation
        input_widgets = [
            self.ui.width, self.ui.depth, self.ui.cover,  # ลบ self.ui.d เพราะคำนวณอัตโนมัติ
            self.ui.fc, self.ui.fy, self.ui.main_rebar_num, self.ui.comp_rebar_num,
            self.ui.stirrup_spacing, self.ui.moment, self.ui.shear
        ]
        
        for widget in input_widgets:
            widget.textChanged.connect(self.validate_inputs)
            widget.textChanged.connect(self.calculate_effective_depth)  # เพิ่มการคำนวณอัตโนมัติ
            
        # Connect combobox changes for effective depth calculation
        combo_widgets = [self.ui.main_rebar_size, self.ui.stirrup_size]
        for widget in combo_widgets:
            widget.currentTextChanged.connect(self.calculate_effective_depth)
            
        # Connect combo box changes
        self.ui.main_rebar_size.currentTextChanged.connect(self.validate_inputs)
        self.ui.comp_rebar_size.currentTextChanged.connect(self.validate_inputs)
        self.ui.stirrup_size.currentTextChanged.connect(self.validate_inputs)
        self.ui.stirrup_type.currentTextChanged.connect(self.validate_inputs)
    
    def setup_validators(self):
        """ตั้งค่า input validators"""
        # Set input masks and validators if needed
        pass
    
    def load_sample_data(self):
        """โหลดข้อมูลตัวอย่าง"""
        sample_data = {
            'width': '300',
            'depth': '500', 
            'd': '450',
            'cover': '40',
            'length': '6.0',
            'fc': '240.00',
            'fy': '4000.00',
            'main_rebar_size': '#5(D16)',
            'main_rebar_num': '4',
            'comp_rebar_size': '#4(D13)', 
            'comp_rebar_num': '2',
            'stirrup_size': '#3(D10)',
            'stirrup_type': 'เหล็กปลอกสองขา',
            'stirrup_spacing': '150',
            'moment': '15.00',
            'shear': '8.00'
        }
        
        self.ui.width.setText(sample_data['width'])
        self.ui.depth.setText(sample_data['depth'])
        # ลบการกำหนด d เพราะจะคำนวณอัตโนมัติ
        self.ui.cover.setText(sample_data['cover'])
        # ลบ self.ui.length.setText(sample_data['length']) - ไม่ใช้แล้ว
        self.ui.fc.setText(sample_data['fc'])
        self.ui.fy.setText(sample_data['fy'])
        self.ui.main_rebar_size.setCurrentText(sample_data['main_rebar_size'])
        self.ui.main_rebar_num.setText(sample_data['main_rebar_num'])
        self.ui.comp_rebar_size.setCurrentText(sample_data['comp_rebar_size'])
        self.ui.comp_rebar_num.setText(sample_data['comp_rebar_num'])
        self.ui.stirrup_size.setCurrentText(sample_data['stirrup_size'])
        self.ui.stirrup_type.setCurrentText(sample_data['stirrup_type'])
        self.ui.stirrup_spacing.setText(sample_data['stirrup_spacing'])
        self.ui.moment.setText(sample_data['moment'])
        self.ui.shear.setText(sample_data['shear'])
        # ลบการตั้งค่า torsion แล้ว
        
        # คำนวณ effective depth อัตโนมัติหลังจากโหลดข้อมูล
        self.calculate_effective_depth()
    
    def validate_inputs(self):
        """ตรวจสอบความถูกต้องของข้อมูลที่ป้อน"""
        try:
            # Validate dimensions
            width_valid, width_msg = ModernInputValidator.validate_positive_number(
                self.ui.width.text(), min_value=100, max_value=2000
            )
            
            depth_valid, depth_msg = ModernInputValidator.validate_positive_number(
                self.ui.depth.text(), min_value=200, max_value=2000
            )
            
            # ลบการ validate effective depth เพราะคำนวณอัตโนมัติ
            d_valid = True  # ไม่ต้องตรวจสอบเพราะคำนวณอัตโนมัติ
            d_msg = ""
            
            cover_valid, cover_msg = ModernInputValidator.validate_positive_number(
                self.ui.cover.text(), min_value=20, max_value=100
            )
            
            # ลบการ validate ความยาวคาน - ตามที่ผู้ใช้ร้องขอ
            
            # Validate materials
            mat_valid, mat_msg = ModernInputValidator.validate_material_properties(
                self.ui.fc.text(), self.ui.fy.text()
            )
            
            # Validate reinforcement
            rebar_valid, rebar_msg = ModernInputValidator.validate_reinforcement(
                self.ui.main_rebar_num.text(), self.ui.comp_rebar_num.text(), 
                self.ui.stirrup_spacing.text()
            )
            
            # Validate loading
            load_valid, load_msg = ModernInputValidator.validate_loading(
                self.ui.moment.text(), self.ui.shear.text()
            )
            
            # Validate beam dimension relationships
            if width_valid and depth_valid and d_valid and cover_valid:
                # ใช้ effective depth ที่คำนวณอัตโนมัติ
                d_calculated = self.calculate_effective_depth()
                dim_valid, dim_msg = ModernInputValidator.validate_beam_dimensions(
                    self.ui.width.text(), self.ui.depth.text(), 
                    str(d_calculated), self.ui.cover.text()
                )
            else:
                dim_valid = False
                dim_msg = ""
            
            # Enable calculate button only if all validations pass
            all_valid = all([width_valid, depth_valid, d_valid, cover_valid,
                           mat_valid, rebar_valid, load_valid, dim_valid])
            self.ui.btn_calculate.setEnabled(all_valid)
            
            # Update status bar
            if all_valid:
                self.ui.statusbar.showMessage("ข้อมูลถูกต้อง - พร้อมคำนวณ", 2000)
            else:
                error_msgs = [msg for valid, msg in [
                    (width_valid, width_msg), (depth_valid, depth_msg), (d_valid, d_msg),
                    (cover_valid, cover_msg), (mat_valid, mat_msg), 
                    (rebar_valid, rebar_msg), (load_valid, load_msg), (dim_valid, dim_msg)
                ] if not valid and msg]
                
                if error_msgs:
                    self.ui.statusbar.showMessage(f"ข้อผิดพลาด: {error_msgs[0]}")
                    
        except Exception as e:
            self.ui.statusbar.showMessage(f"เกิดข้อผิดพลาดในการตรวจสอบ: {str(e)}")
    
    def calculate_beam(self):
        """คำนวณคาน RC ใช้ฟังก์ชันจากไฟล์เดิม"""
        try:
            # ตรวจสอบข้อมูลที่ได้รับจาก UI
            print("=== ตรวจสอบข้อมูลที่ได้รับจาก UI ===")
            
            # Get input values - use ksc units directly (no conversion needed)
            B = float(self.ui.width.text()) / 10   # mm to cm
            D = float(self.ui.depth.text()) / 10   # mm to cm
            d = self.calculate_effective_depth() / 10  # mm to cm (คำนวณอัตโนมัติ)
            # ลบ L = float(self.ui.length.text()) - ไม่ใช้ความยาวคานแล้ว
            fc = float(self.ui.fc.text())          # ksc (already in correct units)
            fy = float(self.ui.fy.text())          # ksc (already in correct units)
            print(f"มิติคาน: B={B*10:.0f} มม., D={D*10:.0f} มม., d={d*10:.0f} มม. (คำนวณอัตโนมัติ)")
            print(f"กำลังวัสดุ: fc={fc:.1f} ksc, fy={fy:.1f} ksc")
            
            # Reinforcement details
            main_rebar_size = self.ui.main_rebar_size.currentText()
            comp_rebar_size = self.ui.comp_rebar_size.currentText()
            main_rebar_num = int(self.ui.main_rebar_num.text())
            comp_rebar_num = int(self.ui.comp_rebar_num.text())
            stirrup_size = self.ui.stirrup_size.currentText()
            stirrup_type = self.ui.stirrup_type.currentText()
            stirrup_spacing = float(self.ui.stirrup_spacing.text()) / 10  # mm to cm
            print(f"เหล็กหลัก: {main_rebar_size} x{main_rebar_num}, เหล็กอัด: {comp_rebar_size} x{comp_rebar_num}")
            print(f"เหล็กปลอก: {stirrup_size} {stirrup_type} @{stirrup_spacing*10:.0f} มม.")
            
            # Loading (use tf units directly - no conversion needed)
            Mu = float(self.ui.moment.text())      # tf-m (already in correct units)
            Vu = float(self.ui.shear.text())       # tf (already in correct units) 
            Tu = 0.0  # ลบช่องกรอก torsion แล้ว ตั้งค่าเป็น 0
            print(f"แรงกระทำ: Mu={Mu:.2f} tf-m, Vu={Vu:.2f} tf, Tu={Tu:.2f} tf-m")
            
            # Get material and section properties using original functions
            PrtctT = get_clear_cover('Beam')  # cm
            stirrup_num = stirrup_info(stirrup_type)
            
            [beta, Ec, db_rebar1, Ab_rebar1, db_rebar2, Ab_rebar2, As, Ass, d_eff, dt, dd, 
             db_stirrup, Ab_stirrup, RebarAllowNumPerRow1, RebarAllowNumPerRow2] = get_section_info(
                B, D, fc, fy, main_rebar_size, comp_rebar_size, main_rebar_num, 
                comp_rebar_num, stirrup_size, PrtctT, 'no', "Beam"
            )
            
            # Calculate moment strength using original function
            [Asy, result0, c, Cc, Cs, Mn] = cal_recbeam_Mn(dd, fc, beta, B, d_eff, fy, Ass, As)
            [es, et, result1, result2, phi] = cal_phi(c, d_eff, dt)
            
            # Calculate shear strength using original function
            [Av, Vc, phiVn] = cal_shear_strngth(db_stirrup, stirrup_num, stirrup_spacing, fc, fy, B, d_eff)
            [s_max, s_max1, s_max2] = check_stirrup_span_limit(Vu, Vc, fc, fy, B, d_eff, Av)
            
            # Compile results
            results = {
                # Input parameters - ใช้ค่าที่ผู้ใช้กรอกโดยตรง
                'B': B*10, 'D': D*10, 'd': d*10, 'fc': fc, 'fy': fy,  # ใช้ค่าจริงที่กรอก
                'main_rebar': main_rebar_size, 'main_num': main_rebar_num,
                'comp_rebar': comp_rebar_size, 'comp_num': comp_rebar_num,
                'stirrup': stirrup_size, 'stirrup_type': stirrup_type, 
                'stirrup_spacing': stirrup_spacing*10,
                'Mu': Mu, 'Vu': Vu, 'Tu': Tu,  # เปลี่ยนจาก Mu*10 เป็น Mu เพื่อใช้หน่วย tf ตรง ๆ
                
                # Calculated values - ใช้ค่าที่คำนวณได้จากฟังก์ชัน
                'As': As, 'Ass': Ass, 'Asy': Asy,
                'c': c, 'beta': beta, 'phi': phi,
                'Cc': Cc, 'Cs': Cs, 'Mn': Mn, 'phiMn': phi*Mn,
                'es': es, 'et': et, 'result0': result0, 'result1': result1, 'result2': result2,
                'Av': Av, 'Vc': Vc, 'phiVn': phiVn, 's_max': s_max[0] if s_max[0] != 'no need for stirrup' else 'ไม่จำเป็นใช้เหล็กปลอก',
                's_max1': s_max1, 's_max2': s_max2,  # เพิ่มค่าเงื่อนไขแยก
                
                # Effective depth from calculation for technical purposes
                'd_eff': d_eff*10,  # เพิ่มค่า d_eff สำหรับการคำนวณภายใน
                # ลบ beam_length เพราะไม่ใช้แล้ว
                
                # Check results
                'moment_adequate': phi*Mn >= Mu,
                'shear_adequate': phiVn >= Vu,
                'moment_ratio': (phi*Mn) / Mu if Mu > 0 else float('inf'),
                'shear_ratio': phiVn / Vu if Vu > 0 else float('inf'),
                'spacing_adequate': stirrup_spacing*10 <= (s_max[0] if isinstance(s_max[0], (int, float)) else 600)
            }
            
            # Store results for PDF export
            self.last_results = results
            
            # Display results with detailed formulas
            self.display_detailed_results(results)
            
            # Generate section diagram
            self.generate_section_diagram(results)
            
            # Update status
            self.ui.statusbar.showMessage("คำนวณเสร็จสิ้น", 3000)
            
            # Switch to results tab
            self.ui.tab_widget.setCurrentIndex(0)
            
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการคำนวณ:\n{str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def perform_beam_calculation(self, b, h, d, fc, fy, Mu):
        """ดำเนินการคำนวณคาน (Simplified ACI 318)"""
        import math
        
        # Material properties
        Es = 200000  # MPa (Elastic modulus of steel)
        beta1 = 0.85 if fc <= 28 else max(0.85 - 0.05 * (fc - 28) / 7, 0.65)
        
        # Balanced reinforcement ratio
        rho_b = (0.85 * fc * beta1 / fy) * (600 / (600 + fy))
        rho_max = 0.75 * rho_b
        rho_min = max(1.4 / fy, math.sqrt(fc) / (4 * fy))
        
        # Required moment strength
        phi = 0.9  # Strength reduction factor for flexure
        Mn_req = Mu / phi  # Required nominal moment strength
        
        # Calculate required reinforcement
        Rn = Mn_req / (b * d * d)  # N/mm²
        rho_req = (0.85 * fc / fy) * (1 - math.sqrt(1 - 2 * Rn / (0.85 * fc)))
        
        # Check limits
        rho_use = max(rho_min, min(rho_req, rho_max))
        As_req = rho_use * b * d  # mm²
        
        # Calculate actual moment capacity
        a = As_req * fy / (0.85 * fc * b)
        c = a / beta1
        Mn = As_req * fy * (d - a/2)
        phi_Mn = phi * Mn
        
        # Check adequacy
        adequate = phi_Mn >= Mu
        
        # Calculate strain in steel
        epsilon_s = 0.003 * (d - c) / c
        tension_controlled = epsilon_s >= 0.005
        
        # Results dictionary
        results = {
            'b': b, 'h': h, 'd': d, 'fc': fc, 'fy': fy,
            'Mu': Mu, 'Mn_req': Mn_req, 'phi_Mn': phi_Mn,
            'rho_min': rho_min, 'rho_req': rho_req, 'rho_max': rho_max,
            'rho_use': rho_use, 'As_req': As_req,
            'a': a, 'c': c, 'epsilon_s': epsilon_s,
            'adequate': adequate, 'tension_controlled': tension_controlled,
            'safety_ratio': phi_Mn / Mu if Mu > 0 else 0
        }
        
        return results
    
    def display_detailed_results(self, results):
        """แสดงผลลัพธ์การคำนวณแบบละเอียดพร้อมสูตรและการแทนค่า"""
        
        # ตรวจสอบความปลอดภัยและกำหนดสี
        moment_status = "✓ ปลอดภัย" if results['moment_adequate'] else "✗ ไม่ปลอดภัย"
        moment_color = "green" if results['moment_adequate'] else "red"
        shear_status = "✓ ปลอดภัย" if results['shear_adequate'] else "✗ ไม่ปลอดภัย"
        shear_color = "green" if results['shear_adequate'] else "red"
        
        # แปลงข้อความภาษาจีนเป็นภาษาไทย
        result0_th = self.translate_chinese_result(results.get('result0', ''))
        result1_th = self.translate_chinese_result(results.get('result1', ''))
        result2_th = self.translate_chinese_result(results.get('result2', ''))
        
        # Format detailed results with formulas (for results tab)
        results_text = f"""
=== ผลลัพธ์การคำนวณคาน RC แบบละเอียด ===

📐 ข้อมูลนำเข้า:
  • ความกว้างคาน (B) = {results['B']:.0f} มม.
  • ความสูงคาน (D) = {results['D']:.0f} มม.  
  • ความลึกมีประสิทธิภาพ (d) = {results['d']:.0f} มม.
  • กำลังรับแรงอัดคอนกรีต (f'c) = {results['fc']:.1f} ksc
  • กำลังรับแรงดึงเหล็ก (fy) = {results['fy']:.1f} ksc

🔧 ข้อมูลเหล็กเสริม:
  • เหล็กรับแรงดึง: {results['main_rebar']} จำนวน {results['main_num']} เส้น
  • เหล็กรับแรงอัด: {results['comp_rebar']} จำนวน {results['comp_num']} เส้น  
  • เหล็กปลอก: {results['stirrup']} {results['stirrup_type']} ระยะ {results['stirrup_spacing']:.0f} มม.

⚡ แรงกระทำ:
  • โมเมนต์ (Mu) = {results['Mu']:.2f} tf-m
  • แรงเฉือน (Vu) = {results['Vu']:.2f} tf

📊 การคำนวณโมเมนต์แบบละเอียด:

1. พื้นที่เหล็กเสริม:
   สูตร: As = n × π × d²/4
   As = {results['main_num']} × π × {self.extract_rebar_diameter(results['main_rebar'])}²/4 = {results['As']:.2f} ตร.ซม.
   A's = {results['comp_num']} × π × {self.extract_rebar_diameter(results['comp_rebar'])}²/4 = {results['Ass']:.2f} ตร.ซม.

2. ค่า β1 สำหรับคอนกรีต:
   สูตร: β1 = 0.85 สำหรับ f'c ≤ 280 ksc
   β1 = {results['beta']:.3f}

3. ความลึกของแกนกลาง (c):
   สูตร: c = (As×fy - A's×f's) / (0.85×f'c×b×β1)
   c = ({results['As']:.2f}×{results['fy']:.0f} - {results['Ass']:.2f}×f's) / (0.85×{results['fc']:.1f}×{results['B']/10:.0f}×{results['beta']:.3f})
   c = {results['c']:.2f} ซม.

4. การตรวจสอบการครอบครอง:
   {result0_th}

5. ค่า strain ในเหล็ก:
   สูตร: การเปลี่ยนรูปในเหล็กรับแรงดึง = 0.003 × (d-c)/c
   การเปลี่ยนรูปในเหล็กรับแรงดึง = 0.003 × ({results['d']/10:.1f}-{results['c']:.2f})/{results['c']:.2f} = {results['es']:.6f}
   การเปลี่ยนรูปสูงสุด = 0.003 × (dt-c)/c = {results['et']:.6f}
   สถานะการควบคุม: {result1_th}

6. ค่า ϕ (ตัวคูณความปลอดภัย):
   สูตร: ϕ = 0.9 สำหรับการควบคุมด้วยแรงดึง
   ϕ = {results['phi']:.3f}

7. กำลังรับโมเมนต์:
   สูตร: Cc = 0.85×f'c×a×b (a = β1×c)
   Cc = 0.85×{results['fc']:.1f}×{results['beta']:.3f}×{results['c']:.2f}×{results['B']/10:.0f} = {results['Cc']:.2f} tf
   
   สูตร: Cs = f's×A's
   Cs = f's×{results['Ass']:.2f} = {results['Cs']:.2f} tf
   
   สูตร: Mn = As×fy×(d-a/2) + Cs×(d-d')
   Mn = {results['As']:.2f}×{results['fy']:.0f}×({results['d']/10:.1f}-{results['beta']:.3f}×{results['c']:.2f}/2) + {results['Cs']:.2f}×(d-d')
   Mn = {results['Mn']:.2f} tf-m
   
   ϕMn = {results['phi']:.3f}×{results['Mn']:.2f} = {results['phiMn']:.2f} tf-m

📊 การคำนวณแรงเฉือนแบบละเอียด:

1. พื้นที่เหล็กปลอก:
   สูตร: Av = n_legs × π × db²/4
   Av = {self.get_stirrup_legs(results['stirrup_type'])} × π × {self.extract_rebar_diameter(results['stirrup'])}²/4 = {results['Av']:.3f} ตร.ซม.

2. กำลังรับแรงเฉือนของคอนกรีต:
   สูตร: Vc = 0.53×√f'c × b × d
   Vc = 0.53×√{results['fc']:.1f} × {results['B']/10:.0f} × {results['d']/10:.1f} = {results['Vc']:.2f} tf

3. กำลังรับแรงเฉือนของเหล็กปลอก:
   สูตร: Vs = Av×fy×d/s
   Vs = {results['Av']:.3f}×{results['fy']:.0f}×{results['d']/10:.1f}/{results['stirrup_spacing']/10:.1f}

4. กำลังรับแรงเฉือนรวม:
   สูตร: Vn = Vc + Vs
   φVn = 0.75 × Vn = {results['phiVn']:.2f} tf

5. ระยะห่างเหล็กปลอก (ตาม ACI 9.7.6.2.2):
   ระยะห่างที่กรอก: s = {results['stirrup_spacing']:.0f} มม.
   ระยะห่างสูงสุดที่อนุญาต (มีสองเงื่อนไข):
   - s_max1 = {results['s_max1']} มม. (ตามมาตรฐาน)
   - s_max2 = d/2 = {results['s_max2']} มม. (ความลึกมีประสิทธิภาพ)
   การตรวจสอบ: {'✓ เหมาะสม' if results['spacing_adequate'] else '✗ ไม่เหมาะสม'}
   หมายเหตุ: การคำนวณตาม ACI 318 Table 9.7.6.2.2

✅ การตรวจสอบความปลอดภัย:

🔹 โมเมนต์:
   ϕMn = {results['phiMn']:.2f} tf-m {'≥' if results['moment_adequate'] else '<'} Mu = {results['Mu']:.2f} tf-m
   {moment_status} (อัตราส่วน = {results['moment_ratio']:.2f})

🔹 แรงเฉือน:
   φVn = {results['phiVn']:.2f} tf {'≥' if results['shear_adequate'] else '<'} Vu = {results['Vu']:.2f} tf
   {shear_status} (อัตราส่วน = {results['shear_ratio']:.2f})

🎯 สรุปผล:
{'✅ การออกแบบเหมาะสมและปลอดภัย!' if results['moment_adequate'] and results['shear_adequate'] else '⚠️  การออกแบบต้องปรับปรุง!'}

📝 หมายเหตุ:
   - การคำนวณตามมาตรฐาน ACI 318
   - ใช้หน่วย tf-m สำหรับโมเมนต์, tf สำหรับแรง
   - εs = ค่า strain ในเหล็กรับแรงดึง
   - εt = ค่า strain ในเหล็กที่อยู่ไกลสุดจากแกนกลาง
"""
        # Display in results tab
        self.ui.results_text.setText(results_text)
        
        # Generate Markdown report with LaTeX equations
        markdown_report = self.generate_markdown_report(results)
        self.ui.report_text.setHtml(markdown_report)
    
    def generate_markdown_report(self, results):
        """สร้างรายงานรูปแบบ Markdown แบบมีรูปแบบสวยงาม"""
        
        # แปลงข้อความภาษาจีนเป็นภาษาไทย
        result0_th = self.translate_chinese_result(results.get('result0', ''))
        result1_th = self.translate_chinese_result(results.get('result1', ''))
        
        # ค่าที่ใช้ในสมการ
        main_dia = self.extract_rebar_diameter(results['main_rebar'])
        comp_dia = self.extract_rebar_diameter(results['comp_rebar'])
        stirrup_dia = self.extract_rebar_diameter(results['stirrup'])
        stirrup_legs = self.get_stirrup_legs(results['stirrup_type'])
        
        # สถานะความปลอดภัย
        moment_status = "✅ ปลอดภัย" if results['moment_adequate'] else "❌ ไม่ปลอดภัย"
        shear_status = "✅ ปลอดภัย" if results['shear_adequate'] else "❌ ไม่ปลอดภัย"
        overall_status = "✅ เหมาะสมและปลอดภัย" if results['moment_adequate'] and results['shear_adequate'] else "⚠️ ต้องปรับปรุง"
        
        # คำนวณหน่วยที่ถูกต้อง
        fc_ksc = results['fc']  # ใช้ค่าเดิม ksc
        fy_ksc = results['fy']  # ใช้ค่าเดิม ksc
        
        # แปลงขนาดให้ถูกต้อง
        width_cm = results['B'] / 10  # มม. -> ซม.
        depth_cm = results['D'] / 10  # มม. -> ซม.
        d_cm = results['d'] / 10  # มม. -> ซม.
        
        # แปลงค่าแรงให้ถูกต้อง
        Cc_kg = results['Cc'] * 1000  # ตัน -> กก.
        Cs_kg = results['Cs'] * 1000  # ตัน -> กก.
        Vc_kg = results['Vc'] * 1000  # ตัน -> กก.
        phiVn_kg = results['phiVn'] * 1000  # ตัน -> กก.
        
        markdown = f"""
<h1 style="text-align: center; color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 15px;">
📊 รายงานการวิเคราะห์คาน RC
</h1>

<div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">

## 📐 ข้อมูลพื้นฐาน

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
<thead style="background-color: #3498db; color: white;">
<tr>
<th style="padding: 12px; text-align: left; border: 1px solid #ddd;">รายการ</th>
<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">ค่า</th>
<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">หน่วย</th>
</tr>
</thead>
<tbody>
<tr style="background-color: #f8f9fa;">
<td style="padding: 10px; border: 1px solid #ddd;"><strong>ความกว้างคาน (B)</strong></td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['B']:.0f}</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">มม.</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;"><strong>ความสูงคาน (D)</strong></td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['D']:.0f}</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">มม.</td>
</tr>
<tr style="background-color: #f8f9fa;">
<td style="padding: 10px; border: 1px solid #ddd;"><strong>ความลึกมีประสิทธิภาพ (d)</strong></td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['d']:.0f}</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">มม.</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;"><strong>กำลังรับแรงอัดคอนกรีต (f'c)</strong></td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{fc_ksc:.1f}</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">กก./ตร.ซม.</td>
</tr>
<tr style="background-color: #f8f9fa;">
<td style="padding: 10px; border: 1px solid #ddd;"><strong>กำลังรับแรงดึงเหล็ก (fy)</strong></td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{fy_ksc:.0f}</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">กก./ตร.ซม.</td>
</tr>
</tbody>
</table>

</div>

<div style="background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">

## 🔧 ข้อมูลเหล็กเสริม

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
<thead style="background-color: #27ae60; color: white;">
<tr>
<th style="padding: 12px; text-align: left; border: 1px solid #ddd;">ประเภทเหล็ก</th>
<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">ขนาด</th>
<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">จำนวน</th>
<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">พื้นที่ (ตร.ซม.)</th>
</tr>
</thead>
<tbody>
<tr style="background-color: #f8f9fa;">
<td style="padding: 10px; border: 1px solid #ddd;"><strong>เหล็กรับแรงดึง</strong></td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['main_rebar']}</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['main_num']} เส้น</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['As']:.2f}</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;"><strong>เหล็กรับแรงอัด</strong></td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['comp_rebar']}</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['comp_num']} เส้น</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['Ass']:.2f}</td>
</tr>
<tr style="background-color: #f8f9fa;">
<td style="padding: 10px; border: 1px solid #ddd;"><strong>เหล็กปลอก</strong></td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['stirrup']} {results['stirrup_type']}</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">ระยะ {results['stirrup_spacing']:.0f} มม.</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['Av']:.3f}</td>
</tr>
</tbody>
</table>

</div>

<div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); padding: 20px; border-radius: 10px; margin: 20px 0;">

## ⚡ แรงกระทำ

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
<thead style="background-color: #f39c12; color: white;">
<tr>
<th style="padding: 12px; text-align: left; border: 1px solid #ddd;">ประเภทแรง</th>
<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">ค่า</th>
<th style="padding: 12px; text-align: center; border: 1px solid #ddd;">หน่วย</th>
</tr>
</thead>
<tbody>
<tr style="background-color: #f8f9fa;">
<td style="padding: 10px; border: 1px solid #ddd;"><strong>โมเมนต์ (Mu)</strong></td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['Mu']:.2f}</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">ตัน-เมตร</td>
</tr>
<tr>
<td style="padding: 10px; border: 1px solid #ddd;"><strong>แรงเฉือน (Vu)</strong></td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">{results['Vu']:.2f}</td>
<td style="padding: 10px; text-align: center; border: 1px solid #ddd;">ตัน</td>
</tr>
</tbody>
</table>

</div>

---

<h2 style="color: #2c3e50; border-left: 5px solid #3498db; padding-left: 15px;">📊 การคำนวณโมเมนต์แบบละเอียด</h2>

### 1️⃣ พื้นที่เหล็กเสริม
<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
<p><strong>เหล็กรับแรงดึง:</strong> As = {results['main_num']} × π × {main_dia}²/4 = <span style="color: #e74c3c; font-weight: bold;">{results['As']:.2f} ตร.ซม.</span></p>
<p><strong>เหล็กรับแรงอัด:</strong> A's = {results['comp_num']} × π × {comp_dia}²/4 = <span style="color: #e74c3c; font-weight: bold;">{results['Ass']:.2f} ตร.ซม.</span></p>
</div>

### 2️⃣ ค่า β1 สำหรับคอนกรีต
<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
<p>สำหรับ f'c ≤ 280 กก./ตร.ซม.: β1 = <span style="color: #e74c3c; font-weight: bold;">{results['beta']:.3f}</span></p>
</div>

### 3️⃣ ความลึกของแกนกลาง
<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
<p>สูตร: c = (As×fy - A's×f's) / (0.85×f'c×b×β1)</p>
<p>c = ({results['As']:.2f}×{fy_ksc:.0f} - {results['Ass']:.2f}×f's) / (0.85×{fc_ksc:.1f}×{width_cm:.0f}×{results['beta']:.3f}) = <span style="color: #e74c3c; font-weight: bold;">{results['c']:.2f} ซม.</span></p>
</div>

### 4️⃣ การตรวจสอบการครอบครอง
<div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 10px 0;">
<p style="font-weight: bold; color: #27ae60;">{result0_th}</p>
</div>

### 5️⃣ ค่า Strain ในเหล็ก
<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
<p>การเปลี่ยนรูปในเหล็กรับแรงดึง: εs = 0.003 × (d-c)/c = 0.003 × ({d_cm:.1f}-{results['c']:.2f})/{results['c']:.2f} = <span style="color: #e74c3c; font-weight: bold;">{results['es']:.6f}</span></p>
<p>การเปลี่ยนรูปสูงสุด: εt = 0.003 × (dt-c)/c = <span style="color: #e74c3c; font-weight: bold;">{results['et']:.6f}</span></p>
<p><strong>สถานะการควบคุม:</strong> <span style="color: #27ae60; font-weight: bold;">{result1_th}</span></p>
</div>

### 6️⃣ ค่า ϕ (ตัวคูณความปลอดภัย)
<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
<p>สำหรับการควบคุมด้วยแรงดึง: ϕ = <span style="color: #e74c3c; font-weight: bold;">{results['phi']:.3f}</span></p>
</div>

### 7️⃣ กำลังรับโมเมนต์
<div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0;">
<p><strong>แรงอัดในคอนกรีต:</strong> Cc = 0.85×f'c×a×b (a = β1×c)</p>
<p>Cc = 0.85×{fc_ksc:.1f}×{results['beta']:.3f}×{results['c']:.2f}×{width_cm:.0f} = <span style="color: #e74c3c; font-weight: bold;">{Cc_kg:.0f} กก.</span></p>
<p><strong>แรงในเหล็กรับแรงอัด:</strong> Cs = f's×A's = <span style="color: #e74c3c; font-weight: bold;">{Cs_kg:.0f} กก.</span></p>
<p><strong>โมเมนต์ต้านทานนามบัญญัติ:</strong> Mn = <span style="color: #e74c3c; font-weight: bold;">{results['Mn']:.2f} ตัน-เมตร</span></p>
<p><strong>โมเมนต์ต้านทานออกแบบ:</strong> ϕMn = {results['phi']:.3f}×{results['Mn']:.2f} = <span style="color: #e74c3c; font-weight: bold;">{results['phiMn']:.2f} ตัน-เมตร</span></p>
</div>

---

<h2 style="color: #2c3e50; border-left: 5px solid #e74c3c; padding-left: 15px;">🔧 การคำนวณแรงเฉือนแบบละเอียด</h2>

### 1️⃣ พื้นที่เหล็กปลอก
<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
<p>Av = {stirrup_legs} × π × {stirrup_dia}²/4 = <span style="color: #e74c3c; font-weight: bold;">{results['Av']:.3f} ตร.ซม.</span></p>
</div>

### 2️⃣ กำลังรับแรงเฉือนของคอนกรีต
<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
<p>Vc = 0.53√f'c × b × d</p>
<p>Vc = 0.53√{fc_ksc:.1f} × {width_cm:.0f} × {d_cm:.1f} = <span style="color: #e74c3c; font-weight: bold;">{Vc_kg:.0f} กก.</span></p>
</div>

### 3️⃣ กำลังรับแรงเฉือนของเหล็กปลอก
<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
<p>Vs = Av×fy×d/s = {results['Av']:.3f}×{fy_ksc:.0f}×{d_cm:.1f}/{results['stirrup_spacing']/10:.1f}</p>
</div>

### 4️⃣ กำลังรับแรงเฉือนรวม
<div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0;">
<p>Vn = Vc + Vs</p>
<p>φVn = 0.75 × Vn = <span style="color: #e74c3c; font-weight: bold;">{phiVn_kg:.0f} กก.</span> = <span style="color: #e74c3c; font-weight: bold;">{results['phiVn']:.2f} ตัน</span></p>
</div>

### 5️⃣ ระยะห่างเหล็กปลอกสูงสุด
<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
<p>ระยะห่างเหล็กปลอก (ตาม ACI 9.7.6.2.2):</p>
<p>s = {results['stirrup_spacing']:.0f} มม. (ที่กรอก)</p>
<p>ระยะห่างสูงสุดที่อนุญาต (มีสองเงื่อนไข):</p>
<p>- s_max1 = <span style="color: #e74c3c; font-weight: bold;">{results['s_max1']} มม.</span> (ตามมาตรฐาน)</p>
<p>- s_max2 = d/2 = <span style="color: #e74c3c; font-weight: bold;">{results['s_max2']} มม.</span> (ความลึกมีประสิทธิภาพ)</p>
<p>การตรวจสอบ: <span style="color: {'green' if results['spacing_adequate'] else 'red'}; font-weight: bold;">{'✓ เหมาะสม' if results['spacing_adequate'] else '✗ ไม่เหมาะสม'}</span></p>
<p>หมายเหตุ: การคำนวณตาม ACI 318 Table 9.7.6.2.2</p>
</div>

---

<h2 style="color: #2c3e50; border-left: 5px solid #f39c12; padding-left: 15px;">🛡️ การตรวจสอบความปลอดภัย</h2>

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
<thead style="background-color: #34495e; color: white;">
<tr>
<th style="padding: 15px; text-align: left; border: 1px solid #ddd;">รายการตรวจสอบ</th>
<th style="padding: 15px; text-align: center; border: 1px solid #ddd;">ค่าออกแบบ</th>
<th style="padding: 15px; text-align: center; border: 1px solid #ddd;">ค่าที่กระทำ</th>
<th style="padding: 15px; text-align: center; border: 1px solid #ddd;">อัตราส่วน</th>
<th style="padding: 15px; text-align: center; border: 1px solid #ddd;">ผลการตรวจสอบ</th>
</tr>
</thead>
<tbody>
<tr style="background-color: {'#d4edda' if results['moment_adequate'] else '#f8d7da'};">
<td style="padding: 12px; border: 1px solid #ddd;"><strong>โมเมนต์</strong></td>
<td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{results['phiMn']:.2f} ตัน-ม</td>
<td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{results['Mu']:.2f} ตัน-ม</td>
<td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{results['moment_ratio']:.2f}</td>
<td style="padding: 12px; text-align: center; border: 1px solid #ddd; font-weight: bold;">{moment_status}</td>
</tr>
<tr style="background-color: {'#d4edda' if results['shear_adequate'] else '#f8d7da'};">
<td style="padding: 12px; border: 1px solid #ddd;"><strong>แรงเฉือน</strong></td>
<td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{results['phiVn']:.2f} ตัน</td>
<td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{results['Vu']:.2f} ตัน</td>
<td style="padding: 12px; text-align: center; border: 1px solid #ddd;">{results['shear_ratio']:.2f}</td>
<td style="padding: 12px; text-align: center; border: 1px solid #ddd; font-weight: bold;">{shear_status}</td>
</tr>
</tbody>
</table>

---

<div style="background: linear-gradient(135deg, {'#d4edda' if results['moment_adequate'] and results['shear_adequate'] else '#f8d7da'} 0%, {'#c3e6cb' if results['moment_adequate'] and results['shear_adequate'] else '#f5c6cb'} 100%); padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center;">

<h2 style="margin: 0; color: {'#155724' if results['moment_adequate'] and results['shear_adequate'] else '#721c24'};">🎯 สรุปผลการวิเคราะห์</h2>

<p style="font-size: 18px; font-weight: bold; margin: 15px 0; color: {'#155724' if results['moment_adequate'] and results['shear_adequate'] else '#721c24'};">
การออกแบบ: {overall_status}
</p>

</div>

---

<div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">

### 📝 หมายเหตุ

- การคำนวณตามมาตรฐาน **ACI 318**
- หน่วยที่ใช้:
  - **ความยาว**: มิลลิเมตร (มม.), เซนติเมตร (ซม.), เมตร (ม.)
  - **แรง**: กิโลกรัม (กก.), ตัน
  - **โมเมนต์**: ตัน-เมตร (ตัน-ม)
  - **ความเค้น**: กิโลกรัมต่อตารางเซนติเมตร (กก./ตร.ซม.)
- การเปลี่ยนรูปในเหล็กรับแรงดึง (εs) = ค่าการเปลี่ยนรูปในเหล็กชั้นในสุด
- การเปลี่ยนรูปสูงสุด (εt) = ค่าการเปลี่ยนรูปในเหล็กที่อยู่ไกลสุดจากแกนกลาง
- ตัวคูณความปลอดภัย (ϕ) = ตัวคูณลดกำลัง (strength reduction factor)

</div>

<hr style="border: none; height: 2px; background: linear-gradient(90deg, #3498db, #e74c3c, #f39c12, #27ae60); margin: 30px 0;">

<p style="text-align: center; color: #7f8c8d; font-style: italic; margin-top: 30px;">
<em>รายงานสร้างโดย RC Beam Analysis Program</em><br>
<small>วันที่สร้างรายงาน: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</small>
</p>
"""
        
        return markdown

    def create_results_text(self, results):
        """สร้างข้อความแสดงผลลัพธ์สำหรับแท็บ Results"""
        
        # แปลงข้อความภาษาจีนเป็นภาษาไทย
        result0_th = self.translate_chinese_result(results.get('result0', ''))
        result1_th = self.translate_chinese_result(results.get('result1', ''))
        
        # ตรวจสอบความปลอดภัย
        moment_status = "✓ ปลอดภัย" if results['moment_adequate'] else "✗ ไม่ปลอดภัย"
        shear_status = "✓ ปลอดภัย" if results['shear_adequate'] else "✗ ไม่ปลอดภัย"
        overall_status = "✅ การออกแบบเหมาะสมและปลอดภัย!" if results['moment_adequate'] and results['shear_adequate'] else "⚠️ การออกแบบต้องปรับปรุง!"
        
        text = f"""=== ผลลัพธ์การคำนวณคาน RC แบบละเอียด ===

📐 ข้อมูลนำเข้า:
  • ความกว้างคาน (B) = {results['B']:.0f} มม.
  • ความสูงคาน (D) = {results['D']:.0f} มม.  
  • ความลึกมีประสิทธิภาพ (d) = {results['d']:.0f} มม.
  • กำลังรับแรงอัดคอนกรีต (f'c) = {results['fc']:.1f} กก./ตร.ซม.
  • กำลังรับแรงดึงเหล็ก (fy) = {results['fy']:.1f} กก./ตร.ซม.

🔧 ข้อมูลเหล็กเสริม:
  • เหล็กรับแรงดึง: {results['main_rebar']} จำนวน {results['main_num']} เส้น
  • เหล็กรับแรงอัด: {results['comp_rebar']} จำนวน {results['comp_num']} เส้น  
  • เหล็กปลอก: {results['stirrup']} {results['stirrup_type']} ระยะ {results['stirrup_spacing']:.0f} มม.

⚡ แรงกระทำ:
  • โมเมนต์ (Mu) = {results['Mu']:.2f} ตัน-เมตร
  • แรงเฉือน (Vu) = {results['Vu']:.2f} ตัน

📊 การคำนวณโมเมนต์แบบละเอียด:

1. พื้นที่เหล็กเสริม:
   As = {results['As']:.2f} ตร.ซม. (เหล็กรับแรงดึง)
   A's = {results['Ass']:.2f} ตร.ซม. (เหล็กรับแรงอัด)

2. ค่า β₁ สำหรับคอนกรีต:
   β₁ = {results['beta']:.3f}

3. ความลึกของแกนกลาง (c):
   c = {results['c']:.2f} ซม.

4. การตรวจสอบการครอบครอง:
   {result0_th}

5. ค่า strain ในเหล็ก:
   εs = {results['es']:.6f}
   εt = {results['et']:.6f}
   สถานะการควบคุม: {result1_th}

6. ค่า φ (ตัวคูณความปลอดภัย):
   φ = {results['phi']:.3f}

7. กำลังรับโมเมนต์:
   Cc = {results['Cc']*1000:.0f} กก. ({results['Cc']:.2f} ตัน)
   Cs = {results['Cs']*1000:.0f} กก. ({results['Cs']:.2f} ตัน)
   Mn = {results['Mn']:.2f} ตัน-เมตร
   φMn = {results['phiMn']:.2f} ตัน-เมตร

📊 การคำนวณแรงเฉือนแบบละเอียด:

1. พื้นที่เหล็กปลอก:
   Av = {results['Av']:.3f} ตร.ซม.

2. กำลังรับแรงเฉือนของคอนกรีต:
   Vc = {results['Vc']*1000:.0f} กก. ({results['Vc']:.2f} ตัน)

3. กำลังรับแรงเฉือนรวม:
   φVn = {results['phiVn']*1000:.0f} กก. ({results['phiVn']:.2f} ตัน)

4. ระยะห่างเหล็กปลอก (ตาม ACI 9.7.6.2.2):
   ระยะห่างที่กรอก: s = {results['stirrup_spacing']:.0f} มม.
   ระยะห่างสูงสุดที่อนุญาต (มีสองเงื่อนไข):
   - s_max1 = {results['s_max1']} มม. (ตามมาตรฐาน)
   - s_max2 = d/2 = {results['s_max2']} มม. (ความลึกมีประสิทธิภาพ)
   การตรวจสอบ: {'✓ เหมาะสม' if results['spacing_adequate'] else '✗ ไม่เหมาะสม'}
   หมายเหตุ: การคำนวณตาม ACI 318 Table 9.7.6.2.2

✅ การตรวจสอบความปลอดภัย:

🔹 โมเมนต์:
   φMn = {results['phiMn']:.2f} ตัน-ม {'≥' if results['moment_adequate'] else '<'} Mu = {results['Mu']:.2f} ตัน-ม
   {moment_status} (อัตราส่วน = {results['moment_ratio']:.2f})

🔹 แรงเฉือน:
   φVn = {results['phiVn']:.2f} ตัน {'≥' if results['shear_adequate'] else '<'} Vu = {results['Vu']:.2f} ตัน
   {shear_status} (อัตราส่วน = {results['shear_ratio']:.2f})

🎯 สรุปผล:
{overall_status}

📝 หมายเหตุ:
   - การคำนวณตามมาตรฐาน ACI 318
   - หน่วยความยาว: มิลลิเมตร (มม.), เซนติเมตร (ซม.)
   - หน่วยแรง: กิโลกรัม (กก.), ตัน
   - หน่วยโมเมนต์: ตัน-เมตร (ตัน-ม)
   - หน่วยความเค้น: กิโลกรัมต่อตารางเซนติเมตร (กก./ตร.ซม.)
   - εs = ค่า strain ในเหล็กรับแรงดึง
   - εt = ค่า strain ในเหล็กที่อยู่ไกลสุดจากแกนกลาง
"""
        
        return text
    
    def translate_chinese_result(self, text):
        """แปลงข้อความภาษาจีนเป็นภาษาไทย"""
        translations = {
            '壓力鋼筋未降伏': 'เหล็กรับแรงอัดไม่ยอม',
            '壓力鋼筋降伏': 'เหล็กรับแรงอัดยอม',
            '拉力控制': 'ควบคุมด้วยแรงดึง',
            '壓力控制': 'ควบคุมด้วยแรงอัด',
            '過渡區域': 'บริเวณเปลี่ยนผ่าน',
            '應力': 'ความเค้น',
            '應變': 'ความเครียด'
        }
        
        for chinese, thai in translations.items():
            text = text.replace(chinese, thai)
        
        return text
    
    def get_stirrup_legs(self, stirrup_type):
        """คืนค่าจำนวนขาเหล็กปลอก"""
        if 'สองขา' in stirrup_type:
            return 2
        elif 'สามขา' in stirrup_type:
            return 3
        elif 'สี่ขา' in stirrup_type:
            return 4
        else:
            return 2  # default
    
    def extract_rebar_diameter(self, rebar):
        """ดึงขนาดเส้นผ่านศูนย์กลางเหล็กจากข้อความ"""
        try:
            # ค้นหาตัวเลขในข้อความ เช่น "RB9" -> 9, "DB12" -> 12
            import re
            numbers = re.findall(r'\d+', rebar)
            if numbers:
                return int(numbers[0])
            else:
                return 12  # default
        except:
            return 12
    
    def translate_chinese_result(self, text):
        """แปลงข้อความภาษาจีนเป็นภาษาไทย"""
        translations = {
            '壓力鋼筋未降伏': 'เหล็กรับแรงอัดไม่ยอม',
            '壓力鋼筋降伏': 'เหล็กรับแรงอัดยอม',
            '拉力控制': 'ควบคุมด้วยแรงดึง',
            '壓力控制': 'ควบคุมด้วยแรงอัด',
            '過渡區域': 'บริเวณเปลี่ยนผ่าน',
            '應力': 'ความเค้น',
            '應變': 'ความเครียด'
        }
        
        for chinese, thai in translations.items():
            text = text.replace(chinese, thai)
        
        return text
    
    def get_stirrup_legs(self, stirrup_type):
        """คืนค่าจำนวนขาเหล็กปลอก"""
        if 'สองขา' in stirrup_type:
            return 2
        elif 'สามขา' in stirrup_type:
            return 3
        elif 'สี่ขา' in stirrup_type:
            return 4
        else:
            return 2  # default
    
    def generate_detailed_report(self, results):
        """สร้างรายงานแบบละเอียดสำหรับ PDF"""
        try:
            if plt is None:
                QMessageBox.warning(self, "เตือน", "ไม่พบ matplotlib กรุณาติดตั้ง: pip install matplotlib")
                return
                
            # สร้าง figure สำหรับรายงาน
            fig = plt.figure(figsize=(16, 20))
            fig.suptitle('รายงานการคำนวณคาน RC แบบละเอียด', fontsize=16, fontweight='bold', y=0.98)
            
            # Close any existing figures to prevent memory warning
            if hasattr(self, 'report_figure') and self.report_figure is not None:
                plt.close(self.report_figure)
            
            # 1. ข้อมูลนำเข้า (subplot 1)
            ax1 = plt.subplot(6, 2, (1, 2))
            ax1.axis('off')
            
            input_text = f"""ข้อมูลการออกแบบ:
            
            ขนาดหน้าตัดคาน:
            • ความกว้าง (B) = {results['B']:.0f} มม.
            • ความสูง (D) = {results['D']:.0f} มม.
            • ความลึกมีประสิทธิภาพ (d) = {results['d']:.0f} มม.
            
            คุณสมบัติวัสดุ:
            • กำลังรับแรงอัดคอนกรีต (f'c) = {results['fc']:.1f} ksc
            • กำลังรับแรงดึงเหล็ก (fy) = {results['fy']:.1f} ksc
            
            เหล็กเสริม:
            • เหล็กรับแรงดึง: {results['main_rebar']} จำนวน {results['main_num']} เส้น
            • เหล็กรับแรงอัด: {results['comp_rebar']} จำนวน {results['comp_num']} เส้น
            • เหล็กปลอก: {results['stirrup']} {results['stirrup_type']} ระยะ {results['stirrup_spacing']:.0f} มม.
            
            แรงกระทำ:
            • โมเมนต์ (Mu) = {results['Mu']:.2f} tf-m
            • แรงเฉือน (Vu) = {results['Vu']:.2f} tf"""
            
            ax1.text(0.05, 0.95, input_text, transform=ax1.transAxes, fontsize=10,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
            
            # 2. แผนภาพหน้าตัดคาน (subplot 2)
            ax2 = plt.subplot(6, 2, (3, 4))
            self.draw_beam_section(ax2, results)
            
            # 3. สูตรการคำนวณโมเมนต์ (subplot 3)
            ax3 = plt.subplot(6, 2, (5, 6))
            ax3.axis('off')
            
            moment_calc = f"""การคำนวณโมเมนต์ (ACI 318):
            
            1. พื้นที่เหล็กเสริม:
               As = {results['As']:.2f} ตร.ซม. (เหล็กรับแรงดึง)
               A's = {results['Ass']:.2f} ตร.ซม. (เหล็กรับแรงอัด)
            
            2. ความลึกของแกนกลาง:
               c = As×fy / (0.85×f'c×b×β₁) = {results['c']:.2f} ซม.
               β₁ = {results['beta']:.3f}
            
            3. ค่า strain และ φ:
               εs = 0.003×(d-c)/c = {results['es']:.6f}
               εt = 0.003×(dt-c)/c = {results['et']:.6f}
               φ = {results['phi']:.3f}
            
            4. กำลังรับโมเมนต์:
               Cc = 0.85×f'c×a×b = {results['Cc']:.2f} tf
               Cs = fs'×A's = {results['Cs']:.2f} tf
               Mn = As×fy×(d-a/2) + Cs×(d-d') = {results['Mn']:.2f} tf-m
               φMn = {results['phiMn']:.2f} tf-m"""
            
            ax3.text(0.05, 0.95, moment_calc, transform=ax3.transAxes, fontsize=9,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.5))
            
            # 4. การคำนวณแรงเฉือน (subplot 4)
            ax4 = plt.subplot(6, 2, (7, 8))
            ax4.axis('off')
            
            shear_calc = f"""การคำนวณแรงเฉือน (ACI 318):
            
            1. พื้นที่เหล็กปลอก:
               Av = {results['Av']:.3f} ตร.ซม.
            
            2. กำลังรับแรงเฉือนของคอนกรีต:
               Vc = 0.53√f'c × b × d
               Vc = 0.53√{results['fc']:.1f} × {results['B']:.0f} × {results['d']:.0f} = {results['Vc']:.2f} tf
            
            3. กำลังรับแรงเฉือนของเหล็กปลอก:
               Vs = Av×fy×d / s = {results['Av']:.3f}×{results['fy']:.0f}×{results['d']:.0f}/{results['stirrup_spacing']:.0f}
            
            4. กำลังรับแรงเฉือนรวม:
               φVn = φ(Vc + Vs) = {results['phiVn']:.2f} tf
            
            5. ระยะห่างเหล็กปลอกสูงสุด:
               s_max = min(d/2, 600) = {results['s_max']} มม."""
            
            ax4.text(0.05, 0.95, shear_calc, transform=ax4.transAxes, fontsize=9,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.5))
            
            # 5. ผลลัพธ์การตรวจสอบ (subplot 5)
            ax5 = plt.subplot(6, 2, (9, 10))
            ax5.axis('off')
            
            check_results = f"""ผลการตรวจสอบความปลอดภัย:
            
            🔹 โมเมนต์:
               φMn = {results['phiMn']:.2f} tf-m {'≥' if results['moment_adequate'] else '<'} Mu = {results['Mu']:.2f} tf-m
               {'✓ ปลอดภัย' if results['moment_adequate'] else '✗ ไม่ปลอดภัย'}
               อัตราส่วนความปลอดภัย = {results['moment_ratio']:.2f}
            
            🔹 แรงเฉือน:
               φVn = {results['phiVn']:.2f} tf {'≥' if results['shear_adequate'] else '<'} Vu = {results['Vu']:.2f} tf
               {'✓ ปลอดภัย' if results['shear_adequate'] else '✗ ไม่ปลอดภัย'}  
               อัตราส่วนความปลอดภัย = {results['shear_ratio']:.2f}
            
            🎯 สรุปผล:
            {'✅ การออกแบบเหมาะสมและปลอดภัย!' if (results['moment_adequate'] and results['shear_adequate']) else '⚠️ ต้องปรับปรุงการออกแบบ!'}
            
            หมายเหตุ: การคำนวณตามมาตรฐาน ACI 318"""
            
            color = "lightgreen" if (results['moment_adequate'] and results['shear_adequate']) else "lightcoral"
            ax5.text(0.05, 0.95, check_results, transform=ax5.transAxes, fontsize=10,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.5))
            
            # 6. แผนภาพแรงและโมเมนต์ (subplot 6)
            ax6 = plt.subplot(6, 2, (11, 12))
            self.draw_force_diagram(ax6, results)
            
            plt.tight_layout()
            
            # แสดงในแท็บ Visualization
            canvas = FigureCanvas(fig)
            
            # ล้างเนื้อหาเก่าและเพิ่มใหม่ในแท็บ visualization
            plot_widget = self.ui.plot_widget
            if hasattr(plot_widget, 'layout') and plot_widget.layout():
                # ล้างเนื้อหาเก่า
                while plot_widget.layout().count():
                    child = plot_widget.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            else:
                # สร้าง layout ใหม่ถ้าไม่มี
                layout = QtWidgets.QVBoxLayout(plot_widget)
                plot_widget.setLayout(layout)
                
            plot_widget.layout().addWidget(canvas)
            
            # เก็บ figure สำหรับ export PDF
            self.report_figure = fig
            
        except Exception as e:
            print(f"Error generating detailed report: {e}")
            import traceback
            print(traceback.format_exc())
            
    def draw_beam_section(self, ax, results):
        """วาดแผนภาพหน้าตัดคาน"""
        # ตั้งค่าฟอนต์ภาษาไทยสำหรับการวาดภาพ
        try:
            font_used = setup_font_for_pdf()
        except:
            font_used = 'Arial Unicode MS'
            
        ax.clear()
        ax.set_aspect('equal')
        ax.set_title(f'หน้าตัดคาน {results["B"]:.0f}×{results["D"]:.0f} มม.', 
                    fontweight='bold', fontsize=14, fontfamily=font_used)
        
        # ขนาดคาน (แปลงเป็น ซม. สำหรับการแสดงผล)
        B = results['B'] / 10  # มม. -> ซม.
        D = results['D'] / 10  # มม. -> ซม.
        d = results['d'] / 10  # มม. -> ซม. (ความลึกมีประสิทธิภาพที่คำนวณได้)
        
        # คำนวณระยะหุ้มจริงจากข้อมูล
        cover = (D * 10 - results['d']) / 2 / 10  # แปลงเป็น ซม.
        
        # วาดคาน
        beam = Rectangle((0, 0), B, D, linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.7)
        ax.add_patch(beam)
        
        # วาดเหล็กปลอก (stirrups)
        stirrup_dia = self.extract_rebar_diameter(results['stirrup']) / 20  # ทำให้เส้นเล็กลง
        # วาดเหล็กปลอกที่มุมคาน
        stirrup_rect = Rectangle((cover/2, cover/2), B - cover, D - cover, 
                                linewidth=stirrup_dia*5, edgecolor='green', 
                                facecolor='none', linestyle='-', alpha=0.8)
        ax.add_patch(stirrup_rect)
        
        # เส้นมิติ
        ax.plot([0, B], [-2, -2], 'k-', linewidth=1)
        ax.text(B/2, -3, f'b = {results["B"]:.0f} มม.', ha='center', va='top', 
               fontsize=10, fontfamily=font_used)
        ax.plot([-1.5, -1.5], [0, D], 'k-', linewidth=1)
        ax.text(-2.5, D/2, f'h = {results["D"]:.0f} มม.', ha='center', va='center', 
               rotation=90, fontsize=10, fontfamily=font_used)
        
        # วาดเหล็กรับแรงดึง (tension steel)
        main_dia = self.extract_rebar_diameter(results['main_rebar']) / 10  # มม. -> ซม.
        main_num = int(results['main_num'])
        
        if main_num > 0:
            # คำนวณตำแหน่งเหล็กรับแรงดึง - ใช้ระยะหุ้มจริง
            steel_spacing = (B - 2*cover) / (main_num - 1) if main_num > 1 else 0
            y_pos = D - d  # ตำแหน่งเหล็กจากด้านล่าง = D - d
            
            for i in range(main_num):
                x_pos = cover + i * steel_spacing
                circle = plt.Circle((x_pos, y_pos), main_dia/2, color='red', zorder=3)
                ax.add_patch(circle)
                
        # วาดเหล็กรับแรงอัด (compression steel)
        comp_dia = self.extract_rebar_diameter(results['comp_rebar']) / 10  # มม. -> ซม.
        comp_num = int(results['comp_num'])
        
        if comp_num > 0:
            # คำนวณตำแหน่งเหล็ก
            steel_spacing = (B - 2*cover) / (comp_num - 1) if comp_num > 1 else 0
            y_pos = D - cover - comp_dia/2
            
            for i in range(comp_num):
                x_pos = cover + i * steel_spacing
                circle = plt.Circle((x_pos, y_pos), comp_dia/2, color='blue', zorder=3)
                ax.add_patch(circle)
        
        # เส้นระดับ d (ความลึกมีประสิทธิภาพจากด้านบน)
        actual_d_from_top = D - d  # ระยะจากด้านบนของคานถึงระดับ d
        ax.plot([0, B], [actual_d_from_top, actual_d_from_top], 'r--', linewidth=2, alpha=0.8)
        ax.text(B + 0.5, actual_d_from_top, f'd = {results["d"]:.0f} มม. (ความลึกมีประสิทธิภาพ)', 
               ha='left', va='center', fontsize=10, color='red', fontfamily=font_used, weight='bold')
        
        # เพิ่มมิติแสดงระยะ d
        ax.plot([B + 2, B + 2], [0, actual_d_from_top], 'r-', linewidth=1, alpha=0.6)
        ax.plot([B + 1.8, B + 2.2], [0, 0], 'r-', linewidth=1)
        ax.plot([B + 1.8, B + 2.2], [actual_d_from_top, actual_d_from_top], 'r-', linewidth=1)
        
        # Legend - ย้ายไปด้านขวานอกหน้าตัดคาน
        legend_x = B + max(B, D) * 0.15  # ตำแหน่ง x ด้านขวา
        legend_y_start = D * 0.8  # เริ่มจากด้านบน
        legend_spacing = D * 0.15  # ระยะห่างระหว่างรายการ
        
        current_y = legend_y_start
        
        if main_num > 0:
            # วาดจุดสีแดงสำหรับ legend
            ax.plot(legend_x, current_y, 'o', color='red', markersize=8)
            ax.text(legend_x + 1, current_y, f'เหล็กรับแรงดึง: {results["main_rebar"]} จำนวน {main_num} เสน', 
                   ha='left', va='center', fontsize=9, fontfamily=font_used)
            current_y -= legend_spacing
            
        if comp_num > 0:
            # วาดจุดสีน้ำเงินสำหรับ legend
            ax.plot(legend_x, current_y, 'o', color='blue', markersize=8)
            ax.text(legend_x + 1, current_y, f'เหล็กรับแรงอัด: {results["comp_rebar"]} จำนวน {comp_num} เสน', 
                   ha='left', va='center', fontsize=9, fontfamily=font_used)
            current_y -= legend_spacing
            
        # เพิ่มข้อมูลเหล็กปลอก
        ax.plot(legend_x, current_y, 's', color='green', markersize=6, fillstyle='none', markeredgewidth=2)
        ax.text(legend_x + 1, current_y, f'เหล็กปลอก: {results["stirrup"]} {results["stirrup_type"]} @{results["stirrup_spacing"]:.0f} มม.', 
               ha='left', va='center', fontsize=9, fontfamily=font_used)
        
        # ปรับแกน - ขยายด้านขวาเพื่อให้พื้นที่สำหรับ legend
        margin = max(B, D) * 0.1
        ax.set_xlim(-margin, B + max(B, D) * 0.6)  # ขยายด้านขวามากขึ้น
        ax.set_ylim(-margin, D + margin)
        ax.set_xlabel('ระยะทางตามแนวนอน (ซม.)', fontsize=10, fontfamily=font_used)
        ax.set_ylabel('ระยะทางตามแนวตั้ง (ซม.)', fontsize=10, fontfamily=font_used)
        ax.grid(True, alpha=0.3)
        
    def draw_moment_curvature_diagram(self, ax, results):
        """วาดแผนภาพโมเมนต์-ความโค้ง"""
        try:
            font_used = setup_font_for_pdf()
        except:
            font_used = 'Arial Unicode MS'
            
        ax.clear()
        ax.set_title('แผนภาพความสัมพันธ์ระหว่างโมเมนต์และความโค้ง', 
                    fontweight='bold', fontsize=12, fontfamily=font_used)
        
        # สร้างข้อมูลตัวอย่างสำหรับแผนภาพ M-φ
        phi_range = np.linspace(0, 0.01, 100)  # ความโค้ง (1/m)
        
        # คำนวณโมเมนต์แบบง่าย (สำหรับการแสดงผล)
        Mn = float(results['Mn'])
        My = Mn * 0.7  # โมเมนต์ครอบ
        
        # สร้างเส้นโค้ง M-φ แบบง่าย
        M = []
        for p in phi_range:
            if p <= 0.002:  # ช่วงเหล็กยืด
                m = p * (My / 0.002)
            elif p <= 0.006:  # ช่วงการ hardening
                m = My + (p - 0.002) * ((Mn - My) / 0.004)
            else:  # ช่วงหลังจาก ultimate
                m = Mn * (1 - (p - 0.006) * 0.05)
            M.append(max(0, m))
        
        # วาดกราฟ
        ax.plot(phi_range * 1000, M, 'b-', linewidth=2, label=f'M-ϕ สำหรับคาน')
        
        # เส้นแสดงจุดสำคัญ
        ax.axhline(y=My, color='g', linestyle='--', alpha=0.7, label=f'My = {My:.1f} ตัน-ม')
        ax.axhline(y=Mn, color='r', linestyle='--', alpha=0.7, label=f'Mn = {Mn:.1f} ตัน-ม')
        ax.axhline(y=results['Mu'], color='orange', linestyle=':', alpha=0.7, 
                  label=f'Mu = {results["Mu"]:.1f} ตัน-ม (ความตองการ)')
        
        ax.set_xlabel('ความโค้ง ? (×10⁻³ 1/ม)', fontsize=10, fontfamily=font_used)
        ax.set_ylabel('โมเมนต์ M (ตัน-ม)', fontsize=10, fontfamily=font_used)
        ax.legend(prop={'family': font_used, 'size': 9})
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, max(Mn, results['Mu']) * 1.2)
        
    def extract_rebar_diameter(self, rebar_text):
        """แยกเอาขนาดเส้นผ่านศูนย์กลางจากข้อความเหล็ก เช่น '#5(D16)' -> 16"""
        try:
            if 'D' in rebar_text:
                # Extract diameter from format like '#5(D16)' or 'DB16'
                dia_part = rebar_text.split('D')[1].replace(')', '')
                return int(dia_part)
            elif '#' in rebar_text:
                # US rebar sizes - convert to metric
                us_sizes = {
                    '#3': 10, '#4': 13, '#5': 16, '#6': 19,
                    '#7': 22, '#8': 25, '#9': 29, '#10': 32, '#11': 36
                }
                us_key = rebar_text.split('(')[0]
                return us_sizes.get(us_key, 16)  # default to 16mm
            else:
                return 16  # default
        except:
            return 16  # fallback default
        # วาดเหล็กรับแรงดึง (ล่าง)
        main_dia = self.extract_rebar_diameter(results['main_rebar']) / 10  # มม. -> ซม.
        main_num = int(results['main_num'])
        cover = 3  # cm
        
        spacing = (B - 2*cover) / (main_num - 1) if main_num > 1 else 0
        for i in range(main_num):
            x = cover + i * spacing if main_num > 1 else B/2
            y = cover
            circle = Circle((x, y), main_dia/2, color='red', alpha=0.8)
            ax.add_patch(circle)
            rebar_size = self.extract_rebar_diameter(results['main_rebar'])
            ax.text(x, y, f'D{rebar_size}', ha='center', va='center', fontsize=6)
        
        # วาดเหล็กรับแรงอัด (บน) ถ้ามี
        if int(results['comp_num']) > 0:
            comp_dia = self.extract_rebar_diameter(results['comp_rebar']) / 10
            comp_num = int(results['comp_num'])
            spacing = (B - 2*cover) / (comp_num - 1) if comp_num > 1 else 0
            for i in range(comp_num):
                x = cover + i * spacing if comp_num > 1 else B/2
                y = D - cover
                circle = Circle((x, y), comp_dia/2, color='blue', alpha=0.8)
                ax.add_patch(circle)
                comp_rebar_size = self.extract_rebar_diameter(results['comp_rebar'])
                ax.text(x, y, f'D{comp_rebar_size}', ha='center', va='center', fontsize=6)
        
        # วาดเหล็กปลอก
        stirrup_dia = self.extract_rebar_diameter(results['stirrup']) / 10
        
        # แสดงเหล็กปลอกตัวอย่าง
        stirrup_rect = Rectangle((stirrup_dia/2, stirrup_dia/2), 
                                B - stirrup_dia, D - stirrup_dia,
                                linewidth=1.5, edgecolor='green', facecolor='none')
        ax.add_patch(stirrup_rect)
        
        # ขนาดและคำอธิบาย
        ax.text(B/2, -D*0.15, f'B = {results["B"]:.0f} มม.', ha='center', fontweight='bold')
        ax.text(-B*0.15, D/2, f'D = {results["D"]:.0f} มม.', va='center', rotation=90, fontweight='bold')
        ax.text(B + B*0.05, d, f'd = {results["d"]:.0f} มม.', va='center', fontweight='bold')
        
        # เส้นแสดงระยะ d
        ax.plot([B + B*0.02, B + B*0.02], [0, d], 'k--', alpha=0.5)
        ax.plot([B + B*0.015, B + B*0.025], [0, 0], 'k-', alpha=0.5)
        ax.plot([B + B*0.015, B + B*0.025], [d, d], 'k-', alpha=0.5)
        
        # Legend
        main_rebar_display = f'D{self.extract_rebar_diameter(results["main_rebar"])}'
        red_patch = mpatches.Patch(color='red', label=f'เหล็กรับแรงดึง: {main_rebar_display} x {results["main_num"]}')
        if int(results['comp_num']) > 0:
            comp_rebar_display = f'D{self.extract_rebar_diameter(results["comp_rebar"])}'
            blue_patch = mpatches.Patch(color='blue', label=f'เหล็กรับแรงอัด: {comp_rebar_display} x {results["comp_num"]}')
            stirrup_display = f'D{self.extract_rebar_diameter(results["stirrup"])}'
            green_patch = mpatches.Patch(color='green', label=f'เหล็กปลอก: {stirrup_display} @{results["stirrup_spacing"]:.0f}')
            ax.legend(handles=[red_patch, blue_patch, green_patch], loc='upper right', bbox_to_anchor=(1, 1))
        else:
            stirrup_display = f'D{self.extract_rebar_diameter(results["stirrup"])}'
            green_patch = mpatches.Patch(color='green', label=f'เหล็กปลอก: {stirrup_display} @{results["stirrup_spacing"]:.0f}')
            ax.legend(handles=[red_patch, green_patch], loc='upper right', bbox_to_anchor=(1, 1))
        
        ax.set_xlim(-B*0.2, B*1.3)
        ax.set_ylim(-D*0.2, D*1.1)
        ax.grid(True, alpha=0.3)
        
    def draw_force_diagram(self, ax, results):
        """วาดแผนภาพแรงและโมเมนต์"""
        ax.clear()
        ax.set_title('แผนภาพแรงและการกระจายหน่วยแรง', fontweight='bold')
        
        # ตรวจสอบ numpy
        if np is None:
            ax.text(0.5, 0.5, 'ต้องการ numpy สำหรับแผนภาพนี้', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # สร้างข้อมูลตัวอย่างสำหรับแผนภาพ
        L = results.get('beam_length', 6.0)  # ใช้ความยาวคานจากข้อมูล หรือ 6 เมตรถ้าไม่มี
        x = np.linspace(0, L, 100)  # ความยาวตามที่กำหนด
        
        # โมเมนต์ (แบบ parabolic สำหรับ uniform load)
        M_max = results['Mu']  # tf-m (ใช้ค่าจริงที่คำนวณได้)
        moment = M_max * x * (L - x) / (L*L/4)  # สูตรโมเมนต์สำหรับ uniform load
        
        # Plot โมเมนต์
        ax.plot(x, moment, 'b-', linewidth=2, label='Moment (tf-m)')
        ax.axhline(y=results['phiMn'], color='r', linestyle='--', label=f'φMn = {results["phiMn"]:.2f} tf-m')
        ax.fill_between(x, 0, moment, alpha=0.3, color='blue')
        ax.set_ylabel('โมเมนต์ (tf-m)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # เพิ่มข้อความแสดงค่าสูงสุด
        max_idx = np.argmax(moment)
        ax.annotate(f'Mu,max = {M_max:.2f} tf-m', 
                   xy=(x[max_idx], moment[max_idx]), 
                   xytext=(x[max_idx]+1, moment[max_idx]+0.5),
                   arrowprops=dict(arrowstyle='->', color='black'),
                   fontsize=9)
        
        ax.set_xlim(0, L)
        ax.set_xlabel('ระยะตามแนวคาน (ม.)')
    
    def generate_section_diagram(self, results):
        """Generate beam cross-section diagram"""
        try:
            if plt is None:
                self.ui.plot_widget.setText("ต้องการ matplotlib สำหรับแผนภาพ\nกรุณาติดตั้ง: pip install matplotlib")
                return
                
            # Create figure for section diagram
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            
            # Draw beam section
            self.draw_beam_section(ax, results)
            
            # Display in widget
            if FigureCanvas:
                canvas = FigureCanvas(fig)
                
                # Add to visualization tab
                layout = self.ui.plot_widget.layout()
                if layout is None:
                    layout = QtWidgets.QVBoxLayout(self.ui.plot_widget)
                
                # Clear existing widgets
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                
                layout.addWidget(canvas)
            
        except Exception as e:
            print(f"Error generating section diagram: {e}")
            import traceback
            print(traceback.format_exc())
            
            # Show error message in widget
            if hasattr(self.ui, 'plot_widget'):
                error_label = QtWidgets.QLabel(f"เกิดข้อผิดพลาดในการสร้างแผนภาพ:\n{str(e)}")
                error_label.setStyleSheet("color: red; padding: 20px;")
                error_label.setAlignment(QtCore.Qt.AlignCenter)
                
                layout = self.ui.plot_widget.layout()
                if layout is None:
                    layout = QtWidgets.QVBoxLayout(self.ui.plot_widget)
                
                # Clear existing widgets
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
                        
                layout.addWidget(error_label)

    def clear_inputs(self):
        """ล้างข้อมูลทั้งหมด"""
        reply = QMessageBox.question(
            self, 'ยืนยันการล้างข้อมูล', 
            'คุณต้องการล้างข้อมูลทั้งหมดหรือไม่?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear all input fields
            for widget in [self.ui.width, self.ui.depth, self.ui.cover,  # ลบ self.ui.d เพราะคำนวณอัตโนมัติ
                          self.ui.fc, self.ui.fy, self.ui.main_rebar_num, self.ui.comp_rebar_num,
                          self.ui.stirrup_spacing, self.ui.moment, self.ui.shear]:
                widget.clear()
            
            # Reset combo boxes to default
            self.ui.main_rebar_size.setCurrentText('#5(D16)')
            self.ui.comp_rebar_size.setCurrentText('#4(D13)')
            self.ui.stirrup_size.setCurrentText('#3(D10)')
            self.ui.stirrup_type.setCurrentText('เหล็กปลอกสองขา')
            
            # Reset effective depth display
            self.ui.d_display.setText("จะคำนวณจากความสูง - ระยะหุ้ม - ขนาดเหล็ก")
            
            # Clear output areas
            self.ui.results_text.clear()
            self.ui.report_text.clear()
            
            self.ui.statusbar.showMessage("ล้างข้อมูลเรียบร้อย", 2000)
    
    def save_data(self):
        """บันทึกข้อมูลการคำนวณ"""
        try:
            import os
            
            # รวบรวมข้อมูลทั้งหมด
            data = {
                'timestamp': datetime.now().isoformat(),
                'beam_data': {
                    'B': self.ui.width.text(),
                    'D': self.ui.depth.text(),
                    'd': str(self.calculate_effective_depth()),  # ใช้ค่าที่คำนวณอัตโนมัติ
                    'fc': self.ui.fc.text(),
                    'fy': self.ui.fy.text(),
                    'main_rebar': self.ui.main_rebar_size.currentText(),
                    'main_num': self.ui.main_rebar_num.text(),
                    'comp_rebar': self.ui.comp_rebar_size.currentText(),
                    'comp_num': self.ui.comp_rebar_num.text(),
                    'stirrup': self.ui.stirrup_size.currentText(),
                    'stirrup_type': self.ui.stirrup_type.currentText(),
                    'stirrup_spacing': self.ui.stirrup_spacing.text(),
                    'Mu': self.ui.moment.text(),
                    'Vu': self.ui.shear.text()
                },
                'results': self.ui.results_text.toPlainText()
            }
            
            # เลือกที่ตั้งไฟล์
            default_name = f"RC_Beam_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "บันทึกข้อมูล", default_name, "JSON Files (*.json)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "สำเร็จ", f"บันทึกข้อมูลเรียบร้อย\n{file_path}")
                self.ui.statusbar.showMessage(f"บันทึกข้อมูล: {os.path.basename(file_path)}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"ไม่สามารถบันทึกข้อมูลได้:\n{str(e)}")
            print(f"Save data error: {e}")
    
    def load_data(self):
        """โหลดข้อมูลที่บันทึกไว้"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "โหลดข้อมูล", "", "JSON Files (*.json)"
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # ใส่ข้อมูลกลับเข้าไปในฟอร์ม
                beam_data = data.get('beam_data', {})
                
                self.ui.width.setText(beam_data.get('B', ''))
                self.ui.depth.setText(beam_data.get('D', ''))
                # ลบ self.ui.d.setText(beam_data.get('d', '')) - คำนวณอัตโนมัติ
                self.ui.fc.setText(beam_data.get('fc', ''))
                self.ui.fy.setText(beam_data.get('fy', ''))
                self.ui.main_num.setText(beam_data.get('main_num', ''))
                self.ui.comp_num.setText(beam_data.get('comp_num', ''))
                self.ui.stirrup_spacing.setText(beam_data.get('stirrup_spacing', ''))
                self.ui.Mu.setText(beam_data.get('Mu', ''))
                self.ui.Vu.setText(beam_data.get('Vu', ''))
                self.ui.Tu.setText(beam_data.get('Tu', ''))
                
                # Set combo box values
                if beam_data.get('main_rebar'):
                    index = self.ui.main_rebar.findText(beam_data['main_rebar'])
                    if index >= 0:
                        self.ui.main_rebar.setCurrentIndex(index)
                        
                if beam_data.get('comp_rebar'):
                    index = self.ui.comp_rebar.findText(beam_data['comp_rebar'])
                    if index >= 0:
                        self.ui.comp_rebar.setCurrentIndex(index)
                        
                if beam_data.get('stirrup'):
                    index = self.ui.stirrup.findText(beam_data['stirrup'])
                    if index >= 0:
                        self.ui.stirrup.setCurrentIndex(index)
                        
                if beam_data.get('stirrup_type'):
                    index = self.ui.stirrup_type.findText(beam_data['stirrup_type'])
                    if index >= 0:
                        self.ui.stirrup_type.setCurrentIndex(index)
                
                QMessageBox.information(self, "สำเร็จ", "โหลดข้อมูลเรียบร้อย")
                self.ui.statusbar.showMessage("โหลดข้อมูลเรียบร้อย", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"ไม่สามารถโหลดข้อมูลได้:\n{str(e)}")
            print(f"Load data error: {e}")
    
    def export_pdf(self):
        """ส่งออก PDF คุณภาพสูงแบบหลายหน้าพร้อมแผนภาพคาน"""
        try:
            if plt is None:
                QMessageBox.warning(self, "เตือน", "ไม่พบ matplotlib กรุณาติดตั้ง: pip install matplotlib")
                return
                
            if not hasattr(self, 'last_results') or self.last_results is None:
                QMessageBox.warning(self, "เตือน", "กรุณาคำนวณก่อนส่งออก PDF")
                return
                
            import os
            from matplotlib.backends.backend_pdf import PdfPages
            
            # เลือกที่ตั้งไฟล์
            default_name = f"RC_Beam_Report_Enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "บันทึกรายงาน PDF", default_name, "PDF Files (*.pdf)"
            )
            
            if file_path:
                # สร้าง multi-page PDF
                with PdfPages(file_path) as pdf:
                    try:
                        # หน้าที่ 1: ข้อมูลพื้นฐานและแผนภาพคาน
                        fig1 = self.create_pdf_page_1(self.last_results, setup_font_for_pdf())
                        if fig1:
                            pdf.savefig(fig1, bbox_inches='tight', dpi=300)
                            plt.close(fig1)
                        
                        # หน้าที่ 2: การคำนวณโมเมนต์และแรงเฉือน  
                        fig2 = self.create_pdf_page_2(self.last_results, setup_font_for_pdf())
                        if fig2:
                            pdf.savefig(fig2, bbox_inches='tight', dpi=300)
                            plt.close(fig2)
                        
                        # หน้าที่ 3: ผลการตรวจสอบและสรุป
                        fig3 = self.create_pdf_page_3(self.last_results, setup_font_for_pdf())
                        if fig3:
                            pdf.savefig(fig3, bbox_inches='tight', dpi=300)
                            plt.close(fig3)
                        
                        # เก็บข้อมูล metadata
                        d = pdf.infodict()
                        d['Title'] = 'รายงานการคำนวณคาน RC ตามมาตรฐาน ACI 318'
                        d['Author'] = 'RC Beam Analysis Program'
                        d['Subject'] = 'การวิเคราะห์และออกแบบคาน RC'
                        d['Keywords'] = 'RC Beam, ACI 318, Concrete Design'
                        d['Creator'] = 'RC Beam Analysis Program v.1.0'
                        d['Producer'] = 'Enhanced PDF Generator'
                        
                    except Exception as e:
                        print(f"Error generating PDF pages: {e}")
                        # Fallback to single page PDF
                        pdf_fig = self.create_a4_report_figure(self.last_results)
                        if pdf_fig:
                            pdf.savefig(pdf_fig, bbox_inches='tight', dpi=300)
                            plt.close(pdf_fig)
                
                QMessageBox.information(self, "สำเร็จ", f"บันทึกรายงาน PDF คุณภาพสูงแบบหลายหน้าเรียบร้อย\n{file_path}")
                self.ui.statusbar.showMessage(f"ส่งออก Enhanced PDF: {os.path.basename(file_path)}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "ข้อผิดพลาด", f"ไม่สามารถส่งออก PDF ได้:\n{str(e)}")
            print(f"PDF export error: {e}")
            import traceback
            print(traceback.format_exc())
    
    def create_pdf_report_figure(self, results):
        """สร้าง figure ใหม่สำหรับ PDF export"""
        try:
            # สร้าง figure ใหม่
            fig = plt.figure(figsize=(16, 20))
            fig.suptitle('รายงานการคำนวณคาน RC แบบละเอียด', fontsize=16, fontweight='bold', y=0.98)
            
            # 1. ข้อมูลนำเข้า (subplot 1)
            ax1 = plt.subplot(6, 2, (1, 2))
            ax1.axis('off')
            
            input_text = f"""ข้อมูลการออกแบบ:
            
            ขนาดหน้าตัดคาน:
            • ความกว้าง (B) = {results['B']:.0f} มม.
            • ความสูง (D) = {results['D']:.0f} มม.
            • ความลึกมีประสิทธิภาพ (d) = {results['d']:.0f} มม.
            
            คุณสมบัติวัสดุ:
            • กำลังรับแรงอัดคอนกรีต (f'c) = {results['fc']*10.197:.1f} ksc
            • กำลังรับแรงดึงเหล็ก (fy) = {results['fy']*10.197:.1f} ksc
            
            เหล็กเสริม:
            • เหล็กรับแรงดึง: {results['main_rebar']} จำนวน {results['main_num']} เส้น
            • เหล็กรับแรงอัด: {results['comp_rebar']} จำนวน {results['comp_num']} เส้น
            • เหล็กปลอก: {results['stirrup']} {results['stirrup_type']} ระยะ {results['stirrup_spacing']:.0f} มม.
            
            แรงกระทำ:
            • โมเมนต์ (Mu) = {results['Mu']:.2f} tf-m
            • แรงเฉือน (Vu) = {results['Vu']:.2f} tf"""
            
            ax1.text(0.05, 0.95, input_text, transform=ax1.transAxes, fontsize=10,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
            
            # 2. แผนภาพหน้าตัดคาน (subplot 2)
            ax2 = plt.subplot(6, 2, (3, 4))
            self.draw_beam_section(ax2, results)
            
            # 3. สูตรการคำนวณโมเมนต์ (subplot 3)
            ax3 = plt.subplot(6, 2, (5, 6))
            ax3.axis('off')
            
            moment_calc = f"""การคำนวณโมเมนต์ (ACI 318):
            
            1. พื้นที่เหล็กเสริม:
               As = {results['As']:.2f} ตร.ซม. (เหล็กรับแรงดึง)
               A's = {results['Ass']:.2f} ตร.ซม. (เหล็กรับแรงอัด)
            
            2. ความลึกของแกนกลาง:
               c = As×fy / (0.85×f'c×b×β₁) = {results['c']:.2f} ซม.
               β₁ = {results['beta']:.3f}
            
            3. ค่า strain และ φ:
               εs = 0.003×(d-c)/c = {results['es']:.6f}
               εt = 0.003×(dt-c)/c = {results['et']:.6f}
               φ = {results['phi']:.3f}
            
            4. กำลังรับโมเมนต์:
               Cc = 0.85×f'c×a×b = {results['Cc']:.2f} tf
               Cs = fs'×A's = {results['Cs']:.2f} tf
               Mn = As×fy×(d-a/2) + Cs×(d-d') = {results['Mn']:.2f} tf-m
               φMn = {results['phiMn']:.2f} tf-m"""
            
            ax3.text(0.05, 0.95, moment_calc, transform=ax3.transAxes, fontsize=9,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.5))
            
            # 4. การคำนวณแรงเฉือน (subplot 4)
            ax4 = plt.subplot(6, 2, (7, 8))
            ax4.axis('off')
            
            shear_calc = f"""การคำนวณแรงเฉือน (ACI 318):
            
            1. พื้นที่เหล็กปลอก:
               Av = {results['Av']:.3f} ตร.ซม.
            
            2. กำลังรับแรงเฉือนของคอนกรีต:
               Vc = 0.53√f'c × b × d
               Vc = 0.53√{results['fc']:.1f} × {results['B']:.0f} × {results['d']:.0f} = {results['Vc']:.2f} tf
            
            3. กำลังรับแรงเฉือนของเหล็กปลอก:
               Vs = Av×fy×d / s = {results['Av']:.3f}×{results['fy']:.0f}×{results['d']:.0f}/{results['stirrup_spacing']:.0f}
            
            4. กำลังรับแรงเฉือนรวม:
               φVn = φ(Vc + Vs) = {results['phiVn']:.2f} tf
            
            5. ระยะห่างเหล็กปลอกสูงสุด:
               s_max = min(d/2, 600) = {results['s_max']} มม."""
            
            ax4.text(0.05, 0.95, shear_calc, transform=ax4.transAxes, fontsize=9,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.5))
            
            # 5. ผลลัพธ์การตรวจสอบ (subplot 5)
            ax5 = plt.subplot(6, 2, (9, 10))
            ax5.axis('off')
            
            check_results = f"""ผลการตรวจสอบความปลอดภัย:
            
            🔹 โมเมนต์:
               φMn = {results['phiMn']:.2f} tf-m {'≥' if results['moment_adequate'] else '<'} Mu = {results['Mu']:.2f} tf-m
               {'✓ ปลอดภัย' if results['moment_adequate'] else '✗ ไม่ปลอดภัย'}
               อัตราส่วนความปลอดภัย = {results['moment_ratio']:.2f}
            
            🔹 แรงเฉือน:
               φVn = {results['phiVn']:.2f} tf {'≥' if results['shear_adequate'] else '<'} Vu = {results['Vu']:.2f} tf
               {'✓ ปลอดภัย' if results['shear_adequate'] else '✗ ไม่ปลอดภัย'}  
               อัตราส่วนความปลอดภัย = {results['shear_ratio']:.2f}
            
            🎯 สรุปผล:
            {'✅ การออกแบบเหมาะสมและปลอดภัย!' if (results['moment_adequate'] and results['shear_adequate']) else '⚠️ ต้องปรับปรุงการออกแบบ!'}
            
            หมายเหตุ: การคำนวณตามมาตรฐาน ACI 318"""
            
            color = "lightgreen" if (results['moment_adequate'] and results['shear_adequate']) else "lightcoral"
            ax5.text(0.05, 0.95, check_results, transform=ax5.transAxes, fontsize=10,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.5))
            
            # 6. แผนภาพแรงและโมเมนต์ (subplot 6)
            ax6 = plt.subplot(6, 2, (11, 12))
            self.draw_force_diagram(ax6, results)
            
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            print(f"Error creating PDF report figure: {e}")
            return None
    
    def create_a4_report_figure(self, results):
        """สร้าง figure สำหรับ PDF รูปแบบ A4 คุณภาพสูงพร้อมแผนภาพคาน"""
        try:
            # ตั้งค่าฟอนต์ที่รองรับสัญลักษณ์พิเศษสำหรับ PDF
            font_used = setup_font_for_pdf()
            
            # สร้าง multi-page PDF แยกเป็นหลายหน้า
            figures = []
            
            # หน้าที่ 1: ข้อมูลพื้นฐานและแผนภาพคาน
            fig1 = self.create_pdf_page_1(results, font_used)
            if fig1:
                figures.append(fig1)
            
            # หน้าที่ 2: การคำนวณโมเมนต์และแรงเฉือน
            fig2 = self.create_pdf_page_2(results, font_used)
            if fig2:
                figures.append(fig2)
            
            # หน้าที่ 3: ผลการตรวจสอบและสรุป
            fig3 = self.create_pdf_page_3(results, font_used)
            if fig3:
                figures.append(fig3)
            
            # Return first figure (main function expects single figure)
            return figures[0] if figures else None
            
        except Exception as e:
            print(f"Error creating A4 report figure: {e}")
            return None
    
    def create_pdf_page_1(self, results, font_used):
        """สร้างหน้าที่ 1: ข้อมูลพื้นฐานและแผนภาพคาน"""
        try:
            # สร้าง figure ขนาด A4 แนวตั้ง
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.suptitle('รายงานการคำนวณคาน RC ตามมาตรฐาน ACI 318 - หน้าที่ 1/3', 
                        fontsize=16, fontweight='bold', y=0.97, fontfamily=font_used)
            
            # ปรับ layout ให้เหมาะสมกับ A4 - เพิ่มระยะห่างจากชื่อ
            plt.subplots_adjust(left=0.08, right=0.92, top=0.90, bottom=0.08, hspace=0.5)
            
            # ใช้ค่าที่ถูกต้องโดยไม่ต้องแปลงหน่วย
            fc_ksc = results['fc']  # ksc
            fy_ksc = results['fy']  # ksc
            
            # 1. ข้อมูลพื้นฐาน (ย้ายลงมาจากชื่อ)
            ax1 = plt.subplot(3, 1, 1)
            ax1.axis('off')
            
            input_text = f"""ข้อมูลการออกแบบคาน RC:
            
ขนาดหน้าตัดคาน:
• ความกว้าง (B) = {results['B']:.0f} มม.        • ความสูง (D) = {results['D']:.0f} มม.
• ความลึกมีประสิทธิภาพ (d) = {results['d']:.0f} มม. (คำนวณอัตโนมัติ)

คุณสมบัติวัสดุ:
• กำลังรับแรงอัดคอนกรีต (f'c) = {fc_ksc:.1f} กก./ตร.ซม.
• กำลังรับแรงดึงเหล็ก (fy) = {fy_ksc:.0f} กก./ตร.ซม.

เหล็กเสริม:
• เหล็กรับแรงดึง: {results['main_rebar']} จำนวน {results['main_num']} เส้น (As = {results['As']:.2f} ตร.ซม.)
• เหล็กรับแรงอัด: {results['comp_rebar']} จำนวน {results['comp_num']} เส้น (A's = {results['Ass']:.2f} ตร.ซม.)
• เหล็กปลอก: {results['stirrup']} {results['stirrup_type']} ระยะ {results['stirrup_spacing']:.0f} มม. (Av = {results['Av']:.3f} ตร.ซม.)

แรงกระทำ:
• โมเมนต์ (Mu) = {results['Mu']:.2f} ตัน-เมตร        • แรงเฉือน (Vu) = {results['Vu']:.2f} ตัน"""
            
            ax1.text(0.05, 0.95, input_text, transform=ax1.transAxes, fontsize=12,
                    verticalalignment='top', fontfamily=font_used,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="lightblue", alpha=0.7))
            
            # 2. แผนภาพหน้าตัดคาน (ขนาดใหญ่และชัดเจน แต่ไม่ซ้อนทับข้อมูล)
            ax2 = plt.subplot(3, 1, 2)
            self.draw_detailed_beam_section_for_pdf(ax2, results, font_used)
            ax2.set_title('แผนภาพหน้าตัดคาน', 
                         fontsize=14, fontweight='bold', fontfamily=font_used, pad=15)
            
            # 3. ข้อมูลเหล็กเสริม (ย้ายมาไว้ใต้แผนภาพ)
            ax3 = plt.subplot(3, 1, 3)
            ax3.axis('off')
            
            steel_info = f"""ข้อมูลเหล็กเสริมรายละเอียด:

เหล็กรับแรงดึง (Tension Steel):
• ขนาด: {results['main_rebar']} จำนวน {results['main_num']} เส้น
• พื้นที่: As = {results['As']:.2f} ตร.ซม.
• ตำแหน่ง: ด้านล่างของคาน (ระยะ {40} มม. จากขอบ)

เหล็กรับแรงอัด (Compression Steel):
• ขนาด: {results['comp_rebar']} จำนวน {results['comp_num']} เส้น  
• พื้นที่: A's = {results['Ass']:.2f} ตร.ซม.
• ตำแหน่ง: ด้านบนของคาน (ระยะ {40} มม. จากขอบ)

เหล็กปลอก (Stirrups):
• ขนาด: {results['stirrup']} {results['stirrup_type']}
• ระยะห่าง: {results['stirrup_spacing']:.0f} มม.
• พื้นที่: Av = {results['Av']:.3f} ตร.ซม."""
            
            ax3.text(0.05, 0.95, steel_info, transform=ax3.transAxes, fontsize=12,
                    verticalalignment='top', fontfamily=font_used,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", alpha=0.7))
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"Error creating PDF page 1: {e}")
            return None
    
    def draw_detailed_beam_section_for_pdf(self, ax, results, font_used):
        """วาดแผนภาพหน้าตัดคานแบบละเอียดสำหรับ PDF"""
        try:
            # ข้อมูลมิติ
            width = results['B']  # mm
            height = results['D']  # mm
            d = results['d']  # mm
            cover = 40  # default cover
            
            # แปลงเป็น cm สำหรับการแสดงผล
            w_cm = width / 10
            h_cm = height / 10
            d_cm = d / 10
            cover_cm = cover / 10
            
            # ตั้งค่า axis
            ax.set_xlim(-5, w_cm + 5)
            ax.set_ylim(-5, h_cm + 5)
            ax.set_aspect('equal')
            
            # วาดเส้นขอบคาน
            from matplotlib.patches import Rectangle
            beam_rect = Rectangle((0, 0), w_cm, h_cm, linewidth=3, 
                                edgecolor='black', facecolor='lightgray', alpha=0.3)
            ax.add_patch(beam_rect)
            
            # วาดเส้นความลึกมีประสิทธิภาพ
            ax.axhline(y=h_cm-d_cm, xmin=0.1, xmax=0.9, color='red', 
                      linewidth=2, linestyle='--', alpha=0.8)
            
            # วาดเหล็กรับแรงดึง (main reinforcement)
            main_num = results['main_num']
            if main_num > 0:
                main_dia = 16  # default diameter in mm
                main_dia_cm = main_dia / 10
                
                # คำนวณตำแหน่งเหล็ก
                spacing = (w_cm - 2 * cover_cm) / (main_num - 1) if main_num > 1 else 0
                for i in range(main_num):
                    x_pos = cover_cm + i * spacing
                    y_pos = cover_cm
                    
                    circle = plt.Circle((x_pos, y_pos), main_dia_cm/2, 
                                      color='blue', alpha=0.8, linewidth=2)
                    ax.add_patch(circle)
            
            # วาดเหล็กรับแรงอัด (compression reinforcement)
            comp_num = results['comp_num']
            if comp_num > 0:
                comp_dia = 13  # default diameter in mm
                comp_dia_cm = comp_dia / 10
                
                # คำนวณตำแหน่งเหล็ก
                spacing = (w_cm - 2 * cover_cm) / (comp_num - 1) if comp_num > 1 else 0
                for i in range(comp_num):
                    x_pos = cover_cm + i * spacing
                    y_pos = h_cm - cover_cm
                    
                    circle = plt.Circle((x_pos, y_pos), comp_dia_cm/2, 
                                      color='green', alpha=0.8, linewidth=2)
                    ax.add_patch(circle)
            
            # วาดเหล็กปลอก
            stirrup_spacing = results['stirrup_spacing'] / 10  # convert to cm
            stirrup_width = w_cm - 2 * cover_cm
            stirrup_height = h_cm - 2 * cover_cm
            
            # วาดเหล็กปลอกตัวอย่าง
            stirrup_rect = Rectangle((cover_cm, cover_cm), stirrup_width, stirrup_height, 
                                   linewidth=2, edgecolor='orange', facecolor='none', 
                                   linestyle='-', alpha=0.7)
            ax.add_patch(stirrup_rect)
            
            # ใส่ขนาดและป้ายกำกับ
            # ขนาดความกว้าง
            ax.annotate('', xy=(0, -2), xytext=(w_cm, -2), 
                       arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
            ax.text(w_cm/2, -3, f'b = {width:.0f} มม.', ha='center', va='top', 
                   fontsize=12, fontweight='bold', fontfamily=font_used)
            
            # ขนาดความสูง
            ax.annotate('', xy=(-2, 0), xytext=(-2, h_cm), 
                       arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
            ax.text(-3, h_cm/2, f'h = {height:.0f} มม.', ha='center', va='center', 
                   rotation=90, fontsize=12, fontweight='bold', fontfamily=font_used)
            
            # ความลึกมีประสิทธิภาพ
            ax.annotate('', xy=(w_cm + 1, h_cm), xytext=(w_cm + 1, h_cm - d_cm), 
                       arrowprops=dict(arrowstyle='<->', color='red', lw=2))
            ax.text(w_cm + 2, h_cm - d_cm/2, f'd = {d:.0f} มม.\n(คำนวณอัตโนมัติ)', 
                   ha='left', va='center', fontsize=11, fontweight='bold', 
                   color='red', fontfamily=font_used)
            
            # ย้ายข้อมูลเหล็กเสริมไปด้านขวาของแผนภาพแทนการใช้ legend
            # เพื่อไม่ให้ซ้อนทับแผนภาพคาน
            info_x = w_cm + 8  # ตำแหน่ง x ด้านขวาของแผนภาพ
            info_y_start = h_cm  # เริ่มจากด้านบนของแผนภาพ
            
            # ข้อมูลเหล็กรับแรงดึง
            ax.plot(info_x - 1, info_y_start - 5, 'o', color='blue', markersize=8, alpha=0.8)
            ax.text(info_x, info_y_start - 5, f'เหล็กรับแรงดึง: {results["main_rebar"]} จำนวน {main_num} เส้น', 
                   ha='left', va='center', fontsize=10, fontfamily=font_used, color='blue')
            
            # ข้อมูลเหล็กรับแรงอัด
            ax.plot(info_x - 1, info_y_start - 8, 'o', color='green', markersize=8, alpha=0.8)
            ax.text(info_x, info_y_start - 8, f'เหล็กรับแรงอัด: {results["comp_rebar"]} จำนวน {comp_num} เส้น', 
                   ha='left', va='center', fontsize=10, fontfamily=font_used, color='green')
            
            # ข้อมูลเหล็กปลอก
            ax.plot([info_x - 1.5, info_x - 0.5], [info_y_start - 11, info_y_start - 11], 
                   color='orange', linewidth=3, alpha=0.7)
            ax.text(info_x, info_y_start - 11, f'เหล็กปลอก: {results["stirrup"]} ระยะ {stirrup_spacing*10:.0f} มม.', 
                   ha='left', va='center', fontsize=10, fontfamily=font_used, color='orange')
            
            # ข้อมูลความลึกมีประสิทธิภาพ
            ax.plot([info_x - 1.5, info_x - 0.5], [info_y_start - 14, info_y_start - 14], 
                   color='red', linewidth=2, linestyle='--', alpha=0.8)
            ax.text(info_x, info_y_start - 14, f'ความลึกมีประสิทธิภาพ d = {d:.0f} มม.', 
                   ha='left', va='center', fontsize=10, fontfamily=font_used, color='red')
            
            # ปรับขอบเขตของแผนภาพให้เห็นข้อมูลด้านขวา
            ax.set_xlim(-5, w_cm + 35)  # เพิ่มพื้นที่ด้านขวาให้มากขึ้น
            
            # ตั้งชื่อ axes
            ax.set_xlabel('ระยะทางในแนวกว้าง (ซม.)', fontsize=12, fontfamily=font_used)
            ax.set_ylabel('ระยะทางในแนวสูง (ซม.)', fontsize=12, fontfamily=font_used)
            
            # ใส่ grid
            ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
            
        except Exception as e:
            print(f"Error drawing beam section: {e}")
    
    def create_pdf_page_2(self, results, font_used):
        """สร้างหน้าที่ 2: การคำนวณโมเมนต์และแรงเฉือน"""
        try:
            # สร้าง figure ขนาด A4 แนวตั้ง
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.suptitle('รายงานการคำนวณคาน RC ตามมาตรฐาน ACI 318 - หน้าที่ 2/3', 
                        fontsize=16, fontweight='bold', y=0.96, fontfamily=font_used)
            
            # ปรับ layout ให้เหมาะสมกับ A4
            plt.subplots_adjust(left=0.08, right=0.92, top=0.92, bottom=0.08, hspace=0.5)
            
            fc_ksc = results['fc']
            fy_ksc = results['fy']
            
            # 1. การคำนวณโมเมนต์
            ax1 = plt.subplot(2, 1, 1)
            ax1.axis('off')
            
            moment_calc = f"""การคำนวณโมเมนต์ (ACI 318):

1. พื้นที่เหล็กเสริม:
   As = {results['As']:.2f} ตร.ซม. (เหล็กรับแรงดึง)     A's = {results['Ass']:.2f} ตร.ซม. (เหล็กรับแรงอัด)

2. ความลึกของแกนกลาง:
   c = As×fy / (0.85×f'c×b×β₁) = {results['c']:.2f} ซม.     β₁ = {results['beta']:.3f}

3. ค่า strain และ φ:
   εs = 0.003×(d-c)/c = {results['es']:.6f}     φ = {results['phi']:.3f}

4. กำลังรับโมเมนต์:
   Cc = 0.85×f'c×a×b = {results['Cc']:.2f} ตัน
   Mn = As×fy×(d-a/2) + Cs×(d-d') = {results['Mn']:.2f} ตัน-เมตร
   φMn = {results['phi']:.3f}×{results['Mn']:.2f} = {results['phiMn']:.2f} ตัน-เมตร"""
            
            ax1.text(0.05, 0.95, moment_calc, transform=ax1.transAxes, fontsize=12,
                    verticalalignment='top', fontfamily=font_used,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", alpha=0.7))
            
            # 2. การคำนวณแรงเฉือน
            ax2 = plt.subplot(2, 1, 2)
            ax2.axis('off')
            
            shear_calc = f"""การคำนวณแรงเฉือน (ACI 318):

1. พื้นที่เหล็กปลอก:
   Av = {results['Av']:.3f} ตร.ซม.

2. กำลังรับแรงเฉือนของคอนกรีต:
   Vc = 0.53√f'c × b × d = 0.53√{fc_ksc:.1f} × {results['B']:.0f} × {results['d']:.0f} = {results['Vc']:.2f} ตัน

3. กำลังรับแรงเฉือนของเหล็กปลอก:
   Vs = Av×fy×d / s = {results['Av']:.3f}×{fy_ksc:.0f}×{results['d']:.0f}/{results['stirrup_spacing']:.0f}

4. กำลังรับแรงเฉือนรวม:
   φVn = φ(Vc + Vs) = {results['phiVn']:.2f} ตัน

5. ระยะห่างเหล็กปลอกสูงสุด (ตาม ACI 9.7.6.2.2):
   ระยะห่างที่กรอก: s = {results['stirrup_spacing']:.0f} มม.
   ระยะห่างสูงสุดที่อนุญาต (มีสองเงื่อนไข):
   - s_max1 = {results['s_max1']} มม. (ตามมาตรฐาน)
   - s_max2 = d/2 = {results['s_max2']} มม. (ความลึกมีประสิทธิภาพ)
   การตรวจสอบ: {'[OK] เหมาะสม' if results['spacing_adequate'] else '[NG] ไม่เหมาะสม'}
   หมายเหตุ: การคำนวณตาม ACI 318 Table 9.7.6.2.2"""
            
            ax2.text(0.05, 0.95, shear_calc, transform=ax2.transAxes, fontsize=12,
                    verticalalignment='top', fontfamily=font_used,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="lightgreen", alpha=0.7))
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"Error creating PDF page 2: {e}")
            return None
    
    def create_pdf_page_3(self, results, font_used):
        """สร้างหน้าที่ 3: ผลการตรวจสอบความปลอดภัยและสรุป"""
        try:
            # สร้าง figure ขนาด A4 แนวตั้ง
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.suptitle('รายงานการคำนวณคาน RC ตามมาตรฐาน ACI 318 - หน้าที่ 3/3', 
                        fontsize=16, fontweight='bold', y=0.96, fontfamily=font_used)
            
            # ปรับ layout ให้เหมาะสมกับ A4
            plt.subplots_adjust(left=0.08, right=0.92, top=0.92, bottom=0.08, hspace=0.4)
            
            # 1. ผลการตรวจสอบความปลอดภัย (ใช้สัญลักษณ์ที่แสดงได้ใน PDF)
            ax1 = plt.subplot(3, 1, 1)
            ax1.axis('off')
            
            # แก้ไขสัญลักษณ์ให้แสดงผลได้ใน PDF
            moment_check = "ปลอดภัย" if results['moment_adequate'] else "ไม่ปลอดภัย"
            shear_check = "ปลอดภัย" if results['shear_adequate'] else "ไม่ปลอดภัย"
            moment_symbol = "[OK]" if results['moment_adequate'] else "[NG]"
            shear_symbol = "[OK]" if results['shear_adequate'] else "[NG]"
            overall_status = "การออกแบบเหมาะสมและปลอดภัย!" if results['moment_adequate'] and results['shear_adequate'] else "การออกแบบต้องปรับปรุง!"
            overall_color = "lightgreen" if results['moment_adequate'] and results['shear_adequate'] else "lightcoral"
            
            check_results = f"""ผลการตรวจสอบความปลอดภัย:

โมเมนต์:
   φMn = {results['phiMn']:.2f} ตัน-ม {'≥' if results['moment_adequate'] else '<'} Mu = {results['Mu']:.2f} ตัน-ม
   {moment_symbol} {moment_check}     อัตราส่วนความปลอดภัย = {results['moment_ratio']:.2f}

แรงเฉือน:
   φVn = {results['phiVn']:.2f} ตัน {'≥' if results['shear_adequate'] else '<'} Vu = {results['Vu']:.2f} ตัน
   {shear_symbol} {shear_check}     อัตราส่วนความปลอดภัย = {results['shear_ratio']:.2f}

สรุปผลรวม:
{overall_status}"""
            
            ax1.text(0.05, 0.95, check_results, transform=ax1.transAxes, fontsize=14,
                    verticalalignment='top', fontfamily=font_used, weight='bold',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor=overall_color, alpha=0.7))
            
            # 2. ตารางสรุปผล
            ax2 = plt.subplot(3, 1, 2)
            ax2.axis('off')
            
            # สร้างตารางแสดงผล
            table_data = [
                ['รายการตรวจสอบ', 'ค่าออกแบบ', 'ค่าที่กระทำ', 'อัตราส่วน', 'ผลการตรวจสอบ'],
                ['โมเมนต์', f'{results["phiMn"]:.2f} ตัน-ม', f'{results["Mu"]:.2f} ตัน-ม', 
                 f'{results["moment_ratio"]:.2f}', f'{moment_symbol} {moment_check}'],
                ['แรงเฉือน', f'{results["phiVn"]:.2f} ตัน', f'{results["Vu"]:.2f} ตัน', 
                 f'{results["shear_ratio"]:.2f}', f'{shear_symbol} {shear_check}']
            ]
            
            # วาดตาราง
            table = ax2.table(cellText=table_data[1:], colLabels=table_data[0], 
                             cellLoc='center', loc='center', 
                             colWidths=[0.25, 0.2, 0.2, 0.15, 0.2])
            table.auto_set_font_size(False)
            table.set_fontsize(11)
            table.scale(1, 2)
            
            # จัดสีตาราง
            for i in range(len(table_data[0])):
                table[(0, i)].set_facecolor('#34495e')
                table[(0, i)].set_text_props(weight='bold', color='white')
            
            for i in range(1, len(table_data)):
                color = '#d4edda' if (i == 1 and results['moment_adequate']) or (i == 2 and results['shear_adequate']) else '#f8d7da'
                for j in range(len(table_data[0])):
                    table[(i, j)].set_facecolor(color)
            
            # 3. หมายเหตุและข้อมูลเพิ่มเติม (ย้ายมาจากหน้าแรก)
            ax3 = plt.subplot(3, 1, 3)
            ax3.axis('off')
            
            final_notes = f"""หมายเหตุและข้อมูลเพิ่มเติม:

📋 การคำนวณและมาตรฐาน:
• การคำนวณตามมาตรฐาน ACI 318-19 สำหรับคาน RC
• ระบบหน่วย: กิโลกรัม-ตัน-มิลลิเมตร (kg-ton-mm)
• หน่วยที่ใช้: ความยาว (มม., ซม.), แรง (ตัน), โมเมนต์ (ตัน-ม), ความเค้น (กก./ตร.ซม.)

🔤 สัญลักษณ์และความหมาย:
• εs = ค่าการเปลี่ยนรูปในเหล็กรับแรงดึง (strain)
• φ = ตัวคูณลดกำลัง (strength reduction factor) = 0.9 สำหรับโมเมนต์, 0.75 สำหรับแรงเฉือน
• ρ = อัตราส่วนเหล็กเสริม (reinforcement ratio)
• [OK] = ✅ ปลอดภัย, [NG] = ❌ ไม่ปลอดภัย

📐 การคำนวณความลึกมีประสิทธิภาพ:
• d = D - ระยะหุ้ม - ขนาดเหล็กปลอก - ขนาดเหล็กหลัก/2
• ระยะหุ้มมาตรฐาน = 40 มม. (สำหรับสภาพแวดล้อมปกติ)

⚠️ ข้อแนะนำและข้อควรระวัง:
• หากผลการตรวจสอบแสดง [NG] แนะนำให้ปรับปรุงการออกแบบ
• ตรวจสอบความเหมาะสมของขนาดหน้าตัดและปริมาณเหล็กเสริม
• พิจารณาเงื่อนไขการบริการ (serviceability) เพิ่มเติม

📅 ข้อมูลรายงาน:
วันที่สร้างรายงาน: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
สร้างโดย: RC Beam Analysis Program v.1.0 - Enhanced Edition
เวอร์ชัน: ACI 318-19 Compliance"""
            
            ax3.text(0.05, 0.95, final_notes, transform=ax3.transAxes, fontsize=10,
                    verticalalignment='top', fontfamily=font_used, style='italic',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"Error creating PDF page 3: {e}")
            return None
            
            ax1.text(0.05, 0.95, input_text, transform=ax1.transAxes, fontsize=11,
                    verticalalignment='top', fontfamily=font_used,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="lightblue", alpha=0.7))
            
            # 2. การคำนวณโมเมนต์
            ax2 = plt.subplot(5, 1, 2)
            ax2.axis('off')
            
            moment_calc = f"""การคำนวณโมเมนต์ (ACI 318):

1. พื้นที่เหล็กเสริม:
   As = {results['As']:.2f} ตร.ซม. (เหล็กรับแรงดึง)     A's = {results['Ass']:.2f} ตร.ซม. (เหล็กรับแรงอัด)

2. ความลึกของแกนกลาง:
   c = As×fy / (0.85×f'c×b×β₁) = {results['c']:.2f} ซม.     β₁ = {results['beta']:.3f}

3. ค่า strain และ φ:
   εs = 0.003×(d-c)/c = {results['es']:.6f}     φ = {results['phi']:.3f}

4. กำลังรับโมเมนต์:
   Cc = 0.85×f'c×a×b = {results['Cc']:.2f} ตัน
   Mn = As×fy×(d-a/2) + Cs×(d-d') = {results['Mn']:.2f} ตัน-เมตร
   φMn = {results['phi']:.3f}×{results['Mn']:.2f} = {results['phiMn']:.2f} ตัน-เมตร"""
            
            ax2.text(0.05, 0.95, moment_calc, transform=ax2.transAxes, fontsize=11,
                    verticalalignment='top', fontfamily=font_used,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", alpha=0.7))
            
            # 3. การคำนวณแรงเฉือน
            ax3 = plt.subplot(5, 1, 3)
            ax3.axis('off')
            
            shear_calc = f"""การคำนวณแรงเฉือน (ACI 318):

1. พื้นที่เหล็กปลอก:
   Av = {results['Av']:.3f} ตร.ซม.

2. กำลังรับแรงเฉือนของคอนกรีต:
   Vc = 0.53√f'c × b × d = 0.53√{fc_ksc:.1f} × {results['B']:.0f} × {results['d']:.0f} = {results['Vc']:.2f} ตัน

3. กำลังรับแรงเฉือนของเหล็กปลอก:
   Vs = Av×fy×d / s = {results['Av']:.3f}×{fy_ksc:.0f}×{results['d']:.0f}/{results['stirrup_spacing']:.0f}

4. กำลังรับแรงเฉือนรวม:
   φVn = φ(Vc + Vs) = {results['phiVn']:.2f} ตัน

5. ระยะห่างเหล็กปลอกสูงสุด (ตาม ACI 9.7.6.2.2):
   s = {results['stirrup_spacing']:.0f} มม. (ที่กรอก)
   ระยะห่างสูงสุดที่อนุญาต (มีสองเงื่อนไข):
   - s_max1 = {results['s_max1']} มม. (ตามมาตรฐาน)
   - s_max2 = d/2 = {results['s_max2']} มม. (ความลึกมีประสิทธิภาพ)
   การตรวจสอบ: {'✓ เหมาะสม' if results['spacing_adequate'] else '✗ ไม่เหมาะสม'}
   หมายเหตุ: การคำนวณตาม ACI 318 Table 9.7.6.2.2"""
            
            ax3.text(0.05, 0.95, shear_calc, transform=ax3.transAxes, fontsize=11,
                    verticalalignment='top', fontfamily=font_used,
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="lightgreen", alpha=0.7))
            
            # 4. ผลการตรวจสอบความปลอดภัย
            ax4 = plt.subplot(5, 1, 4)
            ax4.axis('off')
            
            moment_status = "✅ ปลอดภัย" if results['moment_adequate'] else "❌ ไม่ปลอดภัย"
            shear_status = "✅ ปลอดภัย" if results['shear_adequate'] else "❌ ไม่ปลอดภัย"
            overall_color = "lightgreen" if results['moment_adequate'] and results['shear_adequate'] else "lightcoral"
            
            check_results = f"""ผลการตรวจสอบความปลอดภัย:

โมเมนต์:
   φMn = {results['phiMn']:.2f} ตัน-ม {'≥' if results['moment_adequate'] else '<'} Mu = {results['Mu']:.2f} ตัน-ม
   {moment_status}     อัตราส่วนความปลอดภัย = {results['moment_ratio']:.2f}

แรงเฉือน:
   φVn = {results['phiVn']:.2f} ตัน {'≥' if results['shear_adequate'] else '<'} Vu = {results['Vu']:.2f} ตัน
   {shear_status}     อัตราส่วนความปลอดภัย = {results['shear_ratio']:.2f}

สรุปผล:
{'✅ การออกแบบเหมาะสมและปลอดภัย!' if results['moment_adequate'] and results['shear_adequate'] else '⚠️ การออกแบบต้องปรับปรุง!'}"""
            
            ax4.text(0.05, 0.95, check_results, transform=ax4.transAxes, fontsize=12,
                    verticalalignment='top', fontfamily=font_used, weight='bold',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor=overall_color, alpha=0.7))
            
            # 5. หมายเหตุและข้อมูลเพิ่มเติม
            ax5 = plt.subplot(5, 1, 5)
            ax5.axis('off')
            
            notes = f"""หมายเหตุและข้อมูลเพิ่มเติม:

• การคำนวณตามมาตรฐาน ACI 318
• หน่วยที่ใช้: ความยาว (มม., ซม.), แรง (ตัน), โมเมนต์ (ตัน-ม), ความเค้น (กก./ตร.ซม.)
• εs = ค่าการเปลี่ยนรูปในเหล็กรับแรงดึง, φ = ตัวคูณลดกำลัง (strength reduction factor)
• ความลึกมีประสิทธิภาพ (d) คำนวณอัตโนมัติจาก: d = D - ระยะหุ้ม - ขนาดเหล็กปลอก - ขนาดเหล็กหลัก/2

วันที่สร้างรายงาน: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
สร้างโดย: RC Beam Analysis Program"""
            
            ax5.text(0.05, 0.95, notes, transform=ax5.transAxes, fontsize=10,
                    verticalalignment='top', fontfamily=font_used, style='italic',
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="lightgray", alpha=0.5))
            
            plt.tight_layout()
            return fig
            
        except Exception as e:
            print(f"Error creating A4 report figure: {e}")
            return None
    
    def create_corrected_pdf_report_figure(self, results):
        """สร้าง figure ใหม่สำหรับ PDF export พร้อมแก้ไขปัญหาภาษา - เวอร์ชันปรับปรุงใหม่"""
        try:
            # ตั้งค่าฟอนต์ที่รองรับสัญลักษณ์พิเศษสำหรับ PDF
            font_used = setup_font_for_pdf()
            
            # สร้าง figure ใหม่ขนาด A4 แนวตั้ง
            fig = plt.figure(figsize=(8.27, 11.69))  # A4 size in inches
            fig.suptitle('รายงานการคำนวณคาน RC แบบละเอียด', fontsize=14, fontweight='bold', 
                        y=0.97, fontfamily=font_used)
            
            # ปรับ layout ให้เหมาะสมกับ A4
            plt.subplots_adjust(left=0.08, right=0.92, top=0.94, bottom=0.06, hspace=0.3, wspace=0.2)
            
            # 1. ข้อมูลนำเข้า (subplot 1)
            ax1 = plt.subplot(6, 2, (1, 2))
            ax1.axis('off')
            
            # ใช้ค่าที่ถูกต้องโดยไม่ต้องแปลงหน่วย (เพราะเป็น ksc อยู่แล้ว)
            fc_display = results['fc']  # ksc
            fy_display = results['fy']  # ksc
            
            input_text = f"""ข้อมูลการออกแบบ:
            
            ขนาดหน้าตัดคาน:
            • ความกว้าง (B) = {results['B']:.0f} มม.
            • ความสูง (D) = {results['D']:.0f} มม.
            • ความลึกมีประสิทธิภาพ (d) = {results['d']:.0f} มม.
            
            คุณสมบัติวัสดุ:
            • กำลังรับแรงอัดคอนกรีต (f'c) = {fc_display:.1f} กก./ตร.ซม.
            • กำลังรับแรงดึงเหล็ก (fy) = {fy_display:.1f} กก./ตร.ซม.
            
            เหล็กเสริม:
            • เหล็กรับแรงดึง: {results['main_rebar']} จำนวน {results['main_num']} เส้น
            • เหล็กรับแรงอัด: {results['comp_rebar']} จำนวน {results['comp_num']} เส้น
            • เหล็กปลอก: {results['stirrup']} {results['stirrup_type']} ระยะ {results['stirrup_spacing']:.0f} มม.
            
            แรงกระทำ:
            • โมเมนต์ (Mu) = {results['Mu']:.2f} ตัน-เมตร
            • แรงเฉือน (Vu) = {results['Vu']:.2f} ตัน"""
            
            ax1.text(0.05, 0.95, input_text, transform=ax1.transAxes, fontsize=11,
                    verticalalignment='top', fontfamily=font_used,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
            
            # 2. แผนภาพหน้าตัดคาน (subplot 2)
            ax2 = plt.subplot(6, 2, (3, 4))
            self.draw_beam_section(ax2, results)
            
            # 3. สูตรการคำนวณโมเมนต์ (subplot 3)
            ax3 = plt.subplot(6, 2, (5, 6))
            ax3.axis('off')
            
            moment_calc = f"""การคำนวณโมเมนต (ACI 318):
            
            1. พื้นที่เหล็กเสริม:
               As = {results['As']:.2f} ตร.ซม. (เหล็กรับแรงดึง)
               A's = {results['Ass']:.2f} ตร.ซม. (เหล็กรับแรงอัด)
            
            2. ความลึกของแกนกลาง:
               c = As×fy / (0.85×f'c×b×β₁) = {results['c']:.2f} ซม.
               β₁ = {results['beta']:.3f}
            
            3. คา strain และ φ:
               εs = 0.003×(d-c)/c = {results['es']:.6f}
               εt = 0.003×(dt-c)/c = {results['et']:.6f}
               φ = {results['phi']:.3f}
            
            4. กำลังรับโมเมนต์:
               Cc = 0.85×f'c×a×b = {results['Cc']*1000:.0f} กก. ({results['Cc']:.2f} ตัน)
               Cs = fs'×A's = {results['Cs']*1000:.0f} กก. ({results['Cs']:.2f} ตัน)
               Mn = As×fy×(d-a/2) + Cs×(d-d') = {results['Mn']:.2f} ตัน-เมตร
               φMn = {results['phiMn']:.2f} ตัน-เมตร"""
            
            ax3.text(0.05, 0.95, moment_calc, transform=ax3.transAxes, fontsize=10,
                    verticalalignment='top', fontfamily=font_used,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.5))
            
            # 4. การคำนวณแรงเฉือน (subplot 4)
            ax4 = plt.subplot(6, 2, (7, 8))
            ax4.axis('off')
            
            shear_calc = f"""การคำนวณแรงเฉือน (ACI 318):
            
            1. พื้นที่เหล็กปลอก:
               Av = {results['Av']:.3f} ตร.ซม.
            
            2. กำลังรับแรงเฉือนของคอนกรีต:
               Vc = 0.53√f'c × b × d
               Vc = 0.53√{fc_display:.1f} × {results['B']:.0f} × {results['d']:.0f} = {results['Vc']*1000:.0f} กก. ({results['Vc']:.2f} ตัน)
            
            3. กำลังรับแรงเฉือนของเหล็กปลอก:
               Vs = Av×fy×d / s = {results['Av']:.3f}×{fy_display:.0f}×{results['d']:.0f}/{results['stirrup_spacing']:.0f}
            
            4. กำลังรับแรงเฉือนรวม:
               φVn = φ(Vc + Vs) = {results['phiVn']*1000:.0f} กก. ({results['phiVn']:.2f} ตัน)
            
            5. ระยะห่างเหล็กปลอกสูงสุด:
               s_max = min(d/2, 600) = {results['s_max']} มม."""
            
            ax4.text(0.05, 0.95, shear_calc, transform=ax4.transAxes, fontsize=10,
                    verticalalignment='top', fontfamily=font_used,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.5))
            
            # 5. ผลลัพธ์การตรวจสอบ (subplot 5)
            ax5 = plt.subplot(6, 2, (9, 10))
            ax5.axis('off')
            
            check_results = f"""ผลการตรวจสอบความปลอดภัย:
            
            โมเมนต์:
               φMn = {results['phiMn']:.2f} ตัน-เมตร {'≥' if results['moment_adequate'] else '<'} Mu = {results['Mu']:.2f} ตัน-เมตร
               {'✓ ปลอดภัย' if results['moment_adequate'] else '✗ ไม่ปลอดภัย'}
            
            แรงเฉือน:
               φVn = {results['phiVn']:.2f} ตัน {'≥' if results['shear_adequate'] else '<'} Vu = {results['Vu']:.2f} ตัน
               {'✓ ปลอดภัย' if results['shear_adequate'] else '✗ ไม่ปลอดภัย'}
            
            ระยะห่างเหล็กปลอก:
               s = {results['stirrup_spacing']:.0f} มม. {'≤' if results['spacing_adequate'] else '>'} s_max = {results['s_max']} มม.
               {'✓ เหมาะสม' if results['spacing_adequate'] else '✗ ไม่เหมาะสม'}"""
            
            ax5.text(0.05, 0.95, check_results, transform=ax5.transAxes, fontsize=11,
                    verticalalignment='top', fontfamily=font_used,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcyan", alpha=0.5))
            
            # ไม่แสดงแผนภาพ - ตามที่ผู้ใช้ร้องขอ
            
            plt.tight_layout()
            plt.subplots_adjust(top=0.95)
            
            return fig
            
        except Exception as e:
            print(f"Error creating PDF figure: {e}")
            import traceback
            print(traceback.format_exc())
            return None
        """สร้าง figure ใหม่สำหรับ PDF export พร้อมแก้ไขปัญหาภาษา"""
        try:
            # ตั้งค่าฟอนต์ภาษาไทยสำหรับ PDF
            font_used = setup_font_used_for_pdf()
            
            # สร้าง figure ใหม่
            fig = plt.figure(figsize=(16, 20))
            fig.suptitle('รายงานการคำนวณคาน RC แบบละเอียด', fontsize=16, fontweight='bold', 
                        y=0.98, fontfamily=font_used)
            
            # 1. ข้อมูลนำเข้า (subplot 1)
            ax1 = plt.subplot(6, 2, (1, 2))
            ax1.axis('off')
            
            # แปลงหน่วยให้ถูกต้องสำหรับการแสดงผล
            fc_ksc = results['fc'] * 10.197  # แปลงเป็น ksc
            fy_ksc = results['fy'] * 10.197  # แปลงเป็น ksc
            
            input_text = f"""ข้อมูลการออกแบบ:
            
            ขนาดหน้าตัดคาน:
            • ความกว้าง (B) = {results['B']:.0f} มม.
            • ความสูง (D) = {results['D']:.0f} มม.
            • ความลึกมีประสิทธิภาพ (d) = {results['d']:.0f} มม.
            
            คุณสมบัติวัสดุ:
            • กำลังรับแรงอัดคอนกรีต (f'c) = {fc_ksc:.1f} กก./ตร.ซม.
            • กำลังรับแรงดึงเหล็ก (fy) = {fy_ksc:.1f} กก./ตร.ซม.
            
            เหล็กเสริม:
            • เหล็กรับแรงดึง: {results['main_rebar']} จำนวน {results['main_num']} เส้น
            • เหล็กรับแรงอัด: {results['comp_rebar']} จำนวน {results['comp_num']} เส้น
            • เหล็กปลอก: {results['stirrup']} {results['stirrup_type']} ระยะ {results['stirrup_spacing']:.0f} มม.
            
            แรงกระทำ:
            • โมเมนต์ (Mu) = {results['Mu']:.2f} ตัน-เมตร
            • แรงเฉือน (Vu) = {results['Vu']:.2f} ตัน"""
            
            ax1.text(0.05, 0.95, input_text, transform=ax1.transAxes, fontsize=11,
                    verticalalignment='top', fontfamily=font_used,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
            
            # 2. แผนภาพหน้าตัดคาน (subplot 2)
            ax2 = plt.subplot(6, 2, (3, 4))
            self.draw_beam_section(ax2, results)
            
            # 3. สูตรการคำนวณโมเมนต์ (subplot 3)
            ax3 = plt.subplot(6, 2, (5, 6))
            ax3.axis('off')
            
            moment_calc = f"""การคำนวณโมเมนต์ (ACI 318):
            
            1. พื้นที่เหล็กเสริม:
               As = {results['As']:.2f} ตร.ซม. (เหล็กรับแรงดึง)
               A's = {results['Ass']:.2f} ตร.ซม. (เหล็กรับแรงอัด)
            
            2. ความลึกของแกนกลาง:
               c = As×fy / (0.85×f'c×b×β₁) = {results['c']:.2f} ซม.
               β₁ = {results['beta']:.3f}
            
            3. ค่า strain และ φ:
               εs = 0.003×(d-c)/c = {results['es']:.6f}
               εt = 0.003×(dt-c)/c = {results['et']:.6f}
               φ = {results['phi']:.3f}
            
            4. กำลังรับโมเมนต์:
               Cc = 0.85×f'c×a×b = {results['Cc']:.2f} tf
               Cs = fs'×A's = {results['Cs']:.2f} tf
               Mn = As×fy×(d-a/2) + Cs×(d-d') = {results['Mn']:.2f} tf-m
               φMn = {results['phiMn']:.2f} tf-m"""
            
            ax3.text(0.05, 0.95, moment_calc, transform=ax3.transAxes, fontsize=9,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.5))
            
            # 4. การคำนวณแรงเฉือน (subplot 4)
            ax4 = plt.subplot(6, 2, (7, 8))
            ax4.axis('off')
            
            shear_calc = f"""การคำนวณแรงเฉือน (ACI 318):
            
            1. พื้นที่เหล็กปลอก:
               Av = {results['Av']:.3f} ตร.ซม.
            
            2. กำลังรับแรงเฉือนของคอนกรีต:
               Vc = 0.53√f'c × b × d
               Vc = 0.53√{fc_ksc:.1f} × {results['B']:.0f} × {results['d']:.0f} = {results['Vc']:.2f} tf
            
            3. กำลังรับแรงเฉือนของเหล็กปลอก:
               Vs = Av×fy×d / s = {results['Av']:.3f}×{fy_ksc:.0f}×{results['d']:.0f}/{results['stirrup_spacing']:.0f}
            
            4. กำลังรับแรงเฉือนรวม:
               φVn = φ(Vc + Vs) = {results['phiVn']:.2f} tf
            
            5. ระยะห่างเหล็กปลอกสูงสุด (ตาม ACI 9.7.6.2.2):
               s = {results['stirrup_spacing']:.0f} มม. (ที่กรอก)
               ระยะห่างสูงสุดที่อนุญาต (มีสองเงื่อนไข):
               - s_max1 = {results['s_max1']} มม. (ตามมาตรฐาน)
               - s_max2 = d/2 = {results['s_max2']} มม. (ความลึกมีประสิทธิภาพ)
               การตรวจสอบ: {'✓ เหมาะสม' if results['spacing_adequate'] else '✗ ไม่เหมาะสม'}
               หมายเหตุ: การคำนวณตาม ACI 318 Table 9.7.6.2.2"""
            
            ax4.text(0.05, 0.95, shear_calc, transform=ax4.transAxes, fontsize=9,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.5))
            
            # 5. ผลลัพธ์การตรวจสอบ (subplot 5)
            ax5 = plt.subplot(6, 2, (9, 10))
            ax5.axis('off')
            
            check_results = f"""ผลการตรวจสอบความปลอดภัย:
            
            🔹 โมเมนต์:
               φMn = {results['phiMn']:.2f} tf-m {'≥' if results['moment_adequate'] else '<'} Mu = {results['Mu']:.2f} tf-m
               {'✓ ปลอดภัย' if results['moment_adequate'] else '✗ ไม่ปลอดภัย'}
               อัตราส่วนความปลอดภัย = {results['moment_ratio']:.2f}
            
            🔹 แรงเฉือน:
               φVn = {results['phiVn']:.2f} tf {'≥' if results['shear_adequate'] else '<'} Vu = {results['Vu']:.2f} tf
               {'✓ ปลอดภัย' if results['shear_adequate'] else '✗ ไม่ปลอดภัย'}  
               อัตราส่วนความปลอดภัย = {results['shear_ratio']:.2f}
            
            🎯 สรุปผล:
            {'✅ การออกแบบเหมาะสมและปลอดภัย!' if (results['moment_adequate'] and results['shear_adequate']) else '⚠️ ต้องปรับปรุงการออกแบบ!'}
            
            หมายเหตุ: การคำนวณตามมาตรฐาน ACI 318"""
            
            color = "lightgreen" if (results['moment_adequate'] and results['shear_adequate']) else "lightcoral"
            ax5.text(0.05, 0.95, check_results, transform=ax5.transAxes, fontsize=10,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.5))
            
            # 6. แผนภาพแรงและโมเมนต์ (subplot 6)
            ax6 = plt.subplot(6, 2, (11, 12))
            self.draw_force_diagram(ax6, results)
            
            plt.tight_layout()
            
            return fig
            
        except Exception as e:
            print(f"Error creating corrected PDF report figure: {e}")
            return None
    
    def show_welcome_message(self):
        """แสดงข้อความต้อนรับ"""
        self.ui.statusbar.showMessage("ยินดีต้อนรับสู่เครื่องคำนวณคาน RC เวอร์ชันปรับปรุง!", 5000)


def main():
    """ฟังก์ชันหลักสำหรับรันโปรแกรม"""
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("RC Beam Calculator - Improved")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("RC Design Tools")
    
    # Apply dark theme (optional)
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f8f9fa;
        }
        QStatusBar {
            background-color: #2c3e50;
            color: white;
            font-size: 12px;
            padding: 4px;
        }
        QTabWidget::pane {
            border: 2px solid #ecf0f1;
            border-radius: 8px;
            background-color: #ffffff;
        }
    """)
    
    # Create and show main window
    window = ImprovedRCBeamCalculator()
    window.show()
    
    # Show about dialog on first run
    QTimer.singleShot(1000, lambda: QMessageBox.information(
        window, "เกี่ยวกับโปรแกรม", 
        """🎯 เครื่องคำนวณคาน RC เวอร์ชันปรับปรุง
        
✨ ฟีเจอร์ใหม่:
• Interface ทันสมัยและใช้งานง่าย
• ตรวจสอบข้อมูลแบบ Real-time  
• แสดงผลแบบ Tabbed Interface
• รายงานผลแบบละเอียด
• รองรับหลายภาษา

💡 เปรียบเทียบกับเวอร์ชันเดิมได้ที่ไฟล์ GUI_COMPARISON.md"""
    ))
    
    return app.exec_()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()

# Additional methods for enhanced PDF generation
def draw_detailed_beam_section_for_pdf(ax, results, font_used):
    """วาดแผนภาพหน้าตัดคานแบบละเอียดสำหรับ PDF"""
    try:
        # ข้อมูลมิติ
        width = results['B']  # mm
        height = results['D']  # mm
        d = results['d']  # mm
        cover = 40  # default cover
        
        # แปลงเป็น cm สำหรับการแสดงผล
        w_cm = width / 10
        h_cm = height / 10
        d_cm = d / 10
        cover_cm = cover / 10
        
        # ตั้งค่า axis
        ax.set_xlim(-5, w_cm + 5)
        ax.set_ylim(-5, h_cm + 5)
        ax.set_aspect('equal')
        
        # วาดเส้นขอบคาน
        from matplotlib.patches import Rectangle
        beam_rect = Rectangle((0, 0), w_cm, h_cm, linewidth=3, 
                            edgecolor='black', facecolor='lightgray', alpha=0.3)
        ax.add_patch(beam_rect)
        
        # วาดเส้นความลึกมีประสิทธิภาพ
        ax.axhline(y=h_cm-d_cm, xmin=0.1, xmax=0.9, color='red', 
                  linewidth=2, linestyle='--', alpha=0.8)
        
        # วาดเหล็กรับแรงดึง (main reinforcement)
        main_num = results['main_num']
        if main_num > 0:
            main_dia = 16  # default diameter in mm
            main_dia_cm = main_dia / 10
            
            # คำนวณตำแหน่งเหล็ก
            spacing = (w_cm - 2 * cover_cm) / (main_num - 1) if main_num > 1 else 0
            for i in range(main_num):
                x_pos = cover_cm + i * spacing
                y_pos = cover_cm
                
                circle = plt.Circle((x_pos, y_pos), main_dia_cm/2, 
                                  color='blue', alpha=0.8, linewidth=2)
                ax.add_patch(circle)
        
        # วาดเหล็กรับแรงอัด (compression reinforcement)
        comp_num = results['comp_num']
        if comp_num > 0:
            comp_dia = 13  # default diameter in mm
            comp_dia_cm = comp_dia / 10
            
            # คำนวณตำแหน่งเหล็ก
            spacing = (w_cm - 2 * cover_cm) / (comp_num - 1) if comp_num > 1 else 0
            for i in range(comp_num):
                x_pos = cover_cm + i * spacing
                y_pos = h_cm - cover_cm
                
                circle = plt.Circle((x_pos, y_pos), comp_dia_cm/2, 
                                  color='green', alpha=0.8, linewidth=2)
                ax.add_patch(circle)
        
        # วาดเหล็กปลอก
        stirrup_spacing = results['stirrup_spacing'] / 10  # convert to cm
        stirrup_width = w_cm - 2 * cover_cm
        stirrup_height = h_cm - 2 * cover_cm
        
        # วาดเหล็กปลอกตัวอย่าง
        stirrup_rect = Rectangle((cover_cm, cover_cm), stirrup_width, stirrup_height, 
                               linewidth=2, edgecolor='orange', facecolor='none', 
                               linestyle='-', alpha=0.7)
        ax.add_patch(stirrup_rect)
        
        # ใส่ขนาดและป้ายกำกับ
        # ขนาดความกว้าง
        ax.annotate('', xy=(0, -2), xytext=(w_cm, -2), 
                   arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
        ax.text(w_cm/2, -3, f'b = {width:.0f} มม.', ha='center', va='top', 
               fontsize=12, fontweight='bold', fontfamily=font_used)
        
        # ขนาดความสูง
        ax.annotate('', xy=(-2, 0), xytext=(-2, h_cm), 
                   arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
        ax.text(-3, h_cm/2, f'h = {height:.0f} มม.', ha='center', va='center', 
               rotation=90, fontsize=12, fontweight='bold', fontfamily=font_used)
        
        # ความลึกมีประสิทธิภาพ
        ax.annotate('', xy=(w_cm + 1, h_cm), xytext=(w_cm + 1, h_cm - d_cm), 
                   arrowprops=dict(arrowstyle='<->', color='red', lw=2))
        ax.text(w_cm + 2, h_cm - d_cm/2, f'd = {d:.0f} มม.\n(คำนวณอัตโนมัติ)', 
               ha='left', va='center', fontsize=11, fontweight='bold', 
               color='red', fontfamily=font_used)
        
        # คำอธิบาย
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', 
                      markersize=10, label=f'เหล็กรับแรงดึง: {results["main_rebar"]} จำนวน {main_num} เส้น'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', 
                      markersize=10, label=f'เหล็กรับแรงอัด: {results["comp_rebar"]} จำนวน {comp_num} เส้น'),
            plt.Line2D([0], [0], color='orange', linewidth=3, 
                      label=f'เหล็กปลอก: {results["stirrup"]} ระยะ {stirrup_spacing*10:.0f} มม.'),
            plt.Line2D([0], [0], color='red', linewidth=2, linestyle='--', 
                      label=f'ความลึกมีประสิทธิภาพ d = {d:.0f} มม.')
        ]
        
        ax.legend(handles=legend_elements, loc='upper right', 
                 fontsize=10, fontfamily=font_used, framealpha=0.9)
        
        # ตั้งชื่อ axes
        ax.set_xlabel('ระยะทางในแนวกว้าง (ซม.)', fontsize=12, fontfamily=font_used)
        ax.set_ylabel('ระยะทางในแนวสูง (ซม.)', fontsize=12, fontfamily=font_used)
        
        # ใส่ grid
        ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
        
    except Exception as e:
        print(f"Error drawing beam section: {e}")

