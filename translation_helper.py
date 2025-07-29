# -*- coding: utf-8 -*-
"""
Translation helper script
Helps developers add new translations or update existing ones
"""

import json
from language_manager import lang_manager

def add_translation(key, translations):
    """
    Add a new translation key to all language files
    
    Args:
        key (str): Translation key (e.g., "beam.new_field")
        translations (dict): Dictionary with language codes as keys and translations as values
                           e.g., {"th": "ข้อความไทย", "en": "English text", "zh": "中文"}
    """
    languages = ['th', 'en', 'zh']
    
    for lang in languages:
        filename = f'translations_{lang}.json'
        
        try:
            # Load existing translations
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Navigate to the correct nested structure
            keys = key.split('.')
            current = data
            
            # Create nested structure if it doesn't exist
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # Add the translation
            if lang in translations:
                current[keys[-1]] = translations[lang]
                print(f"Added '{key}' = '{translations[lang]}' to {filename}")
            
            # Save back to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error updating {filename}: {e}")

def list_missing_translations():
    """List keys that are missing translations in any language"""
    languages = ['th', 'en', 'zh']
    all_keys = set()
    lang_keys = {}
    
    # Collect all keys from all languages
    for lang in languages:
        filename = f'translations_{lang}.json'
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                keys = extract_keys(data)
                lang_keys[lang] = keys
                all_keys.update(keys)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            lang_keys[lang] = set()
    
    # Find missing keys
    print("Missing translations:")
    for key in sorted(all_keys):
        missing_in = []
        for lang in languages:
            if key not in lang_keys[lang]:
                missing_in.append(lang)
        
        if missing_in:
            print(f"  {key}: missing in {', '.join(missing_in)}")

def extract_keys(data, prefix=""):
    """Extract all keys from nested dictionary"""
    keys = set()
    for k, v in data.items():
        current_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.update(extract_keys(v, current_key))
        else:
            keys.add(current_key)
    return keys

def test_translation(key):
    """Test a translation key in all languages"""
    print(f"Testing key: {key}")
    for lang_code, lang_name in [('th', 'Thai'), ('en', 'English'), ('zh', 'Chinese')]:
        lang_manager.set_language(lang_code)
        translation = lang_manager.tr(key)
        print(f"  {lang_name}: {translation}")

if __name__ == "__main__":
    print("Translation Helper Tool")
    print("======================")
    
    # Example usage
    print("\n1. Testing existing translations:")
    test_translation("beam.width")
    test_translation("common.calculate")
    
    print("\n2. Checking for missing translations:")
    list_missing_translations()
    
    # Example of adding new translation
    print("\n3. Example: Adding new translation")
    print("   add_translation('common.error', {")
    print("       'th': 'ข้อผิดพลาด',")
    print("       'en': 'Error',") 
    print("       'zh': '錯誤'")
    print("   })")
