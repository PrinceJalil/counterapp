import os
import cv2

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

from widgets.drawing_label import DrawingLabel
from utils.theme_manager import theme_manager


class RegionDrawingDialog(QDialog):
    def __init__(self, source, parent=None):
        super().__init__(parent)
        self.source        = source
        self.region_points = []
        self.setWindowTitle("Tentukan Counting Line")
        self.setModal(True)
        self.setFixedSize(800, 600)
        
        is_light = theme_manager.is_light_mode
        bg_col = "#ffffff" if is_light else "#1e1f25"
        text_col = "#111318" if is_light else "#e2e2e9"
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {bg_col}; color: {text_col}; font-family: 'Segoe UI', Arial; }}
            QLabel  {{ color: {text_col}; font-family: 'Segoe UI', Arial; }}
        """)

        self._orig_w = 0
        self._orig_h = 0
        self._first_frame_pixmap = self._get_first_frame()
        self._init_ui()

    def _get_first_frame(self) -> QPixmap:
        is_webcam = isinstance(self.source, int)
        if is_webcam:
            if os.name == 'nt':
                cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(self.source)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        else:
            cap = cv2.VideoCapture(self.source)

        if cap.isOpened():
            self._orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Membaca beberapa frame awal untuk membuang frame hitam (warm-up kamera)
            ret = False
            frame = None
            for _ in range(40):
                r, f = cap.read()
                if r and f is not None:
                    ret = True
                    frame = f
                    if f.mean() > 1.0:  # Jika frame tidak gelap total
                        break
            cap.release()
            if ret:
                h, w, ch = frame.shape
                if self._orig_w == 0: self._orig_w = w
                if self._orig_h == 0: self._orig_h = h
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
                return QPixmap.fromImage(img)

        pm = QPixmap(800, 500)
        pm.fill(Qt.GlobalColor.black)
        return pm

    # ── UI ───────────────────────────────────────────────────────────
    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

        is_light = theme_manager.is_light_mode
        text_col = "#111318" if is_light else "#e2e2e9"
        sub_col = "#555e6d" if is_light else "#8b919e"

        title = QLabel("Tentukan Counting Line")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {text_col};")
        root.addWidget(title)
        
        desc = QLabel("Klik dan tahan, lalu tarik garis pada gambar di bawah untuk menentukan batas garis.")
        desc.setStyleSheet(f"font-size: 12px; color: {sub_col}; margin-bottom: 10px;")
        desc.setWordWrap(True)
        root.addWidget(desc)

        self.view_lbl = DrawingLabel()
        self.view_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.view_lbl.setStyleSheet("background-color: #000; border-radius: 8px;")

        scaled_pm = self._first_frame_pixmap.scaled(
            760, 480,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.view_lbl.setPixmap(scaled_pm)
        if not scaled_pm.isNull():
            self.view_lbl.setFixedSize(scaled_pm.size())

        view_container = QWidget()
        v_l = QHBoxLayout(view_container)
        v_l.setContentsMargins(0, 0, 0, 0)
        v_l.addWidget(self.view_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        root.addWidget(view_container, stretch=1)

        btn_row = QHBoxLayout()
        
        btn_bg = "#f4f5f8" if is_light else "#282a2f"
        btn_hover = "#e2e4e9" if is_light else "#33353a"
        btn_border = "#d9dce1" if is_light else "#414752"
        
        btn_reset = QPushButton("Reset Line")
        btn_reset.setObjectName("btn-reset")
        btn_reset.setStyleSheet(f"""
            #btn-reset {{ background: {btn_bg}; color: {sub_col}; padding: 8px 16px; border-radius: 6px; border: 1px solid {btn_border}; }}
            #btn-reset:hover {{ background: {btn_hover}; }}
        """)
        btn_reset.clicked.connect(self.view_lbl.reset_line)

        btn_save = QPushButton("Save")
        btn_save.setObjectName("btn-save")
        btn_save.setStyleSheet("""
            #btn-save { background: #3D8EF0; color: #fff; font-weight: bold; padding: 8px 16px; border-radius: 6px; border: none; }
            #btn-save:hover { background: #559ef2; }
        """)
        btn_save.clicked.connect(self._save_region)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("btn-cancel")
        btn_cancel.setStyleSheet("""
            #btn-cancel { background: #e63946; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px; border: none; }
            #btn-cancel:hover { background: #ff4d5a; }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(btn_reset)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        root.addLayout(btn_row)

    # Save logic 
    def _save_region(self):
        if not self.view_lbl.line_done or not self.view_lbl.start_point or not self.view_lbl.end_point:
            QMessageBox.warning(
                self,
                "Line Belum Ditentukan",
                "Tentukan counting line terlebih dahulu.\n\n"
                "Klik dan seret pada gambar untuk menggambar garis."
            )
            return

        sh = self.view_lbl.height()
        sw = self.view_lbl.width()
        orig_w = self._orig_w
        orig_h = self._orig_h

        if sh > 0 and sw > 0 and orig_w > 0 and orig_h > 0:
            scale_x = orig_w / sw
            scale_y = orig_h / sh
            x1 = int(self.view_lbl.start_point.x() * scale_x)
            y1 = int(self.view_lbl.start_point.y() * scale_y)
            x2 = int(self.view_lbl.end_point.x() * scale_x)
            y2 = int(self.view_lbl.end_point.y() * scale_y)
            self.region_points = [(x1, y1), (x2, y2)]
        else:
            self.region_points = [(0, 0), (0, 0)]

        self.accept()
