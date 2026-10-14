"""Interactive region selection overlay for snippet screen capture."""
from typing import Optional
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QCursor, QFont
from PyQt6.QtWidgets import QWidget, QApplication
from src.stealth import apply_stealth_flags, stealth_show, stealth_hide


class SnippetOverlay(QWidget):
    """Fullscreen dim overlay for dragging and selecting a screen area."""

    area_selected = pyqtSignal(object)  # tuple (x, y, w, h) or None for full screen
    cancelled = pyqtSignal()

    DEFAULT_HINT = "✂️ Drag to capture region  •  Space: Full Screen  •  Esc: Cancel"

    def __init__(self):
        super().__init__()
        apply_stealth_flags(self)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        self.start_pos: Optional[QPoint] = None
        self.end_pos: Optional[QPoint] = None
        self.is_selecting = False
        self.hint_text = self.DEFAULT_HINT

    def start_selection(self, hint: Optional[str] = None):
        """Displays overlay over the primary screen geometry in pure stealth mode."""
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
        self.start_pos = None
        self.end_pos = None
        self.is_selecting = False
        self.hint_text = hint or self.DEFAULT_HINT
        stealth_show(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self.is_selecting = True
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self.close_and_cancel()

    def mouseDoubleClickEvent(self, event):
        """Double click to capture full screen instantly."""
        stealth_hide(self)
        self.area_selected.emit(None)

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.end_pos = event.pos()
            stealth_hide(self)

            if self.start_pos and self.end_pos:
                rect = QRect(self.start_pos, self.end_pos).normalized()
                # Ignore accidental clicks with tiny dimensions
                if rect.width() > 20 and rect.height() > 20:
                    # Convert to global coordinates
                    global_top_left = self.mapToGlobal(rect.topLeft())
                    self.area_selected.emit((
                        global_top_left.x(),
                        global_top_left.y(),
                        rect.width(),
                        rect.height()
                    ))
                else:
                    self.cancelled.emit()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.close_and_cancel()
        elif key in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Capture full screen
            stealth_hide(self)
            self.area_selected.emit(None)

    def close_and_cancel(self):
        self.is_selecting = False
        stealth_hide(self)
        self.cancelled.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw semi-transparent dim overlay
        overlay_color = QColor(10, 10, 15, 140)
        painter.fillRect(self.rect(), overlay_color)

        if self.start_pos and self.end_pos:
            rect = QRect(self.start_pos, self.end_pos).normalized()

            # Clear the selected area to transparent so background is clearly visible
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, Qt.GlobalColor.transparent)

            # Switch back to normal paint mode to draw glowing border & info badge
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            # Border
            pen = QPen(QColor(99, 102, 241, 240), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

            # Dimension tag (e.g. "800 x 600 px")
            dim_text = f"{rect.width()} × {rect.height()} px"
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
            badge_rect = QRect(rect.left(), max(0, rect.top() - 25), 110, 22)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(24, 24, 27, 220)))
            painter.drawRoundedRect(badge_rect, 4, 4)

            painter.setPen(QColor(220, 220, 240))
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, dim_text)
        else:
            # Draw instruction badge at the top-center
            badge_width = 560
            badge_height = 42
            badge_x = (self.width() - badge_width) // 2
            badge_y = 36
            banner_rect = QRect(badge_x, badge_y, badge_width, badge_height)

            painter.setPen(QPen(QColor(99, 102, 241, 180), 1))
            painter.setBrush(QBrush(QColor(20, 20, 26, 230)))
            painter.drawRoundedRect(banner_rect, 10, 10)

            painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
            painter.setPen(QColor(244, 244, 245, 235))
            painter.drawText(banner_rect, Qt.AlignmentFlag.AlignCenter, self.hint_text)
