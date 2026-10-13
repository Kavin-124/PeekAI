"""Stealth Anti-Proctoring Focus-Loss Prevention Verification Tests."""
import sys
import os
import ctypes

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.ai_service import AIService
from src.ui.floating_hud import FloatingHUD
from src.ui.append_overlay import AppendOverlay
from src.ui.snippet_overlay import SnippetOverlay
from src.config import Config


def test_stealth_hud():
    print("Testing FloatingHUD Stealth Flags & Focus Immunity...")
    app = QApplication.instance() or QApplication([])
    ai = AIService()
    hud = FloatingHUD(ai)

    # 1. Verify Qt WindowDoesNotAcceptFocus flag
    flags = hud.windowFlags()
    assert bool(flags & Qt.WindowType.WindowDoesNotAcceptFocus), "HUD must have WindowDoesNotAcceptFocus flag!"

    # 2. Verify Windows native WS_EX_NOACTIVATE style
    if sys.platform == "win32":
        hwnd = int(hud.winId())
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        assert bool(style & WS_EX_NOACTIVATE), "HUD must have WS_EX_NOACTIVATE set in Windows extended styles!"

        # 3. Test Show does not steal foreground focus
        hud.show()
        foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
        assert foreground_hwnd != hwnd, f"HUD (HWND {hwnd}) stole foreground focus! Active HWND: {foreground_hwnd}"
        hud.hide()

    print("[OK] FloatingHUD is 100% immune to window focus stealing!")


def test_stealth_append_overlay():
    print("Testing AppendOverlay Stealth Flags...")
    app = QApplication.instance() or QApplication([])
    append_bar = AppendOverlay()

    flags = append_bar.windowFlags()
    assert bool(flags & Qt.WindowType.WindowDoesNotAcceptFocus), "AppendOverlay must have WindowDoesNotAcceptFocus!"

    if sys.platform == "win32":
        hwnd = int(append_bar.winId())
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        assert bool(style & WS_EX_NOACTIVATE), "AppendOverlay must have WS_EX_NOACTIVATE set!"

    print("[OK] AppendOverlay is 100% stealth!")


def test_stealth_copy_hotkey_config():
    print("Testing Stealth Copy Hotkey Config...")
    assert Config.DEFAULT_HOTKEY_COPY == "<ctrl>+<alt>+c"
    assert Config.get_hotkey_copy() == "<ctrl>+<alt>+c"
    print("[OK] Stealth Copy hotkey configuration verified!")


if __name__ == "__main__":
    test_stealth_hud()
    test_stealth_append_overlay()
    test_stealth_copy_hotkey_config()
    print("=== All Stealth Anti-Proctoring Tests Passed! ===")
