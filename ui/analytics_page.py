import os
import sqlite3
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np

from utils.theme_manager import theme_manager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "database.db")

COLOR_PALETTE = ['#5a9cf8', '#35e192', '#a0a5b5', '#e2b4ff', '#ffb86c', '#ff6b6b']

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=8, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        
        is_light = theme_manager.is_light_mode
        bg_col = '#ffffff' if is_light else '#0c0e13'
        text_col = '#555e6d' if is_light else '#8b919e'
        
        self.fig.patch.set_facecolor(bg_col)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_facecolor(bg_col)
        
        self.axes.tick_params(colors=text_col, labelsize=10)
        self.axes.spines['bottom'].set_color('none')
        self.axes.spines['top'].set_color('none')
        self.axes.spines['right'].set_color('none')
        self.axes.spines['left'].set_color('none')
        
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()

class AnalyticsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bars_info = []
        self.current_hover_bar = None
        
        self._init_ui()
        self._apply_styles()
        self.load_data()

        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(5000)
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start()
        
        theme_manager.theme_changed.connect(self.apply_theme)

    def _auto_refresh(self):
        if self.isVisible():
            self.load_data()

    def showEvent(self, event):
        self.load_data()
        super().showEvent(event)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────
        header = QFrame()
        header.setObjectName("top-header")
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 0, 30, 0)

        self.title_lbl = QLabel("Analytics")
        is_light = theme_manager.is_light_mode
        self.title_lbl.setStyleSheet(f"font-size: 24px; font-weight: 900; color: {'#111318' if is_light else '#e2e2e9'};")
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        
        main_layout.addWidget(header)

        # ── Content ───────────────────────────────────────────────────────
        content_wrapper = QWidget()
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(30, 20, 30, 30)

        # Chart Container
        chart_container = QFrame()
        chart_container.setObjectName("chart-container")
        chart_layout = QVBoxLayout(chart_container)
        chart_layout.setContentsMargins(30, 30, 30, 30)

        # Chart Header
        ch_header = QHBoxLayout()
        self.chart_title = QLabel("Detection Volume")
        is_light = theme_manager.is_light_mode
        self.chart_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {'#111318' if is_light else '#e2e2e9'};")
        ch_header.addWidget(self.chart_title)
        
        ch_header.addStretch()
        
        # Timeframe Filter Dropdown
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["Weekly", "Monthly", "Yearly", "All Dates"])
        self.timeframe_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.timeframe_combo.setMinimumWidth(110)
        self.timeframe_combo.currentTextChanged.connect(self.load_data)
        ch_header.addWidget(self.timeframe_combo)
        
        ch_header.addSpacing(15)

        # Class Filter Dropdown
        self.class_combo = QComboBox()
        self.class_combo.addItem("All Classes")
        self.class_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.class_combo.setMinimumWidth(130)
        self.class_combo.currentTextChanged.connect(self.load_data)
        ch_header.addWidget(self.class_combo)

        chart_layout.addLayout(ch_header)
        chart_layout.addSpacing(20)

        # Canvas
        self.canvas = MplCanvas(self, width=8, height=4, dpi=100)
        chart_layout.addWidget(self.canvas, stretch=1)
        
        # Connect hover event
        self.canvas.mpl_connect("motion_notify_event", self.hover)
        
        # Legend
        self.legend_layout = QHBoxLayout()
        self.legend_layout.setSpacing(30)
        self.legend_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        chart_layout.addSpacing(15)
        chart_layout.addLayout(self.legend_layout)

        content_layout.addWidget(chart_container, stretch=1)
        main_layout.addWidget(content_wrapper, stretch=1)
        
        self._populate_class_combo()

    def _populate_class_combo(self):
        if not os.path.exists(DB_PATH):
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT class_name FROM history_logs ORDER BY class_name")
        rows = cursor.fetchall()
        conn.close()
        
        current_text = self.class_combo.currentText()
        self.class_combo.blockSignals(True)
        self.class_combo.clear()
        self.class_combo.addItem("All Classes")
        for row in rows:
            self.class_combo.addItem(row[0])
            
        index = self.class_combo.findText(current_text)
        if index >= 0:
            self.class_combo.setCurrentIndex(index)
        self.class_combo.blockSignals(False)

    def _update_legend(self, classes):
        while self.legend_layout.count():
            child = self.legend_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        for i, cls_name in enumerate(classes):
            color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
            
            legend_item = QWidget()
            li_layout = QHBoxLayout(legend_item)
            li_layout.setContentsMargins(0, 0, 0, 0)
            li_layout.setSpacing(8)
            
            color_box = QLabel()
            color_box.setFixedSize(14, 14)
            color_box.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
            
            lbl = QLabel(cls_name)
            is_light = theme_manager.is_light_mode
            lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {'#111318' if is_light else '#e2e2e9'};")
            
            li_layout.addWidget(color_box)
            li_layout.addWidget(lbl)
            self.legend_layout.addWidget(legend_item)

    def _create_annotation(self):
        is_light = theme_manager.is_light_mode
        bg_col = "#ffffff" if is_light else "#1e1f25"
        border_col = "#d9dce1" if is_light else "#414752"
        text_col = "#111318" if is_light else "#e2e2e9"
        
        # Tampilkan tooltip di sebelah kanan (xytext=(15, 0)), ha="left", va="center"
        self.annot = self.canvas.axes.annotate(
            "", xy=(0,0), xytext=(15, 0), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.6", fc=bg_col, ec=border_col, lw=1.5, alpha=0.95),
            color=text_col, fontsize=10, zorder=20, ha="left", va="center"
        )
        self.annot.set_visible(False)
        self.current_hover_bar = None

    def hover(self, event):
        if not hasattr(self, 'annot') or not self.annot:
            return

        is_in_axes = (event.inaxes == self.canvas.axes)
        found_bar = None
        info_found = None

        if is_in_axes:
            for info in self.bars_info:
                bar = info['bar']
                cont, _ = bar.contains(event)
                if cont:
                    found_bar = bar
                    info_found = info
                    break

        if found_bar:
            if self.current_hover_bar != found_bar:
                self.current_hover_bar = found_bar
                self.update_annot(found_bar, info_found)
                self.annot.set_visible(True)
                self.canvas.draw_idle()
        else:
            if self.current_hover_bar is not None:
                self.current_hover_bar = None
                self.annot.set_visible(False)
                self.canvas.draw_idle()

    def update_annot(self, bar, info):
        # Determine whether to show tooltip on the left or right to prevent clipping
        x_bar = bar.get_x()
        xlim = self.canvas.axes.get_xlim()
        
        # If the bar is in the rightmost 30% of the chart, show tooltip on the left
        if x_bar > xlim[0] + 0.7 * (xlim[1] - xlim[0]):
            # Show on the left of the bar
            x = bar.get_x()
            self.annot.set_position((-15, 0)) # xytext is updated via set_position
            self.annot.set_ha("right")
        else:
            # Show on the right of the bar
            x = bar.get_x() + bar.get_width()
            self.annot.set_position((15, 0))
            self.annot.set_ha("left")

        y = bar.get_y() + bar.get_height() / 2.
        self.annot.xy = (x, y)
        
        label = info['label']
        cls_name = info['class_name']
        count = info['count']
        
        text = f"{label}\n■ {cls_name}: {count:,}".replace(',', '.')
        self.annot.set_text(text)
        
        bbox = self.annot.get_bbox_patch()
        if bbox:
            bbox.set_edgecolor(info['color'])

    def load_data(self):
        self._populate_class_combo()
        self.bars_info = []
        
        timeframe = self.timeframe_combo.currentText()
        selected_class = self.class_combo.currentText()
        
        if not os.path.exists(DB_PATH):
            self._render_empty()
            return
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        class_filter = ""
        params = []
        if selected_class != "All Classes":
            class_filter = "AND class_name = ?"
            params.append(selected_class)
            
        cursor.execute("SELECT DISTINCT class_name FROM history_logs WHERE 1=1 " + class_filter, params)
        classes = [r[0] for r in cursor.fetchall()]
        
        today = datetime.now()
        categories = []
        
        if timeframe == "Weekly":
            for i in range(6, -1, -1):
                d = today - timedelta(days=i)
                categories.append({
                    "label": d.strftime("%d %b"),
                    "start": d.strftime("%Y-%m-%d 00:00:00"),
                    "end": d.strftime("%Y-%m-%d 23:59:59")
                })
                
        elif timeframe == "Monthly":
            ranges = [(29, 23), (22, 16), (15, 8), (7, 0)]
            for start_offset, end_offset in ranges:
                d_start = today - timedelta(days=start_offset)
                d_end = today - timedelta(days=end_offset)
                categories.append({
                    "label": f"{d_start.strftime('%d %b')} - {d_end.strftime('%d %b')}",
                    "start": d_start.strftime("%Y-%m-%d 00:00:00"),
                    "end": d_end.strftime("%Y-%m-%d 23:59:59")
                })
                
        elif timeframe == "All Dates":
            cursor.execute("SELECT DISTINCT strftime('%Y', timestamp) FROM history_logs WHERE 1=1 " + class_filter + " ORDER BY timestamp", params)
            years = [r[0] for r in cursor.fetchall() if r[0] is not None]
            if not years:
                years = [str(today.year)]
                
            for y in years:
                y_int = int(y)
                start_d = datetime(y_int, 1, 1)
                end_d = datetime(y_int + 1, 1, 1) - timedelta(seconds=1)
                categories.append({
                    "label": y,
                    "start": start_d.strftime("%Y-%m-%d 00:00:00"),
                    "end": end_d.strftime("%Y-%m-%d 23:59:59")
                })

        else:
            year = today.year
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            for i in range(1, 13):
                start_d = datetime(year, i, 1)
                if i == 12:
                    end_d = datetime(year + 1, 1, 1) - timedelta(seconds=1)
                else:
                    end_d = datetime(year, i + 1, 1) - timedelta(seconds=1)
                
                categories.append({
                    "label": month_names[i-1],
                    "start": start_d.strftime("%Y-%m-%d 00:00:00"),
                    "end": end_d.strftime("%Y-%m-%d 23:59:59")
                })

        data_map = {idx: {cls: 0 for cls in classes} for idx in range(len(categories))}
        
        for idx, cat in enumerate(categories):
            query = f'''
                SELECT class_name, SUM(count_in)
                FROM history_logs
                WHERE timestamp >= ? AND timestamp <= ? {class_filter}
                GROUP BY class_name
            '''
            q_params = [cat["start"], cat["end"]] + params
            cursor.execute(query, q_params)
            for row in cursor.fetchall():
                c_name, c_count = row[0], row[1]
                if c_name in data_map[idx]:
                    data_map[idx][c_name] += c_count

        conn.close()

        self.canvas.axes.clear()
        self._format_axes()
        self._create_annotation()
        self._update_legend(classes)

        if not classes:
            self._render_empty()
            return

        x = np.arange(len(categories))
        n_classes = len(classes)
        group_width = 0.7
        bar_width = group_width / n_classes if n_classes > 0 else group_width
        
        for i, cls_name in enumerate(classes):
            counts = [data_map[idx][cls_name] for idx in range(len(categories))]
            offset = (i - n_classes/2.0 + 0.5) * bar_width
            color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
            bars = self.canvas.axes.bar(x + offset, counts, bar_width * 0.85, color=color, alpha=1.0, zorder=3)
            
            for bar, count, cat in zip(bars, counts, categories):
                self.bars_info.append({
                    'bar': bar,
                    'label': cat['label'],
                    'class_name': cls_name,
                    'count': count,
                    'color': color
                })

        labels = [cat["label"] for cat in categories]
        self.canvas.axes.set_xticks(x)
        is_light = theme_manager.is_light_mode
        self.canvas.axes.set_xticklabels(labels, color='#555e6d' if is_light else '#8b919e', fontsize=11, fontweight='bold')
        
        # Memastikan diagram dengan kategori sedikit (1-4) rata kiri
        if len(categories) < 5:
            self.canvas.axes.set_xlim(-0.5, 4.5)
        
        def y_fmt(tick_val, pos):
            if tick_val >= 1000:
                val = int(tick_val) / 1000.0
                return f'{val:g}k'
            else:
                return f'{int(tick_val)}'
                
        self.canvas.axes.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(y_fmt))
        is_light = theme_manager.is_light_mode
        grid_col = '#e2e4e9' if is_light else '#282a2f'
        self.canvas.axes.grid(axis='y', color=grid_col, linestyle='-', linewidth=1, zorder=0)

        self.canvas.fig.tight_layout()
        self.canvas.draw()

    def _render_empty(self):
        self.canvas.axes.clear()
        self._format_axes()
        self._create_annotation()
        self._update_legend([])
        is_light = theme_manager.is_light_mode
        self.canvas.axes.text(0.5, 0.5, 'No Data Available', 
                             horizontalalignment='center', verticalalignment='center',
                             color='#555e6d' if is_light else '#8b919e', fontsize=12)
        self.canvas.draw()

    def _format_axes(self):
        is_light = theme_manager.is_light_mode
        bg_col = '#ffffff' if is_light else '#0c0e13'
        text_col = '#555e6d' if is_light else '#8b919e'
        
        self.canvas.fig.patch.set_facecolor(bg_col)
        self.canvas.axes.set_facecolor(bg_col)
        self.canvas.axes.tick_params(colors=text_col, length=0, pad=10)
        self.canvas.axes.spines['bottom'].set_color('none')
        self.canvas.axes.spines['top'].set_color('none')
        self.canvas.axes.spines['right'].set_color('none')
        self.canvas.axes.spines['left'].set_color('none')

    def apply_theme(self, is_light: bool):
        self.title_lbl.setStyleSheet(f"font-size: 24px; font-weight: 900; color: {'#111318' if is_light else '#e2e2e9'};")
        self.chart_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {'#111318' if is_light else '#e2e2e9'};")
        self._apply_styles()
        self.load_data()  # Reloads canvas colors and legends

    def _apply_styles(self):
        is_light = theme_manager.is_light_mode
        
        bg_main = "#f4f5f8" if is_light else "#111318"
        text_col = "#111318" if is_light else "#e2e2e9"
        card_bg = "#ffffff" if is_light else "#0c0e13"
        input_bg = "#ffffff" if is_light else "#1a1b21"
        input_border = "#c8cbd2" if is_light else "#33353a"
        dropdown_bg = "#e2e4e9" if is_light else "#282a2f"
        list_bg = "#ffffff" if is_light else "#1e1f25"
        
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            AnalyticsPage {{ background-color: {bg_main}; }}
            #top-header {{ background-color: {bg_main}; }}
            QWidget {{ color: {text_col}; font-family: 'Segoe UI', 'Inter', Arial, sans-serif; }}
            
            #chart-container {{
                background-color: {card_bg}; border-radius: 16px; border: 1px solid {'#d9dce1' if is_light else 'transparent'};
            }}
            
            QComboBox {{
                background-color: {input_bg};
                color: {'#555e6d' if is_light else '#8b919e'};
                border: 1px solid {input_border};
                border-radius: 8px;
                padding: 6px 30px 6px 14px;
                font-size: 12px;
                font-weight: bold;
            }}
            QComboBox:hover {{
                background-color: {dropdown_bg};
                color: {text_col};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: url('data:image/svg+xml;utf8,<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="%23{'555e6d' if is_light else '8b919e'}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>');
            }}
            QComboBox:hover::down-arrow {{
                image: url('data:image/svg+xml;utf8,<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="%23{'111318' if is_light else 'e2e2e9'}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>');
            }}
            QComboBox QAbstractItemView {{
                background-color: {list_bg};
                color: {text_col};
                selection-background-color: #3D8EF0;
                border: 1px solid {input_border};
                outline: none;
            }}
        """)
