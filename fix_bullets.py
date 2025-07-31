#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Fix Unicode bullet points in demo_improved_gui.py
import re

# Read the file
with open('demo_improved_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Unicode bullet points with ASCII dashes
content = content.replace('•', '-')

# Write back to file
with open('demo_improved_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Unicode bullet points in demo_improved_gui.py")
