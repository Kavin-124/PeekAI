"""Floating guide bar shown when user wants to scroll and append a screenshot."""
import sys
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QFont, QKeySequence
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGraphicsDropShadowEffect, QApplication
)
from src.config import Config


class AppendOverlay(QWidget):
    """
    Sleek floating top bar that guides user to scroll page before snapping.
    Allows snapping the scrolled page via button, Enter key, or cropping a region.
    """

    snap_full_requested = pyqtSignal()
    snap_snippet_requested = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position: QPoint = None
        self._init_window()
        self._init_ui()
        self._apply_styles()

    def _init_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.resize(580, 68)

        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = int(self.winId())
                GWL_EXSTYLE = -20
                WS_EX_NOACTIVATE = 0x08000000
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE)
            except Exception:
                pass

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Card container
        self.card = QFrame()
        self.card.setObjectName("cardFrame")

        # Shadow
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(6)
        self.shadow.setColor(QColor(15, 23, 42, 45) if Config.get_theme() != "dark" else QColor(0, 0, 0, 180))
        self.card.setGraphicsEffect(self.shadow)

        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(16, 8, 16, 8)
        card_layout.setSpacing(10)

        # Guide label
        self.guide_label = QLabel("📜 <b>Scroll down</b> to question, then:")
        self.guide_label.setObjectName("guideLabel")
        card_layout.addWidget(self.guide_label)

        card_layout.addStretch()

        # 1. Snap Full Screen button
        self.snap_btn = QPushButton("📸 Snap Scrolled Screen")
        self.snap_btn.setObjectName("snapBtn")
        self.snap_btn.setToolTip("Capture screen after scrolling (or press Enter)")
        self.snap_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.snap_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.snap_btn.clicked.connect(self._on_snap_clicked)
        card_layout.addWidget(self.snap_btn)

        # 2. Crop Region button
        self.crop_btn = QPushButton("✂️ Crop Region")
        self.crop_btn.setObjectName("cropBtn")
        self.crop_btn.setToolTip("Crop only the scrolled column or area")
        self.crop_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.crop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.crop_btn.clicked.connect(self._on_crop_clicked)
        card_layout.addWidget(self.crop_btn)

        # 3. Cancel button
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setToolTip("Cancel and restore HUD (Esc)")
        self.cancel_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        card_layout.addWidget(self.cancel_btn)

        layout.addWidget(self.card)

    def _apply_styles(self):
        is_light = (Config.get_theme() != "dark")
        if hasattr(self, 'shadow'):
            self.shadow.setColor(QColor(15, 23, 42, 45) if is_light else QColor(0, 0, 0, 180))

        if is_light:
            self.setStyleSheet("""
                #cardFrame {
                    background-color: #ffffff;
                    border: 1px solid #cbd5e1;
                    border-radius: 12px;
                }
                #guideLabel {
                    color: #0f172a;
                    font-size: 13px;
                    font-family: 'Segoe UI', system-ui, sans-serif;
                }
                #snapBtn {
                    background-color: #4f46e5;
                    color: #ffffff;
                    border: 1px solid #4338ca;
                    border-radius: 7px;
                    padding: 7px 14px;
                    font-weight: 600;
                    font-size: 12px;
                }
                #snapBtn:hover {
                    background-color: #4338ca;
                }
                #cropBtn {
                    background-color: #f8fafc;
                    color: #1e293b;
                    border: 1px solid #cbd5e1;
                    border-radius: 7px;
                    padding: 7px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }
                #cropBtn:hover {
                    background-color: #f1f5f9;
                    color: #0f172a;
                    border-color: #94a3b8;
                }
                #cancelBtn {
                    background-color: transparent;
                    border: none;
                    color: #64748b;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 6px 10px;
                    border-radius: 6px;
                }
                #cancelBtn:hover {
                    background-color: #f1f5f9;
                    color: #e11d48;
                }
            """)
        else:
            self.setStyleSheet("""
                #cardFrame {
                    background-color: #16161a;
                    border: 1px solid #4338ca;
                    border-radius: 12px;
                }
                #guideLabel {
                    color: #e0e7ff;
                    font-size: 13px;
                    font-family: 'Segoe UI', system-ui, sans-serif;
                }
                #snapBtn {
                    background-color: #4f46e5;
                    color: #ffffff;
                    border: 1px solid #6366f1;
                    border-radius: 7px;
                    padding: 7px 14px;
                    font-weight: 600;
                    font-size: 12px;
                }
                #snapBtn:hover {
                    background-color: #4338ca;
                }
                #cropBtn {
                    background-color: #27272e;
                    color: #cbd5e1;
                    border: 1px solid #3b3b45;
                    border-radius: 7px;
                    padding: 7px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }
                #cropBtn:hover {
                    background-color: #33333d;
                    color: #ffffff;
                }
                #cancelBtn {
                    background-color: transparent;
                    border: none;
                    color: #71717a;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 6px 10px;
                    border-radius: 6px;
                }
                #cancelBtn:hover {
                    background-color: #27272a;
                    color: #f43f5e;
                }
            """)

    def show_guide(self):
        """Centers overlay at the top of the active primary screen and shows it."""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = screen_geo.x() + (screen_geo.width() - self.width()) // 2
            y = screen_geo.y() + 20
            self.move(x, y)
        self.show()
        self.raise_()
        if sys.platform == "win32":
            try:
                import ctypes
                SW_SHOWNOACTIVATE = 4
                ctypes.windll.user32.ShowWindow(int(self.winId()), SW_SHOWNOACTIVATE)
            except Exception:
                pass

    def _on_snap_clicked(self):
        self.hide()
        self.snap_full_requested.emit()

    def _on_crop_clicked(self):
        self.hide()
        self.snap_snippet_requested.emit()

    def _on_cancel_clicked(self):
        self.hide()
        self.cancelled.emit()

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self._on_snap_clicked()
        elif key == Qt.Key.Key_Escape:
            self._on_cancel_clicked()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
