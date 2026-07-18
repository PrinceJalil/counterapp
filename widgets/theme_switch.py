from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtCore import Qt, QRect, QRectF, QPropertyAnimation, pyqtProperty, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPainterPath


class ThemeSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(70, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._thumb_position = 2
        self.animation = QPropertyAnimation(self, b"thumb_position")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.setDuration(250)
        
        self.stateChanged.connect(self.setup_animation)

    @pyqtProperty(int)
    def thumb_position(self):
        return self._thumb_position

    @thumb_position.setter
    def thumb_position(self, pos):
        self._thumb_position = pos
        self.update()

    def setup_animation(self, value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(self.width() - 26)
        else:
            self.animation.setEndValue(2)
        self.animation.start()

    def hitButton(self, pos):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_light = self.isChecked()
        
        # Colors
        track_color = QColor("#d9dce1") if is_light else QColor("#282a2f")
        thumb_color = QColor("#ffffff") if is_light else QColor("#8b919e")
        text_color = QColor("#555e6d") if is_light else QColor("#a6aebf")

        # Draw track
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, float(self.width()), float(self.height())), 14, 14)
        p.fillPath(path, track_color)

        # Draw text
        font = p.font()
        font.setPointSize(9)
        font.setBold(True)
        p.setFont(font)
        p.setPen(text_color)
        
        if is_light:
            p.drawText(QRect(10, 0, self.width() - 26, self.height()), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Light")
        else:
            p.drawText(QRect(0, 0, self.width() - 10, self.height()), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "Dark")

        # Draw thumb
        thumb_rect = QRectF(float(self._thumb_position), 2.0, 24.0, 24.0)
        thumb_path = QPainterPath()
        thumb_path.addEllipse(thumb_rect)
        p.fillPath(thumb_path, thumb_color)
        
        p.end()
