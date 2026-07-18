import os

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from utils.theme_manager import theme_manager

class ModelUploadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_path = ""
        self.setWindowTitle("Upload YOLO Model")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        is_light = theme_manager.is_light_mode
        bg_col = "#ffffff" if is_light else "#1e1f25"
        text_col = "#111318" if is_light else "#e2e2e9"
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {bg_col}; color: {text_col}; font-family: 'Segoe UI', Arial; }}
            QLabel  {{ color: {text_col}; font-family: 'Segoe UI', Arial; }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(12)

        is_light = theme_manager.is_light_mode
        text_col = "#111318" if is_light else "#e2e2e9"
        sub_col = "#555e6d" if is_light else "#8b919e"

        title = QLabel("Upload YOLO Model")
        title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {text_col};")
        root.addWidget(title)

        sub = QLabel("Versi model min yolov8n dengan format .pt")
        sub.setStyleSheet(f"font-size: 11px; color: {sub_col};")
        root.addWidget(sub)

        self.lbl_path = QLabel("Belum ada model dipilih")
        self.lbl_path.setStyleSheet(f"color:{sub_col}; font-size:12px; font-style:italic;")

        btn_bg = "#f4f5f8" if is_light else "#282a2f"

        btn_pick = QPushButton("Browse File...")
        btn_pick.setStyleSheet(f"background:{btn_bg}; color:{text_col}; padding:6px 12px; border-radius:4px; border: 1px solid {'#d9dce1' if is_light else '#414752'};")
        btn_pick.clicked.connect(self._browse)

        row = QHBoxLayout()
        row.addWidget(btn_pick)
        row.addWidget(self.lbl_path, stretch=1)
        root.addLayout(row)
        root.addStretch()

        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Batal")
        btn_cancel.setObjectName("btn-cancel")
        btn_cancel.setStyleSheet("""
            #btn-cancel { background: #e63946; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px; border: none; }
            #btn-cancel:hover { background: #ff4d5a; }
        """)
        btn_cancel.clicked.connect(self.reject)

        self.btn_ok = QPushButton("Lanjutkan")
        self.btn_ok.setObjectName("btn-ok")
        self.btn_ok.setStyleSheet("""
            #btn-ok { background: #3D8EF0; color: #fff; font-weight: 700; padding: 8px 16px; border-radius: 6px; border: none; }
            #btn-ok:hover { background: #559ef2; }
        """)
        self.btn_ok.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_ok.clicked.connect(self._confirm)

        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self.btn_ok)
        root.addLayout(btn_row)

    def _browse(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Model YOLO", "", "Model Files (*.pt)"
        )
        if file_path:
            self.model_path = file_path
            self.lbl_path.setText(os.path.basename(file_path))
            
            is_light = theme_manager.is_light_mode
            text_col = "#111318" if is_light else "#e2e2e9"
            self.lbl_path.setStyleSheet(f"color:{text_col}; font-size:12px;")

    def _confirm(self):
        if self.model_path:
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Model Belum Dipilih",
                "Upload model YOLO terlebih dahulu.\n\n"
                "Klik 'Browse File...' untuk memilih file model.pt."
            )
