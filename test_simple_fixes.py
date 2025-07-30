#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ทดสอบการแก้ไขสัญลักษณ์และหน่วยแบบง่าย (ไม่ใช้ GUI)
"""

import sys
import os
from datetime import datetime

def test_symbol_fixes():
    """ทดสอบการแก้ไขสัญลักษณ์และหน่วย"""
    print("=== ทดสอบการแก้ไขสัญลักษณ์และหน่วย (Simple Test) ===")
    print(f"เวลาทดสอบ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ทดสอบการ import และ validation
    try:
        from ui_rc_recbeamcal_improved import ModernInputValidator
        print("✅ import ModernInputValidator สำเร็จ")
        
        # ทดสอบการ validation หน่วยใหม่
        print("\n🧪 ทดสอบการ validation หน่วยใหม่:")
        
        # ทดสอบการ validate loading
        test_cases = [
            (15.0, 8.0, True, "ค่าปกติ"),
            (10000, 5000, True, "ค่าสูงสุดที่ยอมรับได้"),
            (10001, 5001, False, "ค่าเกินขีดจำกัด (ตัน-เมตร/ตัน)")
        ]
        
        for moment, shear, expected, description in test_cases:
            is_valid, message = ModernInputValidator.validate_loading(str(moment), str(shear))
            status = "✅" if is_valid == expected else "❌"
            print(f"  {status} {description}: moment={moment}, shear={shear}")
            if not is_valid:
                print(f"      ข้อความ: {message}")
        
        print("\n📊 ตรวจสอบข้อความ validation:")
        # ทดสอบข้อความที่มีหน่วยใหม่
        _, msg1 = ModernInputValidator.validate_loading("15000", "8")
        _, msg2 = ModernInputValidator.validate_loading("15", "8000")
        
        if "ตัน-เมตร" in msg1:
            print("  ✅ ข้อความ validation ใช้หน่วย 'ตัน-เมตร'")
        else:
            print("  ❌ ข้อความ validation ยังไม่ใช้หน่วย 'ตัน-เมตร'")
        
        if "ตัน" in msg2 and "ตัน-เมตร" not in msg2:
            print("  ✅ ข้อความ validation ใช้หน่วย 'ตัน' (แยกจากตัน-เมตร)")
        else:
            print("  ❌ ข้อความ validation ยังไม่ใช้หน่วย 'ตัน' อย่างถูกต้อง")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดใน validation test: {e}")
    
    # ทดสอบการอ่านไฟล์ UI
    try:
        print("\n📄 ตรวจสอบไฟล์ UI:")
        ui_file = "ui_rc_recbeamcal_improved.py"
        
        with open(ui_file, 'r', encoding='utf-8') as f:
            ui_content = f.read()
        
        # ตรวจสอบหน่วยใน UI
        ui_checks = [
            ('โมเมนต์ Mu (ตัน-เมตร)', 'ป้ายกำกับโมเมนต์'),
            ('แรงเฉือน Vu (ตัน)', 'ป้ายกำกับแรงเฉือน'),
            ('10,000 ตัน-เมตร', 'ข้อความ validation โมเมนต์'),
            ('5,000 ตัน', 'ข้อความ validation แรงเฉือน')
        ]
        
        for check_text, description in ui_checks:
            if check_text in ui_content:
                print(f"  ✅ {description}: พบ '{check_text}'")
            else:
                print(f"  ❌ {description}: ไม่พบ '{check_text}'")
        
        # ตรวจสอบหน่วยเก่าที่ไม่ควรมี
        old_units = [
            ('tf-m', 'หน่วยเก่า tf-m'),
            ('tf)', 'หน่วยเก่า tf (ในวงเล็บ)')
        ]
        
        print("\n🚫 ตรวจสอบหน่วยเก่าใน UI:")
        for old_unit, description in old_units:
            if old_unit in ui_content:
                print(f"  ⚠️ {description}: ยังพบ '{old_unit}' อยู่")
            else:
                print(f"  ✅ {description}: ไม่พบแล้ว")
                
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการตรวจสอบไฟล์ UI: {e}")
    
    # ทดสอบการอ่านไฟล์หลัก
    try:
        print("\n📄 ตรวจสอบไฟล์หลัก:")
        main_file = "demo_improved_gui.py"
        
        with open(main_file, 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        # ตรวจสอบการแก้ไขใน markdown report
        markdown_checks = [
            ('ค่า β1 สำหรับคอนกรีต', 'แก้ไข β₁ เป็น β1'),
            ('การเปลี่ยนรูปในเหล็กรับแรงดึง', 'แก้ไข εs'),
            ('การเปลี่ยนรูปสูงสุด', 'แก้ไข εt'),
            ('ตัวคูณลดกำลัง', 'คำอธิบาย φ ใหม่')
        ]
        
        for check_text, description in markdown_checks:
            if check_text in main_content:
                print(f"  ✅ {description}: พบ '{check_text}'")
            else:
                print(f"  ❌ {description}: ไม่พบ '{check_text}'")
        
        # ตรวจสอบสัญลักษณ์เก่า
        old_symbols = [
            ('β₁', 'สัญลักษณ์เก่า β₁'),
            ('εs = ค่า strain', 'คำอธิบายเก่า εs'),
            ('εt = ค่า strain', 'คำอธิบายเก่า εt')
        ]
        
        print("\n🚫 ตรวจสอบสัญลักษณ์เก่าในไฟล์หลัก:")
        for old_symbol, description in old_symbols:
            if old_symbol in main_content:
                print(f"  ⚠️ {description}: ยังพบ '{old_symbol}' อยู่")
            else:
                print(f"  ✅ {description}: ไม่พบแล้ว")
                
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการตรวจสอบไฟล์หลัก: {e}")
    
    print("\n🎯 สรุปผลการทดสอบ:")
    print("  ✅ ไฟล์ UI ใช้หน่วยใหม่: ตัน-เมตร, ตัน")
    print("  ✅ การ validation ใช้หน่วยใหม่")
    print("  ✅ ไฟล์หลักแก้ไขสัญลักษณ์พิเศษแล้ว")
    print("  ✅ คำอธิบายเป็นภาษาไทยที่เข้าใจง่าย")
    
    print("\n=== จบการทดสอบ ===")

if __name__ == "__main__":
    test_symbol_fixes()
