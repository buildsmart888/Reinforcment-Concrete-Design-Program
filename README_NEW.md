# Reinforced Concrete Design Program (โปรแกรมออกแบบคอนกรีตเสริมเหล็ก)

<div align="center">
  <img src="https://github.com/chihweisu/Reinforcment-Concrete-Design-Program/blob/master/Readme_asset/png_banner.png" width="60%" >
</div>

## About The Program
This program provides users to analyze RC sections strength including RC beam and RC column. Strength calculations are based on ACI-318 code.

โปรแกรมนี้ให้ผู้ใช้วิเคราะห์ความแข็งแรงของหน้าตัด RC รวมถึงคาน RC และเสา RC การคำนวณความแข็งแรงอิงตามมาตรฐาน ACI-318

## 🌐 New Multi-Language Support / รองรับหลายภาษา

The program now supports **3 languages**:
- **ไทย (Thai)** - Default
- **English** 
- **中文 (Chinese)**

โปรแกรมตอนนี้รองรับ **3 ภาษา**:
- **ไทย** - ค่าเริ่มต้น
- **อังกฤษ**
- **จีน**

### How to Switch Languages / วิธีเปลี่ยนภาษา

1. Look for the language dropdown in the top-right corner of the main menu
2. Select your preferred language: ไทย / English / 中文
3. The interface will update immediately

1. มองหา dropdown ภาษาที่มุมขวาบนของเมนูหลัก
2. เลือกภาษาที่ต้องการ: ไทย / English / 中文  
3. อินเทอร์เฟซจะอัปเดตทันที

## Installation / การติดตั้ง

```bash
# Install required packages / ติดตั้งแพคเกจที่จำเป็น
py -m pip install matplotlib
py -m pip install PyQt5
```

## How to Use / วิธีใช้งาน

Run `starter.py` or `test_language.py` to test the language system:

เรียกใช้ `starter.py` หรือ `test_language.py` เพื่อทดสอบระบบภาษา:

```bash
py starter.py
# or / หรือ
py test_language.py
```

### Main Features / ฟีเจอร์หลัก

* **Menu / เมนู**:
  <div align="center">
  <img src="https://github.com/chihweisu/Reinforcment-Concrete-Design-Program/blob/master/Readme_asset/png_menu.PNG" width="30%" >
  </div>

* **RC Rectangular Beam Calculation / การคำนวณคานสี่เหลี่ยม**:  
  Input section information and load demands of the beam, the program will check if the beam's moment and shear capacity are enough.
  
  ใส่ข้อมูลหน้าตัดและแรงที่กระทำต่อคาน โปรแกรมจะตรวจสอบว่าความสามารถในการรับโมเมนต์และแรงเฉือนของคานเพียงพอหรือไม่

* **RC T-Beam Calculation / การคำนวณคาน T**:   
  Input section information and load demands of the beam, the program will check if the beam's moment and shear capacity are enough.
  
  ใส่ข้อมูลหน้าตัดและแรงที่กระทำต่อคาน โปรแกรมจะตรวจสอบว่าความสามารถในการรับโมเมนต์และแรงเฉือนของคานเพียงพอหรือไม่

* **RC Beam Design / การออกแบบคาน**:   
  Input section information and load demands of the beam, the program will design the required reinforcement of the beam.
  
  ใส่ข้อมูลหน้าตัดและแรงที่กระทำต่อคาน โปรแกรมจะออกแบบเหล็กเสริมที่จำเป็นสำหรับคาน

* **RC Column Calculation / การคำนวณเสา**:   
  Input section information and load demands of the column, the program will draw the P-M-M interaction diagram to check if the column's capacity is enough.
  
  ใส่ข้อมูลหน้าตัดและแรงที่กระทำต่อเสา โปรแกรมจะสร้างไดอะแกรม P-M-M เพื่อตรวจสอบว่าความสามารถของเสาเพียงพอหรือไม่

## Technical Implementation / การใช้งานทางเทคนิค

### Language System / ระบบภาษา

The multi-language system uses:
- `language_manager.py` - Core language management
- `translations_th.json` - Thai translations
- `translations_en.json` - English translations  
- `translations_zh.json` - Chinese translations

ระบบหลายภาษาใช้:
- `language_manager.py` - การจัดการภาษาหลัก
- `translations_th.json` - การแปลภาษาไทย
- `translations_en.json` - การแปลภาษาอังกฤษ
- `translations_zh.json` - การแปลภาษาจีน

### Files Modified / ไฟล์ที่แก้ไข

- `ui_menu.py` - Added language selector / เพิ่มตัวเลือกภาษา
- `menu_controller.py` - Added language change handling / เพิ่มการจัดการการเปลี่ยนภาษา
- `ui_rc_recbeamcal.py` - Updated to use language manager / อัปเดตให้ใช้ตัวจัดการภาษา

## Future Development / การพัฒนาในอนาคต

- Complete translation for all UI files / แปลครบทุกไฟล์ UI
- Add more languages / เพิ่มภาษาอื่นๆ
- Save language preference / บันทึกการตั้งค่าภาษา
- Update calculation result display / อัปเดตการแสดงผลการคำนวณ

## Contact / ติดต่อ

For questions about the language implementation or other features, please create an issue in the repository.

สำหรับคำถามเกี่ยวกับการใช้งานภาษาหรือฟีเจอร์อื่นๆ กรุณาสร้าง issue ใน repository
