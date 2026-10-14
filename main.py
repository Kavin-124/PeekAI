import sys
import os
import time
import traceback
from typing import Optional
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

from src.config import Config
from src.capture import capture_screen
from src.ai_service import AIService
from src.hotkey_listener import HotkeyListener
from src.ui.floating_hud import FloatingHUD
from src.ui.snippet_overlay import SnippetOverlay
from src.ui.append_overlay import AppendOverlay
from src.ui.tray_icon import TrayIcon
from src.ui.settings_dialog import SettingsDialog
from src.stealth import stealth_show, stealth_hide


def _global_exception_handler(ex_type, ex_val, ex_tb):
    """Logs any uncaught exceptions to crash.log and alerts user."""
    crash_file = os.path.join(os.path.dirname(__file__), "crash.log")
    try:
        with open(crash_file, "a", encoding="utf-8") as f:
            f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Uncaught Exception:\n")
            traceback.print_exception(ex_type, ex_val, ex_tb, file=f)
    except Exception:
        pass
    try:
        QMessageBox.critical(
            None,
            "PeekAI Notice",
            f"PeekAI encountered an unexpected issue:\n{ex_val}\n\nDetails saved to crash.log"
        )
    except Exception:
        pass

sys.excepthook = _global_exception_handler


class PeekAIApp:
    """Core controller coordinating HUD, capture, hotkeys, and AI engine."""

    def __init__(self, qapp: QApplication):
        self.qapp = qapp
        self.ai_service = AIService()

        # UI Components
        self.hud = FloatingHUD(self.ai_service)
        self.snippet_overlay = SnippetOverlay()
        self.append_overlay = AppendOverlay()
        self.tray_icon = TrayIcon()
        self.settings_dialog = SettingsDialog()

        # Background listener & state
        self.hotkey_listener = HotkeyListener()
        self._pending_append_snippet = False

        self._wire_signals()

    def _wire_signals(self):
        # Hotkeys -> Triggers
        self.hotkey_listener.full_peek_triggered.connect(self.trigger_full_peek)
        self.hotkey_listener.snippet_peek_triggered.connect(self.trigger_snippet_peek)
        self.hotkey_listener.append_peek_triggered.connect(self.start_guided_append)
        self.hotkey_listener.copy_peek_triggered.connect(self.hud._copy_answer)
        self.hotkey_listener.settings_triggered.connect(self._show_settings)

        # Snippet selection -> Capture & Analyze
        self.snippet_overlay.area_selected.connect(self._on_snippet_selected)
        self.snippet_overlay.cancelled.connect(self._on_snippet_cancelled)

        # Append Overlay Guide signals
        self.append_overlay.snap_full_requested.connect(self._perform_append_capture)
        self.append_overlay.snap_snippet_requested.connect(self._start_append_snippet)
        self.append_overlay.cancelled.connect(self._on_append_cancelled)

        # Tray actions
        self.tray_icon.trigger_full_peek.connect(self.trigger_full_peek)
        self.tray_icon.trigger_snippet_peek.connect(self.trigger_snippet_peek)
        self.tray_icon.trigger_append_peek.connect(self.start_guided_append)
        self.tray_icon.open_hud.connect(self.show_hud_stealth)
        self.tray_icon.open_settings.connect(self._show_settings)
        self.tray_icon.quit_app.connect(self.quit)

        # HUD actions
        self.hud.request_repeek.connect(self.trigger_full_peek)
        self.hud.request_append.connect(self.start_guided_append)
        self.hud.request_settings.connect(self._show_settings)

        # Settings saved
        self.settings_dialog.settings_saved.connect(self._on_settings_saved)

    def start(self):
        """Starts the application and shows the floating HUD in stealth mode."""
        self.tray_icon.show()
        self.hotkey_listener.start()

        # Open settings dialog directly if API key is not configured
        if not Config.is_configured():
            QTimer.singleShot(200, self._show_settings)
        else:
            # Immediately show the floating HUD in stealth mode (zero focus stealing!)
            QTimer.singleShot(100, self.show_hud_stealth)
            self.tray_icon.showMessage(
                "PeekAI is running (Stealth)",
                "Ctrl+Shift+Space: Full Peek | Ctrl+Shift+X: Snippet | Ctrl+Shift+A: Append | Ctrl+Alt+C: Copy Answer",
                TrayIcon.MessageIcon.Information,
                2500
            )

    def show_hud_stealth(self):
        """Restores HUD in pure stealth mode without stealing focus from browser/exam window."""
        stealth_show(self.hud)

    def show_and_activate(self):
        """Alias for backward compatibility - safely redirects to stealth mode."""
        self.show_hud_stealth()

    def _show_hud(self):
        self.show_hud_stealth()

    def _show_settings(self):
        self.settings_dialog._load_current_values()
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def _on_settings_saved(self):
        # Apply theme updates immediately without requiring restart
        if hasattr(self, "hud"):
            self.hud._apply_styles()
            if not self.hud.full_response_text:
                self.hud._clear_content()
        if hasattr(self, "append_overlay"):
            self.append_overlay._apply_styles()

        # Restart hotkey listener in case user changed shortcuts
        self.hotkey_listener.start()

    def trigger_full_peek(self):
        """Captures entire screen and sends to Gemini AI in pure stealth mode."""
        if not Config.is_configured():
            self._show_settings()
            return

        # Hide append overlay if active
        if self.append_overlay.isVisible():
            stealth_hide(self.append_overlay)

        # Full capture runs cleanly (HUD is hardware-excluded from capture via WDA_EXCLUDEFROMCAPTURE)
        self._perform_full_capture()

    def _perform_full_capture(self):
        try:
            img_bytes, pil_img, _ = capture_screen()
            self.hud.start_analysis(img_bytes, pil_img, append=False)
        except Exception as e:
            QMessageBox.critical(None, "Capture Error", f"Failed to capture screen:\n{str(e)}")

    def start_guided_append(self):
        """
        Opened when user clicks 'Snap & Append' on the HUD or tray.
        Hides HUD and presents top floating helper bar allowing user to scroll first.
        """
        if not Config.is_configured():
            self._show_settings()
            return

        stealth_hide(self.hud)
        self.append_overlay.show_guide()

    def trigger_append_peek(self):
        """
        Triggered when user presses Ctrl+Shift+A directly from keyboard.
        Opens the snippet crop overlay in append mode so the user can drag & select the scrolled portion!
        """
        if not Config.is_configured():
            self._show_settings()
            return

        if self.append_overlay.isVisible():
            stealth_hide(self.append_overlay)

        self._pending_append_snippet = True
        self.snippet_overlay.start_selection(
            hint="📸 Drag to crop scrolled section to append  •  Space: Full Screen  •  Esc: Cancel"
        )

    def _perform_append_capture(self):
        try:
            img_bytes, pil_img, _ = capture_screen()
            self.hud.start_analysis(img_bytes, pil_img, append=True)
        except Exception as e:
            QMessageBox.critical(None, "Capture Error", f"Failed to capture screen:\n{str(e)}")

    def _start_append_snippet(self):
        """User chose to crop a specific region from the guided append overlay."""
        self._pending_append_snippet = True
        self.snippet_overlay.start_selection(
            hint="📸 Drag to crop scrolled section to append  •  Space: Full Screen  •  Esc: Cancel"
        )

    def _on_append_cancelled(self):
        """User cancelled guided append mode."""
        self._pending_append_snippet = False
        if self.hud.captured_images:
            stealth_show(self.hud)

    def trigger_snippet_peek(self):
        """Opens interactive snippet selector to capture a specific screen region in pure stealth."""
        if not Config.is_configured():
            self._show_settings()
            return

        self._pending_append_snippet = False
        if self.append_overlay.isVisible():
            stealth_hide(self.append_overlay)

        self.snippet_overlay.start_selection(
            hint="✂️ Drag to capture region  •  Space: Full Screen  •  Esc: Cancel"
        )

    def _on_snippet_selected(self, bbox: Optional[tuple]):
        """Called when user selects a bounding box in SnippetOverlay, or presses Space for full screen."""
        try:
            is_append = self._pending_append_snippet
            self._pending_append_snippet = False

            img_bytes, pil_img, _ = capture_screen(bbox=bbox)
            self.hud.start_analysis(img_bytes, pil_img, append=is_append)
        except Exception as e:
            QMessageBox.critical(None, "Snippet Error", f"Failed to capture snippet area:\n{str(e)}")

    def _on_snippet_cancelled(self):
        """Called when user cancels SnippetOverlay with Escape or Right Click."""
        is_append = self._pending_append_snippet
        self._pending_append_snippet = False
        # If user was appending and cancelled, restore the existing HUD results
        if is_append and self.hud.captured_images:
            stealth_show(self.hud)

    def quit(self):
        self.hotkey_listener.stop()
        self.qapp.quit()


