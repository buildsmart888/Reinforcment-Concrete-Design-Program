# -*- coding: utf-8 -*-
"""
Demo script to test the language system
"""

from PyQt5 import QtWidgets, QtCore
import sys
import os

# Add current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from starter import *
from language_manager import lang_manager

def test_language_system():
    """Test the language system"""
    
    # Test Thai
    print("=== Testing Thai ===")
    lang_manager.set_language('th')
    print(f"App Title: {lang_manager.tr('app_title')}")
    print(f"Calculate: {lang_manager.tr('common.calculate')}")
    print(f"Beam Width: {lang_manager.tr('beam.width')}")
    
    # Test English
    print("\n=== Testing English ===")
    lang_manager.set_language('en')
    print(f"App Title: {lang_manager.tr('app_title')}")
    print(f"Calculate: {lang_manager.tr('common.calculate')}")
    print(f"Beam Width: {lang_manager.tr('beam.width')}")
    
    # Test Chinese
    print("\n=== Testing Chinese ===")
    lang_manager.set_language('zh')
    print(f"App Title: {lang_manager.tr('app_title')}")
    print(f"Calculate: {lang_manager.tr('common.calculate')}")
    print(f"Beam Width: {lang_manager.tr('beam.width')}")

if __name__ == "__main__":
    # Run language test
    test_language_system()
    
    # Start the application
    print("\n=== Starting Application ===")
    app = QtWidgets.QApplication(sys.argv)
    the_mainwindow = MenuController()
    the_mainwindow.show()
    sys.exit(app.exec_())
