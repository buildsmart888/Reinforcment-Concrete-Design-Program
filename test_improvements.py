#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ทดสอบการปรับปรุงโปรแกรม RC Design
ทดสอบการแสดงผลภาษาไทย และหน่วยที่ถูกต้อง
"""

import sys
import os
from datetime import datetime

# เพิ่ม path สำหรับ import โมดูล
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rc_recbeamcal_base import RcRecBeamCalBase

def test_calculation():
    """ทดสอบการคำนวณและการแสดงผล"""
    print("=== ทดสอบการปรับปรุงโปรแกรม RC Design ===")
    print(f"เวลาทดสอบ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # สร้าง instance ของ calculator
    calc = RcRecBeamCalBase()
    
    # กำหนดข้อมูลทดสอบ
    test_data = {
        'B': 300,          # ความกว้างคาน (มม.)
        'D': 500,          # ความสูงคาน (มม.)
        'd': 450,          # ความลึกมีประสิทธิภาพ (มม.)
        'fc': 245,         # กำลังรับแรงอัดคอนกรีต (ksc)
        'fy': 4000,        # กำลังรับแรงดึงเหล็ก (ksc)
        'main_rebar': '#5(D16)',
        'main_num': 4,
        'comp_rebar': '#4(D13)',
        'comp_num': 2,
        'stirrup': '#3(D10)',
        'stirrup_type': 'เหล็กปลอกสองขา',
        'stirrup_spacing': 150,
        'Mu': 15.0,        # โมเมนต์ (ตัน-เมตร)
        'Vu': 8.0          # แรงเฉือน (ตัน)
    }
    
    print("ข้อมูลนำเข้า:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    print()
    
    try:
        # ทำการคำนวณ
        print("กำลังคำนวณ...")
        results = calc.calculate_all(test_data)
        
        if results:
            print("✅ การคำนวณสำเร็จ!")
            print()
            
            # แสดงผลลัพธ์สำคัญ
            print("ผลลัพธ์สำคัญ:")
            print(f"  • gMn = {results.get('phiMn', 0):.2f} ตัน-เมตร")
            print(f"  • gVn = {results.get('phiVn', 0):.2f} ตัน")
            print(f"  • โมเมนต์ปลอดภัย: {'✅' if results.get('moment_adequate', False) else '❌'}")
            print(f"  • แรงเฉือนปลอดภัย: {'✅' if results.get('shear_adequate', False) else '❌'}")
            print()
            
            # ทดสอบการสร้าง markdown report
            print("ทดสอบการสร้าง Markdown Report...")
            
            # Import ฟังก์ชันจากไฟล์หลัก
            sys.path.append('.')
            from demo_improved_gui import generate_markdown_report
            
            markdown_report = generate_markdown_report(results)
            
            if markdown_report:
                print("✅ สร้าง Markdown Report สำเร็จ!")
                print(f"ความยาวรายงาน: {len(markdown_report)} ตัวอักษร")
                
                # บันทึกรายงานลงไฟล์
                report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_report)
                print(f"บันทึกรายงานที่: {report_file}")
                
                # แสดงส่วนหัวของรายงาน
                print("\nส่วนหัวของรายงาน:")
                print(markdown_report[:500] + "...")
                
            else:
                print("❌ ไม่สามารถสร้าง Markdown Report ได้")
            
        else:
            print("❌ การคำนวณไม่สำเร็จ")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        import traceback
        print(traceback.format_exc())
    
    print("\n=== จบการทดสอบ ===")

if __name__ == "__main__":
    test_calculation()
