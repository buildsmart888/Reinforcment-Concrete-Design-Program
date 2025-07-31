# -*- coding: utf-8 -*-
"""Language system tests and demo run"""

import os
import sys
import unittest

# Add current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from language_manager import lang_manager

class TestLanguageSystem(unittest.TestCase):
    """Test translations for supported languages."""

    expected = {
        'th': {
            'app_title': 'โปรแกรมออกแบบคอนกรีตเสริมเหล็ก',
            'calculate': 'คำนวณ',
        },
        'en': {
            'app_title': 'Reinforced Concrete Design Program',
            'calculate': 'Calculate',
        },
        'zh': {
            'app_title': '鋼筋混凝土設計程式',
            'calculate': '計算',
        },
    }

    def test_translations(self):
        for lang, values in self.expected.items():
            with self.subTest(lang=lang):
                lang_manager.set_language(lang)
                self.assertEqual(lang_manager.tr('app_title'), values['app_title'])
                self.assertEqual(lang_manager.tr('common.calculate'), values['calculate'])

if __name__ == "__main__":
    unittest.main(exit=False)

    from PyQt5 import QtWidgets
    from menu_controller import MenuController

    print("\n=== Starting Application ===")
    app = QtWidgets.QApplication(sys.argv)
    the_mainwindow = MenuController()
    the_mainwindow.show()
    sys.exit(app.exec_())
