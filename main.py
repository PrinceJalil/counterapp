import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon

from ui.main_window import MainWindow
from utils.theme_manager import theme_manager


def load_stylesheet(app: QApplication, is_light: bool = False) -> None:
    theme_file = "light_style.qss" if is_light else "main_style.qss"
    qss_path = os.path.join(os.path.dirname(__file__), "styles", theme_file)
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def main() -> None:
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "assets", "iconapp.ico")))
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    load_stylesheet(app, theme_manager.is_light_mode)
    
    # Reload stylesheet on theme change
    theme_manager.theme_changed.connect(lambda is_light: load_stylesheet(app, is_light))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
