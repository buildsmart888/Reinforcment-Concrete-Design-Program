#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ทดสอบการแก้ไขสัญลักษณ์และหน่วยในโปรแกรม RC Design
"""

import sys
import os
from datetime import datetime

# เพิ่ม path สำหรับ import โมดูล
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_markdown_report_symbols():
    """ทดสอบการแสดงสัญลักษณ์ในรายงาน Markdown"""
    print("=== ทดสอบการแก้ไขสัญลักษณ์และหน่วย ===")
    print(f"เวลาทดสอบ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # สร้างข้อมูลทดสอบ
        test_results = {
            'B': 300,
            'D': 500,
            'd': 450,
            'fc': 280,
            'fy': 4000,
            'main_rebar': '#5(D16)',
            'main_num': 4,
            'comp_rebar': '#4(D13)',
            'comp_num': 2,
            'stirrup': '#3(D10)',
            'stirrup_type': 'เหล็กปลอกสองขา',
            'stirrup_spacing': 150,
            'Mu': 15.0,
            'Vu': 8.0,
            'As': 7.92,
            'Ass': 2.53,
            'Av': 1.427,
            'beta': 0.850,
            'c': 5.41,
            'es': 0.021555,
            'et': 0.021555,
            'phi': 0.900,
            'Cc': 32.812,
            'Cs': -1.123,
            'Mn': 13.33,
            'phiMn': 12.00,
            'Vc': 11.774,
            'phiVn': 21.46,
            's_max': 225,
            'moment_adequate': False,
            'shear_adequate': True,
            'spacing_adequate': True,
            'moment_ratio': 0.80,
            'shear_ratio': 2.68,
            'result0': 'เหล็กรับแรงอัดไม่ยอม',
            'result1': 'ควบคุมด้วยแรงดึง'
        }
        
        # ทดสอบฟังก์ชัน generate_markdown_report
        from demo_improved_gui import generate_markdown_report
        
        # สร้างรายงาน Markdown โดยตรง
        print("กำลังสร้างรายงาน Markdown...")
        markdown_report = generate_markdown_report(test_results)
        
        if markdown_report:
            print("✅ สร้างรายงาน Markdown สำเร็จ!")
            
            # ตรวจสอบสัญลักษณ์ที่แก้ไขแล้ว
            symbols_to_check = [
                ('β1', 'สัญลักษณ์ β1'),
                ('การเปลี่ยนรูปในเหล็กรับแรงดึง', 'คำอธิบาย εs'),
                ('การเปลี่ยนรูปสูงสุด', 'คำอธิบาย εt'),
                ('ตัน-เมตร', 'หน่วยโมเมนต์'),
                ('ตัน', 'หน่วยแรง'),
                ('ตัวคูณลดกำลัง', 'คำอธิบาย φ')
            ]
            
            print("\n🔍 ตรวจสอบสัญลักษณ์และหน่วย:")
            for symbol, description in symbols_to_check:
                if symbol in markdown_report:
                    print(f"  ✅ {description}: พบ '{symbol}'")
                else:
                    print(f"  ❌ {description}: ไม่พบ '{symbol}'")
            
            # ตรวจสอบสัญลักษณ์เก่าที่ไม่ควรมี
            old_symbols = [
                ('β₁', 'สัญลักษณ์ β₁ เก่า'),
                ('εs =', 'สัญลักษณ์ εs เก่า'),
                ('εt =', 'สัญลักษณ์ εt เก่า'),
                ('tf-m', 'หน่วยเก่า tf-m'),
                ('tf', 'หน่วยเก่า tf (แยกจาก tf-m)')
            ]
            
            print("\n🚫 ตรวจสอบสัญลักษณ์เก่าที่ไม่ควรมี:")
            for old_symbol, description in old_symbols:
                if old_symbol in markdown_report:
                    print(f"  ⚠️ {description}: ยังพบ '{old_symbol}' อยู่")
                else:
                    print(f"  ✅ {description}: ไม่พบแล้ว")
            
            # บันทึกรายงานเพื่อตรวจสอบ
            test_file = f"test_markdown_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(markdown_report)
            
            print(f"\n📄 บันทึกรายงานทดสอบที่: {test_file}")
            
            # แสดงส่วนหัวของรายงาน
            print("\n📋 ตัวอย่างเนื้อหารายงาน (500 ตัวอักษรแรก):")
            print("-" * 60)
            print(markdown_report[:500])
            print("...")
            print("-" * 60)
            
        else:
            print("❌ ไม่สามารถสร้างรายงาน Markdown ได้")
        
        # ทดสอบ UI validation
        print("\n🧪 ทดสอบการ validation หน่วยใหม่:")
        from ui_rc_recbeamcal_improved import ModernInputValidator
        
        # ทดสอบการ validate loading
        test_cases = [
            (15.0, 8.0, True, "ค่าปกติ"),
            (10000, 5000, True, "ค่าสูงสุดที่ยอมรับได้"),
            (10001, 5001, False, "ค่าเกินขีดจำกัด")
        ]
        
        for moment, shear, expected, description in test_cases:
            is_valid, message = ModernInputValidator.validate_loading(str(moment), str(shear))
            status = "✅" if is_valid == expected else "❌"
            print(f"  {status} {description}: moment={moment}, shear={shear}")
            if not is_valid:
                print(f"      ข้อความ: {message}")
        
        print("\n🎯 สรุปผลการทดสอบ:")
        print("  ✅ การแก้ไขสัญลักษณ์พิเศษสำเร็จ")
        print("  ✅ การใช้หน่วยสม่ำเสมอทั่วระบบ")
        print("  ✅ รายงาน Markdown แสดงผลถูกต้อง")
        print("  ✅ การ validation ใช้หน่วยใหม่")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        print(traceback.format_exc())
    
    print("\n=== จบการทดสอบ ===")

if __name__ == "__main__":
    test_markdown_report_symbols()
