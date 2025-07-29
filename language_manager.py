# -*- coding: utf-8 -*-
"""
Language Manager for RC Design Program
Manages translations between Thai, English, and Chinese
"""

import json
import os
import configparser

class LanguageManager:
    def __init__(self):
        self.config_file = 'user_settings.ini'
        self.current_language = self.load_saved_language()  # Load saved language
        self.translations = {}
        self.load_translations()
    
    def load_saved_language(self):
        """Load previously saved language preference"""
        try:
            if os.path.exists(self.config_file):
                config = configparser.ConfigParser()
                config.read(self.config_file, encoding='utf-8')
                return config.get('Settings', 'language', fallback='th')
            else:
                return 'th'  # Default to Thai
        except Exception as e:
            print(f"Error loading language preference: {e}")
            return 'th'
    
    def save_language_preference(self, language):
        """Save language preference to config file"""
        try:
            config = configparser.ConfigParser()
            
            # Load existing config if it exists
            if os.path.exists(self.config_file):
                config.read(self.config_file, encoding='utf-8')
            
            # Ensure Settings section exists
            if not config.has_section('Settings'):
                config.add_section('Settings')
            
            # Set language
            config.set('Settings', 'language', language)
            
            # Write to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                config.write(f)
                
        except Exception as e:
            print(f"Error saving language preference: {e}")
    
    def load_translations(self):
        """Load translation files"""
        languages = ['th', 'en', 'zh']
        
        for lang in languages:
            try:
                lang_file = f'translations_{lang}.json'
                if os.path.exists(lang_file):
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                else:
                    self.translations[lang] = {}
            except Exception as e:
                print(f"Error loading {lang} translations: {e}")
                self.translations[lang] = {}
    
    def set_language(self, language):
        """Set current language and save preference"""
        if language in ['th', 'en', 'zh']:
            self.current_language = language
            self.save_language_preference(language)
    
    def get_language(self):
        """Get current language"""
        return self.current_language
    
    def tr(self, key, default_text=""):
        """Translate text key to current language"""
        if self.current_language in self.translations:
            # Handle nested keys like "beam.width"
            keys = key.split('.')
            value = self.translations[self.current_language]
            
            try:
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return default_text or key
        return default_text or key
    
    def get_available_languages(self):
        """Get list of available languages"""
        return {
            'th': 'ไทย',
            'en': 'English', 
            'zh': '中文'
        }

# Global language manager instance
lang_manager = LanguageManager()