def main():
    # Set Windows App ID for high DPI and proper taskbar icon grouping
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("google.peekai.copilot.1")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("PeekAI")
    app.setApplicationDisplayName("PeekAI")
    app.setQuitOnLastWindowClosed(False)  # Keep running in system tray

    # Set crisp base font for Windows high DPI
    app.setFont(QFont("Segoe UI", 10))

    # Set Window and Taskbar Icon
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Single Instance Detection via local IPC pipe
    IPC_SERVER_NAME = "google.peekai.copilot.instance.pipe.v1"
    sock = QLocalSocket()
    sock.connectToServer(IPC_SERVER_NAME)
    if sock.waitForConnected(400):
        # An instance is already running! Wake it up and bring to front
        sock.write(b"SHOW\n")
        sock.flush()
        sock.waitForBytesWritten(1000)
        sock.disconnectFromServer()
        sys.exit(0)

    # First instance: start local server to listen for future wake-up requests
    ipc_server = QLocalServer()
    QLocalServer.removeServer(IPC_SERVER_NAME)
    ipc_server.listen(IPC_SERVER_NAME)

    peek_app = PeekAIApp(app)

    def _handle_ipc_wakeup():
        client = ipc_server.nextPendingConnection()
        if client:
            if client.waitForReadyRead(300):
                cmd = bytes(client.readAll()).decode("utf-8", errors="ignore").strip()
                if cmd == "SHOW":
                    peek_app.show_and_activate()
            client.close()

    ipc_server.newConnection.connect(_handle_ipc_wakeup)

    peek_app.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
