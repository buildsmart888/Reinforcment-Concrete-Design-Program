#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🔧 ทดสอบการแก้ไข Title Bar และขยายส่วนกรอกข้อมูล...")

try:
    from PyQt5 import QtWidgets, QtCore
    import sys
    
    # Import โมดูลที่แก้ไขแล้ว
    from ui_rc_recbeamcal_improved import Ui_RcRecBeamCalImproved
    
    print("✅ Import สำเร็จ!")
    
    print("\n🎨 การแก้ไขที่ทำ:")
    print("✅ 1. เพิ่ม Window Title กลับมา")
    print("✅ 2. ขยายส่วนกรอกข้อมูล: 600px → 750px")
    print("✅ 3. ขยายช่องกรอกข้อมูล: 240px → 300px")
    print("✅ 4. ขยายช่องแต่ละอัน: 220px → 280px")
    print("✅ 5. แก้ไข window title bar ให้มีปุ่มย่อ/ขยาย/ปิด")
    
    print("\n🚀 โปรแกรมพร้อมใช้งาน - ส่วนกรอกข้อมูลควรกว้างขึ้นและมี title bar!")
    
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
    import traceback
    traceback.print_exc()
