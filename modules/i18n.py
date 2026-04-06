import json
import os
import locale
import sys
def get_system_language():
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith('tr'):
            return 'tr'
        return 'en'
    except Exception:
        return 'en'
class I18nManager:
    def __init__(self):
        self.base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')
        self.current_lang = 'en'
        self.translations = {}
        self.load_config()
    def load_config(self):
        config_path = os.path.join(os.path.dirname(self.base_path), 'config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.current_lang = config.get('language', get_system_language())
            except:
                self.current_lang = get_system_language()
        else:
            self.current_lang = get_system_language()
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump({'language': self.current_lang}, f, indent=4)
            except:
                pass
        self.load_translations()
    def load_translations(self):
        file_path = os.path.join(self.base_path, f"{self.current_lang}.json")
        if not os.path.exists(file_path):
            file_path = os.path.join(self.base_path, "en.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception as e:
            print(f"Error loading translations: {e}")
            self.translations = {}
    def get_text(self, key, default=None, **kwargs):
        text = self.translations.get(key, default or key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                pass
        return text
manager = I18nManager()
def t(key, default=None, **kwargs):
    return manager.get_text(key, default, **kwargs)
