# การแก้ไขปัญหาการแสดงผลคาน T-beam ในภาษาต่างๆ (T-beam Display Language Fix)

## ปัญหาที่พบ (Problem Found)
เมื่อใช้ภาษาไทยในการคำนวณคาน T-beam การแสดงผลหน้าตาคานไม่เหมือนกับตอนใช้ภาษาจีน เนื่องจากมีการ hard-code ข้อความภาษาจีนในการเช็คประเภทคาน

## สาเหตุของปัญหา (Root Cause)
1. **widget_rc_tbeam.py** - ใช้ `'內梁'` (ภาษาจีน) แบบ hard-coded ในการเช็คประเภทคาน
2. **beam_function.py** - ฟังก์ชัน `cal_effective_width()` ใช้ `'內梁'` แบบ hard-coded
3. เมื่อเปลี่ยนภาษาเป็นไทยหรืออังกฤษ ค่า `BeamCondition` จะเป็น:
   - ไทย: "คานใน"
   - อังกฤษ: "Interior Beam"
   - จีน: "內梁"

## การแก้ไขที่ทำ (Fixes Applied)

### 1. แก้ไขไฟล์ widget_rc_tbeam.py

#### เพิ่ม import language_manager:
```python
from PyQt5 import QtGui,QtWidgets,QtCore
from PyQt5.QtCore import QThread, Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor
from language_manager import lang_manager  # เพิ่มบรรทัดนี้
```

#### แก้ไขการเช็คประเภทคานในฟังก์ชัน rctbeamdraw_info() (บรรทัด 21-34):
```python
# เดิม
if self.BeamCondition=='內梁' :
    self.x_offset=(self.be-self.B)/2
else :
    self.x_offset=self.be-self.B

# แก้ไขเป็น
# Check beam condition for all languages
is_interior_beam = (BeamCondition in [
    lang_manager.tr("beam.interior_beam"),  # Current language
    "內梁",  # Chinese
    "คานใน",  # Thai  
    "Interior Beam"  # English
])

if is_interior_beam:
    self.x_offset=(self.be-self.B)/2
else :
    self.x_offset=self.be-self.B
```

#### แก้ไขการเช็คประเภทคานในฟังก์ชัน paintEvent() (บรรทัด 59-77):
```python
# เดิม
if self.BeamCondition=='內梁' :
    self.qpainter.drawRect(QRect(int(self.B+self.x_offset), 0, int(self.x_offset), int(self.hf)))

# แก้ไขเป็น
# Check beam condition for all languages
is_interior_beam = (self.BeamCondition in [
    lang_manager.tr("beam.interior_beam"),  # Current language
    "內梁",  # Chinese
    "คานใน",  # Thai  
    "Interior Beam"  # English
])

if is_interior_beam:
    self.qpainter.drawRect(QRect(int(self.B+self.x_offset), 0, int(self.x_offset), int(self.hf)))
```

### 2. แก้ไขไฟล์ beam_function.py

#### แก้ไขฟังก์ชัน cal_effective_width() (บรรทัด 204-218):
```python
# เดิม
def cal_effective_width(BeamCondition,B,Sn,hf,length) :
    if BeamCondition=='內梁' :
        be=min(length/4,B+Sn,B+16*hf)
    else :
        be=min(B+length/12,B+Sn/2,B+6*hf)
    return be

# แก้ไขเป็น
def cal_effective_width(BeamCondition,B,Sn,hf,length) :
    # Check beam condition for all languages
    is_interior_beam = (BeamCondition in [
        lang_manager.tr("beam.interior_beam"),  # Current language
        "內梁",  # Chinese
        "คานใน",  # Thai  
        "Interior Beam"  # English
    ])
    
    if is_interior_beam:
        be=min(length/4,B+Sn,B+16*hf)
    else :
        be=min(B+length/12,B+Sn/2,B+6*hf)
    return be
```

## ผลลัพธ์หลังการแก้ไข (Results After Fix)

### ก่อนแก้ไข:
- **ภาษาจีน**: การแสดงผลคาน T-beam ถูกต้อง
- **ภาษาไทย/อังกฤษ**: การแสดงผลคาน T-beam ผิดพลาด เนื่องจากไม่สามารถจดจำประเภทคานได้

### หลังแก้ไข:
- **ทุกภาษา**: การแสดงผลคาน T-beam ถูกต้องเหมือนกันในทุกภาษา
- **คานใน (Interior Beam)**: แสดงผลเป็นคาน T ที่มีส่วนขยายทั้งสองข้าง
- **คานขอบ (Edge Beam)**: แสดงผลเป็นคาน T ที่มีส่วนขยายเพียงข้างเดียว

## การทำงานของระบบ (System Behavior)

### การคำนวณ Effective Width:
- **คานใน**: `be = min(length/4, B+Sn, B+16*hf)`
- **คานขอบ**: `be = min(B+length/12, B+Sn/2, B+6*hf)`

### การแสดงผลกราฟิก:
- **คานใน**: `x_offset = (be-B)/2` - วางคานกลางส่วนขยาย
- **คานขอบ**: `x_offset = be-B` - วางคานติดขอบส่วนขยาย

## การทดสอบ (Testing)
✅ ทดสอบภาษาไทย - การแสดงผลคาน T-beam ถูกต้อง
✅ ทดสอบภาษาอังกฤษ - การแสดงผลคาน T-beam ถูกต้อง  
✅ ทดสอบภาษาจีน - การแสดงผลคาน T-beam ยังคงถูกต้องเหมือนเดิม
✅ การคำนวณ effective width ทำงานถูกต้องในทุกภาษา

## บทเรียนที่ได้รับ (Lessons Learned)
1. **หลีกเลี่ยง Hard-coded Text**: ไม่ควรใช้ข้อความภาษาเฉพาะในการเช็คเงื่อนไข
2. **Multi-language Support**: ต้องรองรับค่าที่แปลแล้วจากทุกภาษา
3. **Consistent Logic**: ใช้ตรรกะเดียวกันในการเช็คประเภทคานทั้งในส่วนคำนวณและการแสดงผล

## สรุป (Summary)
การแก้ไขนี้ทำให้การแสดงผลคาน T-beam ทำงานถูกต้องในทุกภาษา โดยการเปลี่ยนจากการเช็คข้อความแบบ hard-coded เป็นการเช็คแบบ multi-language support ที่รองรับค่าที่แปลแล้วจากทุกภาษา
