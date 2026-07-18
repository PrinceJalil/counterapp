import os

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QFileDialog, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QPixmap

from utils.helpers import get_asset_path
from utils.theme_manager import theme_manager


class SourceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Source")
        self.setModal(True)
        self.setFixedSize(460, 250)

        self.chosen_source = None
        
        is_light = theme_manager.is_light_mode
        bg_col = "#ffffff" if is_light else "#1e1f25"
        text_col = "#111318" if is_light else "#e2e2e9"
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {bg_col}; color: {text_col}; font-family: 'Segoe UI', Arial; }}
            QLabel  {{ color: {text_col}; font-family: 'Segoe UI', Arial; }}
        """)
        
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        sub = QLabel("Pilih sumber video untuk memulai counting.")
        sub_col = '#555e6d' if theme_manager.is_light_mode else '#8b919e'
        sub.setStyleSheet(f"font-size: 13px; color: {sub_col}; font-weight: bold;")
        root.addWidget(sub)
        root.addSpacing(20)

        # Option cards
        self._btn_video = self._make_option_btn(
            "Video File", "Unggah file video (mp4/avi)", get_asset_path("file.png")
        )
        self._btn_webcam = self._make_option_btn(
            "Webcam", "Gunakan kamera bawaan / eksternal", get_asset_path("webcam.png")
        )


        root.addWidget(self._btn_video)
        root.addSpacing(10)
        root.addWidget(self._btn_webcam)

        root.addStretch()

    def _make_option_btn(self, label: str, desc: str, icon_path: str) -> QFrame:
        is_light = theme_manager.is_light_mode
        card_bg = "#f4f5f8" if is_light else "#282a2f"
        card_border = "#d9dce1" if is_light else "#33353a"
        card_hover = "#e2e4e9" if is_light else "#2e3039"
        
        card = QFrame()
        card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        card.setObjectName("opt-card")
        card.setStyleSheet(f"""
            #opt-card {{
                background-color: {card_bg};
                border: 1px solid {card_border};
                border-radius: 10px;
            }}
            #opt-card:hover {{
                background-color: {card_hover};
                border: 1px solid #3D8EF0;
            }}
        """)
        card.setFixedHeight(64)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(14)

        icon_lbl = QLabel()
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            icon_lbl.setPixmap(pixmap.scaled(
                24, 24,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            icon_lbl.setText("📁")
            icon_lbl.setStyleSheet("font-size: 22px; color: #3D8EF0;")
        icon_lbl.setFixedWidth(30)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        is_light = theme_manager.is_light_mode
        text_col = "#111318" if is_light else "#e2e2e9"
        sub_col = "#555e6d" if is_light else "#8b919e"
        arrow_col = "#a6aebf" if is_light else "#414752"
        
        text_col_layout = QVBoxLayout()
        text_col_layout.setSpacing(2)
        text_col_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        name_lbl = QLabel(label)
        name_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {text_col}; background: transparent; border: none;")
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(f"font-size: 11px; color: {sub_col}; background: transparent; border: none;")
        text_col_layout.addWidget(name_lbl)
        text_col_layout.addWidget(desc_lbl)

        arrow = QLabel("›")
        arrow.setStyleSheet(f"font-size: 20px; color: {arrow_col}; background: transparent; border: none;")

        layout.addWidget(icon_lbl)
        layout.addLayout(text_col_layout)
        layout.addStretch()
        layout.addWidget(arrow)

        card.mousePressEvent = lambda e, b=label: self._card_clicked(b)
        return card

    def _card_clicked(self, label: str):
        if label == "Video File":
            self._pick_video()
        elif label == "Webcam":
            self._pick_webcam()


    def _pick_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv)"
        )
        if file_path:
            self.chosen_source = file_path
            self.accept()

    def _pick_webcam(self):
        self.chosen_source = 0
        self.accept()

