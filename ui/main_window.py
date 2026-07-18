import os

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QSizePolicy, QGridLayout, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor

from ui.history_page import HistoryPage
from ui.analytics_page import AnalyticsPage
from widgets.log_item import LogItem
from widgets.theme_switch import ThemeSwitch
from core.app_controller import AppController
from utils.theme_manager import theme_manager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CounterApp")
        self.resize(1280, 800)

        self._log_widgets: list[LogItem] = []
        self._class_count_labels = {}

        self._init_ui()
        self._connect_controller()
        self.on_state_changed(
            running=False, 
            source=self.controller.video_source, 
            model=self.controller.model_path
        )
        
        theme_manager.theme_changed.connect(self.apply_theme)
        self.apply_theme(theme_manager.is_light_mode)

    # Theme application  
    def apply_theme(self, is_light: bool):
        # Sidebar
        color_primary = "#111318" if is_light else "#e2e2e9"
        color_secondary = "#555e6d" if is_light else "#8b919e"
        
        self.title_lbl.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color_primary};")
        self.subtitle_lbl.setStyleSheet(f"font-size: 10px; color: {color_secondary}; letter-spacing: 1px;")
        
        if self.status_indicator.text() == "● IDLE":
            self.status_indicator.setStyleSheet(f"color: {color_secondary}; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
            
        # self.theme_btn updates itself via its paintEvent when toggled
        
        # Dashboard
        self.header_title.setStyleSheet(f"font-size: 22px; font-weight: 900; color: {color_primary};")
        
        badge_bg = "#ffffff" if is_light else "#282a2f"
        badge_border = "#d9dce1" if is_light else "#414752"
        self.source_badge.setStyleSheet(
            f"background-color: {badge_bg}; color: {'#2a73cc' if is_light else '#a6c8ff'};"
            f"border: 1px solid {badge_border}; border-radius: 4px;"
            "padding: 4px 10px; font-family: monospace; font-size: 11px;"
        )
        self.model_badge.setStyleSheet(
            f"background-color: {badge_bg}; color: {'#863bcf' if is_light else '#e2b4ff'};"
            f"border: 1px solid {badge_border}; border-radius: 4px;"
            "padding: 4px 10px; font-family: monospace; font-size: 11px;"
        )
        self.fps_badge.setStyleSheet(
            f"background-color: {badge_bg}; color: {'#d67a18' if is_light else '#ffb86c'};"
            f"border: 1px solid {badge_border}; border-radius: 4px;"
            "padding: 4px 10px; font-family: monospace; font-size: 11px; font-weight: bold;"
        )
        
        # Right Panel
        self.c_title.setStyleSheet(f"font-size: 10px; font-weight: 700; letter-spacing: 1px; color: {color_secondary};")
        self.logs_title.setStyleSheet(f"font-size: 10px; font-weight: 700; letter-spacing: 1px; color: {color_secondary};")
        
        if self.status_indicator.text() == "● IDLE":
            self.lbl_count.setStyleSheet(f"font-size: 56px; font-weight: 900; color: {color_secondary};")
            self.lbl_no_source.setStyleSheet(f"color: {color_secondary}; font-size: 14px; background: transparent;")
            self.lbl_empty_log.setStyleSheet(f"color: {color_secondary}; font-size: 12px; margin-top: 30px;")
            self.video_area.setStyleSheet(f"background-color: {'#ffffff' if is_light else '#000000'}; border: 1px solid {'#d9dce1' if is_light else '#282a2f'}; border-radius: 12px;")
        else:
            color_running = "#119c5b" if is_light else "#35e192"
            self.lbl_count.setStyleSheet(f"font-size: 56px; font-weight: 900; color: {color_running};")
            self.video_area.setStyleSheet(f"background-color: {'#ffffff' if is_light else '#000000'}; border: 1px solid {'#3D8EF0' if is_light else '#3d8ef0'}; border-radius: 12px;")

        # Update per-class labels if they exist
        bg_col = '#f4f5f8' if is_light else '#282a2f'
        border_col = '#d9dce1' if is_light else '#414752'
        
        for cls, (lbl_name, lbl_val, frame) in getattr(self, '_class_count_labels', {}).items():
            lbl_name.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {color_primary}; border: none; background: transparent;")
            lbl_val.setStyleSheet(f"font-size: 32px; font-weight: 900; color: {color_primary}; border: none; background: transparent;")
            frame.setStyleSheet(f"background: {bg_col}; border: 1px solid {border_col}; border-radius: 8px;")

    # ── UI construction ──────────────────────────────────────────────
    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self._build_dashboard())

        self.history_page = HistoryPage()
        self.stacked_widget.addWidget(self.history_page)

        self.analytics_page = AnalyticsPage()
        self.stacked_widget.addWidget(self.analytics_page)

        root.addWidget(self.stacked_widget, stretch=1)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 25, 15, 25)

        self.title_lbl = QLabel("CounterApp")
        self.title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #e2e2e9;")
        self.subtitle_lbl = QLabel("PRECISION COUNTING")
        self.subtitle_lbl.setStyleSheet("font-size: 10px; color: #8b919e; letter-spacing: 1px;")
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.subtitle_lbl)
        layout.addSpacing(30)

        self.dash_btn = QPushButton("Dashboard")
        self.dash_btn.setProperty("class", "nav-btn")
        self.dash_btn.setProperty("active", "true")
        self.dash_btn.clicked.connect(self._switch_to_dashboard)

        self.hist_btn = QPushButton("History")
        self.hist_btn.setProperty("class", "nav-btn")
        self.hist_btn.clicked.connect(self._switch_to_history)

        self.analytics_btn = QPushButton("Analytics")
        self.analytics_btn.setProperty("class", "nav-btn")
        self.analytics_btn.clicked.connect(self._switch_to_analytics)

        layout.addWidget(self.dash_btn)
        layout.addWidget(self.hist_btn)
        layout.addWidget(self.analytics_btn)
        layout.addStretch()

        status_layout = QHBoxLayout()
        
        self.status_indicator = QLabel("● IDLE")
        self.status_indicator.setStyleSheet(
            "color: #8b919e; font-size: 10px; font-weight: bold; letter-spacing: 1px;"
        )
        status_layout.addWidget(self.status_indicator)
        status_layout.addStretch()
        
        self.theme_btn = ThemeSwitch()
        self.theme_btn.setChecked(theme_manager.is_light_mode)
        self.theme_btn.clicked.connect(theme_manager.toggle_theme)
        status_layout.addWidget(self.theme_btn)
        
        layout.addLayout(status_layout)
        return sidebar

    def _build_dashboard(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self._build_video_area(), stretch=1)
        content_layout.addWidget(self._build_right_panel())
        layout.addWidget(content, stretch=1)

        return container

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("top-header")
        header.setFixedHeight(64)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(25, 0, 25, 0)

        self.header_title = QLabel("Tactical Observatory")
        self.header_title.setStyleSheet("font-size: 22px; font-weight: 900; color: #e2e2e9;")
        hl.addWidget(self.header_title)
        hl.addStretch()

        self.source_badge = QLabel("")
        self.source_badge.setStyleSheet(
            "background-color: #282a2f; color: #a6c8ff;"
            "border: 1px solid #414752; border-radius: 4px;"
            "padding: 4px 10px; font-family: monospace; font-size: 11px;"
        )
        self.source_badge.hide()
        hl.addWidget(self.source_badge)
        hl.addSpacing(8)

        self.model_badge = QLabel("")
        self.model_badge.setStyleSheet(
            "background-color: #282a2f; color: #e2b4ff;"
            "border: 1px solid #414752; border-radius: 4px;"
            "padding: 4px 10px; font-family: monospace; font-size: 11px;"
        )
        self.model_badge.hide()
        hl.addWidget(self.model_badge)
        hl.addSpacing(8)

        self.fps_badge = QLabel("")
        self.fps_badge.setStyleSheet(
            "background-color: #282a2f; color: #ffb86c;"
            "border: 1px solid #414752; border-radius: 4px;"
            "padding: 4px 10px; font-family: monospace; font-size: 11px; font-weight: bold;"
        )
        self.fps_badge.hide()
        hl.addWidget(self.fps_badge)
        hl.addSpacing(16)

        self.btn_reset = QPushButton("RESET")
        self.btn_reset.setFixedWidth(100)
        self.btn_reset.setProperty("class", "btn-secondary")
        self.btn_reset.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_reset.hide()
        hl.addWidget(self.btn_reset)
        hl.addSpacing(8)

        self.btn_toggle = QPushButton("START")
        self.btn_toggle.setFixedWidth(130)
        self.btn_toggle.setProperty("class", "btn-primary")
        self.btn_toggle.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        hl.addWidget(self.btn_toggle)
        return header

    def _build_video_area(self) -> QWidget:
        video_wrap = QWidget()
        vw_layout = QVBoxLayout(video_wrap)
        vw_layout.setContentsMargins(20, 20, 20, 20)

        self.video_area = QFrame()
        self.video_area.setObjectName("video-area")
        grid = QGridLayout(self.video_area)
        grid.setContentsMargins(0, 0, 0, 0)

        self.lbl_no_source = QLabel(
            "Belum ada sumber video\n"
            "Tekan START untuk memilih sumber dan memulai counting"
        )
        self.lbl_no_source.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_no_source.setStyleSheet("color: #8b919e; font-size: 14px; background: transparent;")

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("background-color: transparent;")
        self.video_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.video_label.setMinimumSize(1, 1)
        self.video_label.hide()

        grid.addWidget(self.lbl_no_source, 0, 0)
        grid.addWidget(self.video_label, 0, 0)
        vw_layout.addWidget(self.video_area)
        return video_wrap

    def _build_right_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("right-panel")
        panel.setFixedWidth(360)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Count card
        count_card = QFrame()
        count_card.setProperty("class", "card-dark")
        cc_layout = QVBoxLayout(count_card)
        cc_layout.setContentsMargins(20, 20, 20, 20)

        c_header = QHBoxLayout()
        self.c_title = QLabel("TOTAL COUNT")
        self.c_title.setStyleSheet(
            "font-size: 10px; font-weight: 700; letter-spacing: 1px; color: #8b919e;"
        )
        c_header.addWidget(self.c_title)
        c_header.addStretch()

        self.lbl_count = QLabel("0")
        self.lbl_count.setStyleSheet("font-size: 56px; font-weight: 900; color: #8b919e;")

        self.counts_grid = QGridLayout()
        self.counts_grid.setContentsMargins(0, 10, 0, 0)
        self.counts_grid.setSpacing(10)
        self.counts_grid.addWidget(self.lbl_count, 0, 0)

        cc_layout.addLayout(c_header)
        cc_layout.addLayout(self.counts_grid)

        # Logs
        logs_title_layout = QHBoxLayout()
        self.logs_title = QLabel("RECENT LOGS")
        self.logs_title.setStyleSheet(
            "font-size: 10px; font-weight: 700; letter-spacing: 1px; color: #8b919e;"
        )
        logs_title_layout.addWidget(self.logs_title)
        logs_title_layout.addStretch()

        self.logs_container = QWidget()
        self.logs_layout = QVBoxLayout(self.logs_container)
        self.logs_layout.setContentsMargins(0, 0, 0, 0)
        self.logs_layout.setSpacing(5)

        self.lbl_empty_log = QLabel("Belum ada aktivitas deteksi\nyang tercatat.")
        self.lbl_empty_log.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_empty_log.setStyleSheet("color: #8b919e; font-size: 12px; margin-top: 30px;")
        self.logs_layout.addWidget(self.lbl_empty_log)
        self.logs_layout.addStretch()

        logs_scroll = QScrollArea()
        logs_scroll.setWidgetResizable(True)
        logs_scroll.setFrameShape(QFrame.Shape.NoFrame)
        logs_scroll.setStyleSheet("background: transparent;")
        logs_scroll.setWidget(self.logs_container)

        layout.addWidget(count_card)
        layout.addLayout(logs_title_layout)
        layout.addWidget(logs_scroll, stretch=1)
        return panel

    # Controller wiring
    def _connect_controller(self):
        self.controller = AppController(self)
        self.btn_toggle.clicked.connect(self.controller.toggle)
        self.btn_reset.clicked.connect(self.controller.reset_config)

    # Navigation
    def _switch_to_dashboard(self):
        self.stacked_widget.setCurrentIndex(0)
        self._set_nav(self.dash_btn, [self.hist_btn, self.analytics_btn])

    def _switch_to_history(self):
        self.stacked_widget.setCurrentIndex(1)
        self._set_nav(self.hist_btn, [self.dash_btn, self.analytics_btn])

    def _switch_to_analytics(self):
        self.stacked_widget.setCurrentIndex(2)
        self._set_nav(self.analytics_btn, [self.dash_btn, self.hist_btn])

    def _set_nav(self, active_btn, inactive_btns):
        active_btn.setProperty("active", "true")
        self._refresh_btn(active_btn)
        for btn in inactive_btns:
            btn.setProperty("active", "false")
            self._refresh_btn(btn)

    def _refresh_btn(self, btn):
        btn.style().unpolish(btn)
        btn.style().polish(btn)

    # Callbacks from AppController
    def on_state_changed(self, running: bool, source=None, model: str = ""):
        is_light = theme_manager.is_light_mode
        color_secondary = "#555e6d" if is_light else "#8b919e"
        
        if running:
            color_running = "#119c5b" if is_light else "#35e192"
            self.status_indicator.setText("● RUNNING")
            self.status_indicator.setStyleSheet(
                f"color: {color_running}; font-size: 10px; font-weight: bold; letter-spacing: 1px;"
            )
            self.btn_toggle.setText("STOP")
            self.btn_toggle.setProperty("class", "btn-danger")
            if hasattr(self, 'btn_reset'):
                self.btn_reset.hide()

            if source == 0 or source == "0":
                badge_text = "source: Webcam"
            else:
                badge_text = (
                    f"source: {os.path.basename(str(source))}"
                    if source and os.path.isfile(str(source))
                    else f"source: {source}"
                )
            self.source_badge.setText(badge_text)
            self.source_badge.show()

            if model:
                self.model_badge.setText(f"model: {os.path.basename(model)}")
                self.model_badge.show()

            self.fps_badge.setText("fps: 0")
            self.fps_badge.show()

            self.lbl_no_source.hide()
            self.video_label.show()
            video_bg = "#ffffff" if is_light else "#000000"
            border_col = "#3D8EF0" if is_light else "#3d8ef0"
            self.video_area.setStyleSheet(
                f"background-color: {video_bg}; border: 1px solid {border_col}; border-radius: 12px;"
            )
            self.lbl_count.setText("0")
            self.lbl_count.setStyleSheet(f"font-size: 56px; font-weight: 900; color: {color_running};")
            self.lbl_empty_log.hide()

        else:
            self.status_indicator.setText("● IDLE")
            self.status_indicator.setStyleSheet(
                f"color: {color_secondary}; font-size: 10px; font-weight: bold; letter-spacing: 1px;"
            )
            self.btn_toggle.setText("START")
            self.btn_toggle.setProperty("class", "btn-primary")
            
            if source is not None and model:
                if hasattr(self, 'btn_reset'):
                    self.btn_reset.show()
                if source == 0 or source == "0":
                    badge_text = "source: Webcam"
                else:
                    badge_text = (
                        f"source: {os.path.basename(str(source))}"
                        if source and os.path.isfile(str(source))
                        else f"source: {source}"
                    )
                self.source_badge.setText(badge_text)
                self.source_badge.show()
                self.model_badge.setText(f"model: {os.path.basename(model)}")
                self.model_badge.show()
                self.lbl_no_source.setText(f"Sumber tersimpan: {badge_text}\nTekan START untuk melanjutkan atau RESET untuk ganti sumber.")
            else:
                if hasattr(self, 'btn_reset'):
                    self.btn_reset.hide()
                self.source_badge.hide()
                self.model_badge.hide()
                self.lbl_no_source.setText(
                    "Belum ada sumber video\n"
                    "Tekan START untuk memilih sumber dan memulai counting"
                )

            self.fps_badge.hide()
            self.lbl_no_source.show()
            self.video_label.hide()
            video_bg = "#ffffff" if is_light else "#000000"
            border_col = "#d9dce1" if is_light else "#282a2f"
            self.video_area.setStyleSheet(
                f"background-color: {video_bg}; border: 1px solid {border_col}; border-radius: 12px;"
            )
            self.lbl_count.setText("0")
            self.lbl_count.setStyleSheet(f"font-size: 56px; font-weight: 900; color: {color_secondary};")
            self.lbl_count.show()
            
            for cls, (lbl_name, lbl_val, frame) in self._class_count_labels.items():
                frame.setParent(None)
                frame.deleteLater()
            self._class_count_labels.clear()

            self.lbl_empty_log.show()
            for w in self._log_widgets:
                w.setParent(None)
                w.deleteLater()
            self._log_widgets.clear()

        self._refresh_btn(self.btn_toggle)

    def on_count_updated(self, total: int, class_counts: dict = None):
        if class_counts is None or not class_counts:
            self.lbl_count.setText(f"{total:,}".replace(",", "."))
            self.lbl_count.show()
            for cls, (lbl_name, lbl_val, frame) in self._class_count_labels.items():
                frame.hide()
            return

        self.lbl_count.hide()
        
        is_light = theme_manager.is_light_mode
        color_primary = "#111318" if is_light else "#e2e2e9"
        bg_col = '#f4f5f8' if is_light else '#282a2f'
        border_col = '#d9dce1' if is_light else '#414752'

        for idx, (cls, count) in enumerate(class_counts.items()):
            if cls not in self._class_count_labels:
                frame = QFrame()
                frame.setStyleSheet(f"background: {bg_col}; border: 1px solid {border_col}; border-radius: 8px;")
                flay = QVBoxLayout(frame)
                flay.setContentsMargins(15, 12, 15, 12)
                
                lbl_name = QLabel(cls.upper())
                lbl_name.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {color_primary}; border: none; background: transparent;")
                
                lbl_val = QLabel(str(count))
                lbl_val.setStyleSheet(f"font-size: 32px; font-weight: 900; color: {color_primary}; border: none; background: transparent;")
                
                flay.addWidget(lbl_name)
                flay.addWidget(lbl_val)
                
                self._class_count_labels[cls] = (lbl_name, lbl_val, frame)
                
                self.counts_grid.addWidget(frame, idx, 0)
            else:
                lbl_name, lbl_val, frame = self._class_count_labels[cls]
                lbl_val.setText(str(count))
                frame.show()

    def on_fps_updated(self, fps: int):
        self.fps_badge.setText(f"fps: {fps}")

    def on_log_entry(self, icon: str, title: str, status: str, time_str: str):
        self.lbl_empty_log.hide()
        item = LogItem(icon, title, status, time_str)
        self.logs_layout.insertWidget(1, item)
        self._log_widgets.append(item)

        if len(self._log_widgets) > 20:
            oldest = self._log_widgets.pop(0)
            oldest.setParent(None)
            oldest.deleteLater()

    # Window close 
    def closeEvent(self, event):
        self.controller.shutdown()
        event.accept()
