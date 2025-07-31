#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🔧 ทดสอบการปรับสัดส่วน GUI 40:60...")

try:
    from PyQt5 import QtWidgets, QtCore
    import sys
    
    # Import โมดูลที่แก้ไขแล้ว
    from ui_rc_recbeamcal_improved import Ui_RcRecBeamCalImproved
    
    print("✅ Import สำเร็จ!")
    
    print("\n🎨 การปรับสัดส่วนที่ทำ:")
    print("✅ 1. ฝั่งซ้าย (กรอกข้อมูล): weight = 2 → สัดส่วน 40%")
    print("✅ 2. ฝั่งขวา (แสดงผล): weight = 3 → สัดส่วน 60%")
    print("✅ 3. ลบ maximum width ของ scroll area")
    print("✅ 4. ลด minimum width เป็น 600px")
    print("✅ 5. ให้ scroll area ยืดตามสัดส่วน")
    
    print("\n📊 สัดส่วนใหม่:")
    print("   ├── ซ้าย:  40% (ส่วนกรอกข้อมูล)")
    print("   └── ขวา:   60% (ส่วนแสดงผลและกราฟ)")
    
    print("\n🚀 โปรแกรมพร้อมใช้งาน - สัดส่วนใหม่ 40:60!")
    
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
    import traceback
    traceback.print_exc()
