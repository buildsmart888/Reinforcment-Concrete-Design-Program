# การแก้ไขปัญหา QRect Float Arguments

## 🐛 **ปัญหาที่พบ**
```
TypeError: arguments did not match any overloaded call:
QRect(): too many arguments
QRect(aleft: int, atop: int, awidth: int, aheight: int): argument 3 has unexpected type 'float'
```

**สาเหตุ**: PyQt5 ต้องการให้พารามิเตอร์ของ `QRect`, `drawRoundedRect`, `drawEllipse`, และ `drawArc` เป็น `int` แต่โค้ดใช้ `float`

## ✅ **ไฟล์ที่แก้ไข**

### 1. `widget_rc_recbeam.py`
- ✅ `QRect(0, 0, int(self.B), int(self.D))`
- ✅ `drawRoundedRect()` - แปลงพารามิเตอร์ทั้งหมดเป็น `int`
- ✅ `drawEllipse()` - แปลงตำแหน่งและขนาดเป็น `int`
- ✅ `drawArc()` และ `drawLine()` - แปลงพิกัดเป็น `int`

### 2. `widget_rc_tbeam.py`
- ✅ `QRect(int(0+self.x_offset), 0, int(self.B), int(self.D))`
- ✅ `QRect(0, 0, int(self.x_offset), int(self.hf))`
- ✅ `QRect(int(self.B+self.x_offset), 0, int(self.x_offset), int(self.hf))`
- ✅ `drawRoundedRect()`, `drawEllipse()`, `drawArc()`, `drawLine()` - แปลงเป็น `int`

### 3. `widget_rc_column.py`
- ✅ `QRect(0, 0, int(self.B), int(self.D))`
- ✅ `drawRoundedRect()`, `drawEllipse()`, `drawArc()`, `drawLine()` - แปลงเป็น `int`

### 4. `widget_rc_beamdsgn.py`
- ✅ `QRect(int(p2x), int(p2y), int(self.L-self.colw), int(self.D))`
- ✅ `QRect(int(p1x), int(p1y), int(self.colw), int(2*self.colh+self.D))`
- ✅ `QRect(int(p3x), int(p1y), int(self.colw), int(2*self.colh+self.D))`

## 🔧 **วิธีการแก้ไข**

### การใช้ int() สำหรับ PyQt5 Drawing Functions:
```python
# ❌ ผิด - ใช้ float
self.qpainter.drawRect(QRect(0, 0, self.B, self.D))
self.qpainter.drawEllipse(x, y, width, height)

# ✅ ถูก - แปลงเป็น int
self.qpainter.drawRect(QRect(0, 0, int(self.B), int(self.D)))
self.qpainter.drawEllipse(int(x), int(y), int(width), int(height))
```

### Functions ที่ต้องการ int:
- `QRect(x, y, width, height)` - ทุกพารามิเตอร์
- `drawRoundedRect(x, y, width, height, xRadius, yRadius)` - ทุกพารามิเตอร์
- `drawEllipse(x, y, width, height)` - ทุกพารามิเตอร์
- `drawArc(x, y, width, height, startAngle, spanAngle)` - พารามิเตอร์ 4 ตัวแรก

### Functions ที่ยอมรับ float:
- `drawLine(x1, y1, x2, y2)` - รับ float ได้ (แต่แปลงเป็น int ก็ได้)

## 🎯 **ผลลัพธ์**
- ✅ โปรแกรมสามารถเรียกใช้ได้โดยไม่มีข้อผิดพลาด
- ✅ Widget ทั้งหมดแสดงผลได้ปกติ
- ✅ ระบบภาษาหลายภาษาทำงานได้สมบูรณ์

## 📝 **บันทึกสำหรับนักพัฒนา**
เมื่อใช้ PyQt5 สำหรับการวาดกราฟิก ควรแปลงค่า `float` เป็น `int` เสมอเพื่อหลีกเลี่ยงข้อผิดพลาด TypeError

```python
# Best Practice
int(calculated_value)  # แปลงผลการคำนวณเป็น int ก่อนใช้ใน drawing functions
```
