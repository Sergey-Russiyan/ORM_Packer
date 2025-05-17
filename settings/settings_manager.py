from PySide6.QtCore import QSettings

class SettingsManager:
    def __init__(self):
        self._settings = QSettings("BadGamesOK", "TexturePacker")

    def save_settings(self, settings):
        try:
            # Save folder path
            self._settings.setValue("last_folder", settings.get('folder', ""))

            # Save suffixes
            suffixes = settings.get('suffixes', {})
            for suffix in ['ao', 'roughness', 'metallic']:
                self._settings.setValue(f"suffix_{suffix}", suffixes.get(suffix, ""))

            # Save advanced options
            advanced = settings.get('advanced', {})
            for option in ['export_log', 'dark_theme', 'play_sound']:
                self._settings.setValue(option, advanced.get(option, False))

            print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_settings(self):
        return {
            'folder': self._settings.value("last_folder", ""),
            'suffixes': {
                'ao': self._settings.value("suffix_ao", "_ao"),
                'roughness': self._settings.value("suffix_roughness", "_roughness"),
                'metallic': self._settings.value("suffix_metallic", "_metallic")
            },
            'advanced': {
                'export_log': self._settings.value("export_log", False, type=bool),
                'dark_theme': self._settings.value("dark_theme", False, type=bool),
                'play_sound': self._settings.value("play_sound", False, type=bool)
            }
        }