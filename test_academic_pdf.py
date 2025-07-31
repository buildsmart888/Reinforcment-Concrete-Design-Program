#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ทดสอบการสร้าง PDF รูปแบบวิชาการใหม่
"""

import sys
import os
from demo_improved_gui import ImprovedRCBeamCalculator

# สร้างข้อมูลทดสอบ
test_results = {
    'B': 300,
    'D': 500, 
    'd': 442,
    'fc': 240,
    'fy': 4000,
    'As': 11.88,
    'Ass': 2.53,
    'Av': 1.427,
    'main_rebar': '#5(D16)',
    'main_num': 6,
    'comp_rebar': '#4(D13)',
    'comp_num': 2,
    'stirrup': '#3(D10)',
    'stirrup_type': 'เหล็กปลอกสองขา',
    'stirrup_spacing': 100,
    'Mu': 15.0,
    'Vu': 8.0,
    'c': 8.27,
    'beta': 0.850,
    'es': 0.012805,
    'phi': 0.900,
    'Cc': 43021.85,
    'Mn': 18.95,
    'phiMn': 17.05,
    'Vc': 10.73,
    'phiVn': 26.70,
    'moment_adequate': True,
    'shear_adequate': True,
    'moment_ratio': 1.14,
    'shear_ratio': 3.34
}

def main():
    print("🔄 เริ่มทดสอบการสร้าง PDF รูปแบบวิชาการใหม่...")
    
    try:
        app = QtWidgets.QApplication(sys.argv)
        calculator = ImprovedRCBeamCalculator()
        
        # ทดสอบสร้าง PDF
        print("📄 กำลังสร้าง PDF...")
        figures = []
        
        from demo_improved_gui import setup_font_for_pdf
        font_used = setup_font_for_pdf()
        
        # หน้า 1
        fig1 = calculator.create_pdf_page_1(test_results, font_used)
        if fig1:
            figures.append(fig1)
            print("✅ สร้างหน้า 1 สำเร็จ")
        
        # หน้า 2  
        fig2 = calculator.create_pdf_page_2(test_results, font_used)
        if fig2:
            figures.append(fig2)
            print("✅ สร้างหน้า 2 สำเร็จ")
            
        # หน้า 3
        fig3 = calculator.create_pdf_page_3(test_results, font_used)
        if fig3:
            figures.append(fig3)
            print("✅ สร้างหน้า 3 สำเร็จ")
        
        print(f"📊 สร้าง PDF สำเร็จ {len(figures)} หน้า")
        print("🎯 การทดสอบเสร็จสิ้น!")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("✨ การทดสอบ PDF รูปแบบวิชาการสำเร็จ!")
    else:
        print("⚠️ การทดสอบไม่สำเร็จ")
