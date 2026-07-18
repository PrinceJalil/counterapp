from PyQt6.QtCore import QObject, pyqtSignal

class _ThemeManager(QObject):
    theme_changed = pyqtSignal(bool)  # Emits True if light mode, False if dark mode

    def __init__(self):
        super().__init__()
        self.is_light_mode = False

    def toggle_theme(self):
        self.is_light_mode = not self.is_light_mode
        self.theme_changed.emit(self.is_light_mode)

    def set_theme(self, is_light: bool):
        if self.is_light_mode != is_light:
            self.is_light_mode = is_light
            self.theme_changed.emit(self.is_light_mode)

# Singleton instance
theme_manager = _ThemeManager()
