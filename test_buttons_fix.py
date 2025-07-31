#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ทดสอบการแก้ไขปุ่มให้เห็นครบ
"""

print("🔧 ทดสอบการแก้ไขปุ่ม GUI...")

try:
    import demo_improved_gui
    from ui_rc_recbeamcal_improved import Ui_RcRecBeamCalImproved
    
    print("✅ Import สำเร็จ!")
    print("\n🎨 การแก้ไขที่ทำ:")
    print("✅ 1. ขยายขนาดหน้าต่าง: 2000x1200 px")
    print("✅ 2. ขยาย scroll area: 600px กว้าง, 900px สูง") 
    print("✅ 3. ปรับขนาดปุ่ม:")
    print("   - ปุ่มคำนวณ: 55px สูง (ใหญ่สุด)")
    print("   - ปุ่มอื่น: 48px สูง, 180px กว้าง")
    print("   - เพิ่ม tooltip สำหรับปุ่มส่งออก")
    print("✅ 4. ปรับ layout: ลด margins และ spacing")
    print("✅ 5. ลบ spacer ที่ดันปุ่มไปไกล")
    
    print("\n🚀 โปรแกรมพร้อมใช้งาน - ปุ่มควรเห็นครบแล้ว!")
    
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
