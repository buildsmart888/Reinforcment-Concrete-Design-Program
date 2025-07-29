# -*- coding: utf-8 -*-
"""
Simple UI Helper - เพิ่มชื่อช่องกรอกข้อมูลแบบเรียบง่าย
เพิ่มเฉพาะ Placeholder Text เพื่อบอกว่าแต่ละช่องคือค่าอะไร
"""

from PyQt5 import QtCore, QtGui, QtWidgets

class SimpleUIHelper:
    """คลาสสำหรับเพิ่มชื่อช่องกรอกข้อมูลแบบเรียบง่าย"""
    
    @staticmethod
    def add_placeholders(ui_window):
        """เพิ่ม placeholder text ให้กับช่องกรอกข้อมูล"""
        
        # หาช่องกรอกข้อมูลทั้งหมด
        line_edits = ui_window.findChildren(QtWidgets.QLineEdit)
        
        for line_edit in line_edits:
            object_name = line_edit.objectName()
            
            # ตรวจสอบว่าช่องนี้ยังไม่มี placeholder text
            if not line_edit.placeholderText():
                
                # กำหนด placeholder text ตามชื่อ object (ใช้ exact match ก่อน)
                if object_name == 'Mux':
                    line_edit.setPlaceholderText("โมเมนต์ Mux (tf-m)")
                elif object_name == 'Muy':
                    line_edit.setPlaceholderText("โมเมนต์ Muy (tf-m)")
                elif object_name == 'Vuy':
                    line_edit.setPlaceholderText("แรงเฉือน Vu (tf)")
                elif object_name == 'Tu':
                    line_edit.setPlaceholderText("แรงบิด Tu (tf-m)")
                elif object_name == 'Pu':
                    line_edit.setPlaceholderText("แรงอัด Pu (tf)")
                elif object_name == 'Mu_left_minus':
                    line_edit.setPlaceholderText("โมเมนต์ Mu- ซ้าย (tf-m)")
                elif object_name == 'Mu_left_plus':
                    line_edit.setPlaceholderText("โมเมนต์ Mu+ ซ้าย (tf-m)")
                elif object_name == 'Vg_left':
                    line_edit.setPlaceholderText("แรงเฉือน V ซ้าย (tf)")
                elif object_name == 'Tu_left':
                    line_edit.setPlaceholderText("แรงบิด Tu ซ้าย (tf-m)")
                elif object_name == 'Mu_mid_minus':
                    line_edit.setPlaceholderText("โมเมนต์ Mu- กลาง (tf-m)")
                elif object_name == 'Mu_mid_plus':
                    line_edit.setPlaceholderText("โมเมนต์ Mu+ กลาง (tf-m)")
                elif object_name == 'Vg_mid':
                    line_edit.setPlaceholderText("แรงเฉือน V กลาง (tf)")
                elif object_name == 'Tu_mid':
                    line_edit.setPlaceholderText("แรงบิด Tu กลาง (tf-m)")
                elif object_name == 'Mu_rght_minus':
                    line_edit.setPlaceholderText("โมเมนต์ Mu- ขวา (tf-m)")
                elif object_name == 'Mu_rght_plus':
                    line_edit.setPlaceholderText("โมเมนต์ Mu+ ขวา (tf-m)")
                elif object_name == 'Vg_rght':
                    line_edit.setPlaceholderText("แรงเฉือน V ขวา (tf)")
                elif object_name == 'Tu_rght':
                    line_edit.setPlaceholderText("แรงบิด Tu ขวา (tf-m)")
                elif object_name == 'hf':
                    line_edit.setPlaceholderText("ความหนาพื้น hf (cm)")
                elif object_name == 'length':
                    line_edit.setPlaceholderText("ความยาวคาน L (m)")
                elif object_name == 'Sn':
                    line_edit.setPlaceholderText("ระยะห่างคาน Sn (cm)")
                    
                # กำหนดแบบ pattern matching สำหรับชื่อทั่วไป
                elif 'width' in object_name.lower() or object_name.lower() in ['b']:
                    line_edit.setPlaceholderText("ความกว้าง B (cm)")
                elif 'depth' in object_name.lower() or object_name.lower() in ['d']:
                    line_edit.setPlaceholderText("ความลึก D (cm)")
                elif 'fc' in object_name.lower():
                    line_edit.setPlaceholderText("F'c (kgf/cm²)")
                elif 'fy' in object_name.lower():
                    line_edit.setPlaceholderText("Fy (kgf/cm²)")
                elif 'stirrup_span' in object_name.lower():
                    line_edit.setPlaceholderText("ระยะห่างเหล็กปลอก (cm)")
                    
                # สำหรับจำนวนเหล็ก
                elif 'barnum1' in object_name.lower():
                    line_edit.setPlaceholderText("จำนวนเหล็กเสริม As")
                elif 'barnum2' in object_name.lower():
                    line_edit.setPlaceholderText("จำนวนเหล็กอัด A's")
                elif 'barnum' in object_name.lower() or 'num' in object_name.lower():
                    line_edit.setPlaceholderText("จำนวนเหล็ก")
                elif 'nx' in object_name.lower():
                    line_edit.setPlaceholderText("จำนวนเหล็ก Nx")
                elif 'ny' in object_name.lower():
                    line_edit.setPlaceholderText("จำนวนเหล็ก Ny")
                elif 'pu' in object_name.lower():
                    line_edit.setPlaceholderText("แรงอัด Pu (tf)")
                    
                # กรณีอื่น ๆ ที่ยังไม่ได้กำหนด
                else:
                    line_edit.setPlaceholderText("กรอกค่า")
                    
    @staticmethod 
    def add_window_titles(ui_window):
        """เพิ่มชื่อหน้าต่างให้ชัดเจน"""
        
        # กำหนดชื่อหน้าต่างตามประเภท
        class_name = ui_window.__class__.__name__
        window_type = str(type(ui_window))
        
        base_title = "โปรแกรมออกแบบคอนกรีตเสริมเหล็ก"
        
        if "RCRecbeamCal" in window_type or "recbeam" in class_name.lower():
            ui_window.setWindowTitle(f"{base_title} - คำนวณคานสี่เหลี่ยม")
        elif "RCBeamDsgn" in window_type or "beamdsgn" in class_name.lower():
            ui_window.setWindowTitle(f"{base_title} - ออกแบบเหล็กเสริมคาน")
        elif "RCColumnCal" in window_type or "column" in class_name.lower():
            ui_window.setWindowTitle(f"{base_title} - คำนวณเสา")
        elif "RCTbeamCal" in window_type or "tbeam" in class_name.lower():
            ui_window.setWindowTitle(f"{base_title} - คำนวณคาน T")
        elif "Menu" in window_type or "menu" in class_name.lower():
            ui_window.setWindowTitle(f"{base_title} - เมนูหลัก")
        else:
            ui_window.setWindowTitle(base_title)

# สร้าง instance สำหรับใช้งาน
simple_ui_helper = SimpleUIHelper()
