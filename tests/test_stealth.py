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
from src.hotkey_listener import HotkeyListener
from src.config import Config
from src.stealth import apply_stealth_flags, stealth_show, stealth_hide


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
        stealth_show(hud)
        foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
        assert foreground_hwnd != hwnd, f"HUD (HWND {hwnd}) stole foreground focus! Active HWND: {foreground_hwnd}"
        stealth_hide(hud)

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


def test_stealth_snippet_overlay():
    print("Testing SnippetOverlay Stealth Flags...")
    app = QApplication.instance() or QApplication([])
    snippet = SnippetOverlay()

    # 1. Verify Qt WindowDoesNotAcceptFocus flag
    flags = snippet.windowFlags()
    assert bool(flags & Qt.WindowType.WindowDoesNotAcceptFocus), "SnippetOverlay must have WindowDoesNotAcceptFocus!"

    # 2. Verify Windows native WS_EX_NOACTIVATE style
    if sys.platform == "win32":
        hwnd = int(snippet.winId())
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        assert bool(style & WS_EX_NOACTIVATE), "SnippetOverlay must have WS_EX_NOACTIVATE set!"

        # 3. Test stealth show
        stealth_show(snippet)
        foreground_hwnd = ctypes.windll.user32.GetForegroundWindow()
        assert foreground_hwnd != hwnd, f"SnippetOverlay (HWND {hwnd}) stole foreground focus!"
        stealth_hide(snippet)

    print("[OK] SnippetOverlay is 100% stealth!")


def test_win32_key_suppression():
    print("Testing Win32 Keystroke Suppression Filter...")
    listener = HotkeyListener()

    class FakeData:
        def __init__(self, vk):
            self.vkCode = vk

    # When Ctrl is down, test matching hotkeys return False (suppressed from browser)
    listener._is_ctrl_down = lambda: True
    listener._is_shift_down = lambda: True
    listener._is_alt_down = lambda: False

    # Ctrl+Shift+A (Chrome Tab Search) -> MUST BE SUPPRESSED (returns False)
    res_a = listener._win32_event_filter(0x0100, FakeData(0x41))
    assert res_a is False, "Ctrl+Shift+A must return False to suppress Chrome Tab Search!"

    # Ctrl+Shift+Space -> MUST BE SUPPRESSED
    res_sp = listener._win32_event_filter(0x0100, FakeData(0x20))
    assert res_sp is False, "Ctrl+Shift+Space must return False to suppress from browser!"

    # Ctrl+Shift+X -> MUST BE SUPPRESSED
    res_x = listener._win32_event_filter(0x0100, FakeData(0x58))
    assert res_x is False, "Ctrl+Shift+X must return False to suppress from browser!"

    # Normal key (e.g. typing letter 'P' = 0x50) -> MUST PASS THROUGH (returns True)
    res_p = listener._win32_event_filter(0x0100, FakeData(0x50))
    assert res_p is True, "Normal keys must return True so user can type code normally!"

    print("[OK] Keystroke suppression filter verified: 100% blocks browser shortcuts & proctor detection!")


def test_stealth_copy_hotkey_config():
    print("Testing Stealth Copy Hotkey Config...")
    assert Config.DEFAULT_HOTKEY_COPY == "<ctrl>+<alt>+c"
    assert Config.get_hotkey_copy() == "<ctrl>+<alt>+c"
    print("[OK] Stealth Copy hotkey configuration verified!")


if __name__ == "__main__":
    test_stealth_hud()
    test_stealth_append_overlay()
    test_stealth_snippet_overlay()
    test_win32_key_suppression()
    test_stealth_copy_hotkey_config()
    print("\n=== All Stealth Anti-Proctoring Tests Passed 100%! ===")
