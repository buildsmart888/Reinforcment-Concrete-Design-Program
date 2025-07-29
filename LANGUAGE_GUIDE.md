# Language Update Implementation Guide
# คู่มือการใช้งานระบบหลายภาษา

## Files Added / ไฟล์ที่เพิ่ม:

1. **language_manager.py** - Core language management system / ระบบจัดการภาษาหลัก
2. **translations_th.json** - Thai translations / การแปลภาษาไทย  
3. **translations_en.json** - English translations / การแปลภาษาอังกฤษ
4. **translations_zh.json** - Chinese translations / การแปลภาษาจีน
5. **translation_helper.py** - Tool for managing translations / เครื่องมือจัดการการแปล
6. **test_language.py** - Test script / สคริปต์ทดสอบ
7. **README_NEW.md** - Updated documentation / เอกสารที่อัปเดตแล้ว

## Files Modified / ไฟล์ที่แก้ไข:

1. **ui_menu.py**:
   - Added language_manager import / เพิ่ม import language_manager
   - Added language selector widget / เพิ่ม widget เลือกภาษา
   - Updated retranslateUi to use language_manager / อัปเดต retranslateUi ให้ใช้ language_manager

2. **menu_controller.py**:
   - Added language_manager import / เพิ่ม import language_manager  
   - Added language change handler / เพิ่มตัวจัดการการเปลี่ยนภาษา
   - Connected language combo to change handler / เชื่อม language combo กับตัวจัดการ

3. **ui_rc_recbeamcal.py**:
   - Added language_manager import / เพิ่ม import language_manager
   - Updated retranslateUi to use translation keys / อัปเดต retranslateUi ให้ใช้ translation keys

## How to Use / วิธีใช้งาน:

### For Users / สำหรับผู้ใช้:

1. **Start the application / เริ่มแอปพลิเคชัน:**
   ```bash
   py starter.py
   ```

2. **Change language / เปลี่ยนภาษา:**
   - Look for language dropdown in top-right corner / มองหา dropdown ที่มุมขวาบน
   - Select: ไทย / English / 中文
   - Interface updates immediately / อินเทอร์เฟซอัปเดตทันที

3. **Test language system / ทดสอบระบบภาษา:**
   ```bash
   py test_language.py
   ```

### For Developers / สำหรับนักพัฒนา:

1. **Add new translations / เพิ่มการแปลใหม่:**
   ```python
   from translation_helper import add_translation
   
   add_translation('new.key', {
       'th': 'ข้อความไทย',
       'en': 'English text',
       'zh': '中文文字'
   })
   ```

2. **Use translations in UI files / ใช้การแปลในไฟล์ UI:**
   ```python
   from language_manager import lang_manager
   
   # In retranslateUi function:
   self.label.setText(lang_manager.tr('translation.key', 'Default Text'))
   ```

3. **Check for missing translations / ตรวจสอบการแปลที่ขาดหาย:**
   ```bash
   py translation_helper.py
   ```

## Next Steps / ขั้นตอนต่อไป:

### To Complete Implementation / เพื่อให้การใช้งานครบถ้วน:

1. **Update remaining UI files / อัปเดตไฟล์ UI ที่เหลือ:**
   - ui_rc_tbeamcal.py
   - ui_rc_beamdsgn.py  
   - ui_rc_columncal.py

2. **Add more translation keys / เพิ่ม translation keys:**
   - Error messages / ข้อความแสดงข้อผิดพลาด
   - Calculation results / ผลการคำนวณ
   - Tooltips / คำแนะนำเครื่องมือ

3. **Enhance features / เพิ่มฟีเจอร์:**
   - Save language preference / บันทึกการตั้งค่าภาษา
   - Dynamic font sizing for different languages / ขนาดฟอนต์แบบไดนามิก
   - Right-to-left language support / รองรับภาษาที่เขียนจากขวาไปซ้าย

## Template for UI Updates / เทมเพลตสำหรับอัปเดต UI:

```python
# 1. Add import at top of file:
from language_manager import lang_manager

# 2. Update retranslateUi function:
def retranslateUi(self, Widget):
    _translate = QtCore.QCoreApplication.translate
    Widget.setWindowTitle(lang_manager.tr('app_title', 'Default Title'))
    self.label.setText(lang_manager.tr('section.label', 'Default Label'))
    # ... repeat for all text elements
```

## Testing Checklist / รายการตรวจสอบ:

- [ ] Language selector appears in main menu / ตัวเลือกภาษาปรากฏในเมนูหลัก
- [ ] Switching languages updates interface immediately / การเปลี่ยนภาษาอัปเดตอินเทอร์เฟซทันที
- [ ] All three languages display correctly / ทั้งสามภาษาแสดงได้ถูกต้อง
- [ ] Thai text displays properly / ข้อความไทยแสดงถูกต้อง
- [ ] Chinese characters render correctly / ตัวอักษรจีนแสดงผลถูกต้อง
- [ ] No encoding errors / ไม่มีข้อผิดพลาดในการเข้ารหัส

## Troubleshooting / การแก้ไขปัญหา:

1. **Text not updating / ข้อความไม่อัปเดต:**
   - Check if retranslateUi is called after language change
   - Verify translation keys exist in JSON files

2. **Encoding issues / ปัญหาการเข้ารหัส:**
   - Ensure all files saved with UTF-8 encoding
   - Check console for encoding warnings

3. **Missing translations / การแปลขาดหาย:**
   - Run translation_helper.py to find missing keys
   - Add missing translations to JSON files
