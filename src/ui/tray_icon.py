"""System tray icon integration for PeekAI."""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu


def create_default_tray_pixmap() -> QPixmap:
    """Draws a clean modern circular icon with a lightning bolt."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0)) # transparent

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Gradient or solid dark purple background circle
    painter.setBrush(QColor(99, 102, 241)) # Indigo
    painter.setPen(QColor(129, 140, 248))
    painter.drawEllipse(4, 4, 56, 56)

    # Letter 'P' or symbol
    painter.setPen(QColor(255, 255, 255))
    font = QFont("Segoe UI", 24, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), 0x0004 | 0x0080, "P") # AlignCenter
    painter.end()

    return pixmap


class TrayIcon(QSystemTrayIcon):
    """System tray manager for PeekAI."""

    trigger_full_peek = pyqtSignal()
    trigger_snippet_peek = pyqtSignal()
    trigger_append_peek = pyqtSignal()
    open_hud = pyqtSignal()
    open_settings = pyqtSignal()
    quit_app = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon(create_default_tray_pixmap()))
        self.setToolTip("PeekAI - Instant Screen Copilot")
        self._init_menu()
        self.activated.connect(self._on_tray_activated)

    def _init_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #1c1c22;
                color: #f4f4f5;
                border: 1px solid #2e2e38;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', sans-serif;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #6366f1;
                color: #ffffff;
            }
            QMenu::separator {
                height: 1px;
                background-color: #2e2e38;
                margin: 4px 6px;
            }
        """)

        # Actions
        peek_full_action = menu.addAction("⚡ Peek Full Screen  (Ctrl+Shift+Space)")
        peek_full_action.triggered.connect(self.trigger_full_peek.emit)

        peek_snippet_action = menu.addAction("✂️ Peek Region  (Ctrl+Shift+X)")
        peek_snippet_action.triggered.connect(self.trigger_snippet_peek.emit)

        peek_append_action = menu.addAction("➕ Snap & Append Scrolled Screen  (Ctrl+Shift+A)")
        peek_append_action.triggered.connect(self.trigger_append_peek.emit)

        menu.addSeparator()

        open_hud_action = menu.addAction("🪟 Open Floating HUD")
        open_hud_action.triggered.connect(self.open_hud.emit)

        settings_action = menu.addAction("⚙️ Settings...")
        settings_action.triggered.connect(self.open_settings.emit)

        menu.addSeparator()

        exit_action = menu.addAction("🚪 Exit PeekAI")
        exit_action.triggered.connect(self.quit_app.emit)

        self.setContextMenu(menu)

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.open_hud.emit()
