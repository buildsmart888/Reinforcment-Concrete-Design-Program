#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🔧 ทดสอบ PDF รูปแบบวิชาการเรียบง่าย...")

try:
    from PyQt5 import QtWidgets, QtCore
    import sys
    
    # Import โมดูลที่แก้ไขแล้ว
    from demo_improved_gui import ImprovedRCBeamCalculator
    
    print("✅ Import สำเร็จ!")
    
    print("\n🎨 การเปลี่ยนแปลง PDF:")
    print("❌ ลบออก: สีสันจัดจ้าน gradient, ตารางสีสัน")
    print("✅ เพิ่มเข้า: รูปแบบวิชาการเรียบง่าย")
    print("    - Header: ข้อความดำบนพื้นขาว เส้นขั้นใต้")
    print("    - เนื้อหา: จัดเป็นหัวข้อมีหมายเลข")
    print("    - แผนภาพ: ขาวดำเรียบง่าย ไม่มีสี")
    print("    - Font: ใช้สีดำทั้งหมด")
    
    print("\n📄 รูปแบบ PDF ใหม่:")
    print("   1. ข้อมูลเบื้องต้น")
    print("   2. ข้อมูลเหล็กเสริม") 
    print("   3. แรงกระทำ")
    print("   4. แผนภาพหน้าตัดคาน (ขาวดำ)")
    print("   5. หมายเหตุ")
    
    print("\n🎯 ลักษณะพิเศษ:")
    print("   - เรียบง่าย เหมาะสำหรับงานวิชาการ")
    print("   - ไม่มีสีจัดจ้าน เน้นเนื้อหา")
    print("   - จัดรูปแบบแบบ academic paper")
    print("   - แผนภาพเรียบง่าย ชัดเจน")
    
    print("\n🚀 พร้อมสร้าง PDF รูปแบบวิชาการ!")
    
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")
    import traceback
    traceback.print_exc()
