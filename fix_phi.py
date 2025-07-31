#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('demo_improved_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# แก้ไข results['?'] เป็น results['phi']
content = content.replace("results['?']", "results['phi']")

with open('demo_improved_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("แก้ไขเสร็จสิ้น - เปลี่ยน results['?'] เป็น results['phi'] แล้ว")
