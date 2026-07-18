from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from utils.theme_manager import theme_manager

class LogItem(QWidget):
    def __init__(self, icon: str, title: str, status: str, time_str: str, parent=None):
        super().__init__(parent)
        self.setProperty("class", "log-item")
        self._build_ui(icon, title, status, time_str)
        self.apply_theme(theme_manager.is_light_mode)
        theme_manager.theme_changed.connect(self.apply_theme)

    def _build_ui(self, icon: str, title: str, status: str, time_str: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        self.icon_lbl = QLabel(icon)
        
        text_col = QVBoxLayout()
        self.title_lbl = QLabel(title)
        self.status_lbl = QLabel(status)
        text_col.addWidget(self.title_lbl)
        text_col.addWidget(self.status_lbl)

        self.time_lbl = QLabel(time_str)

        layout.addWidget(self.icon_lbl)
        layout.addLayout(text_col)
        layout.addStretch()
        layout.addWidget(self.time_lbl)
        
    def apply_theme(self, is_light: bool):
        color_icon = "#119c5b" if is_light else "#35e192"
        color_title = "#111318" if is_light else "#e2e2e9"
        color_sec = "#555e6d" if is_light else "#8b919e"
        
        self.icon_lbl.setStyleSheet(f"font-size: 16px; color: {color_icon};")
        self.title_lbl.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {color_title};")
        self.status_lbl.setStyleSheet(f"font-size: 10px; color: {color_sec};")
        self.time_lbl.setStyleSheet(f"font-size: 11px; color: {color_sec}; font-family: monospace;")

