"""Test suite to verify PeekAI Light and Dark Theme support."""
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication

from src.config import Config
from src.ai_service import AIService
from src.ui.floating_hud import FloatingHUD
from src.ui.append_overlay import AppendOverlay
from src.ui.settings_dialog import SettingsDialog


def test_theme_system():
    print("Testing Theme System...")
    app = QApplication.instance() or QApplication(sys.argv)

    # 1. Config theme get & set
    initial_theme = Config.get_theme()
    print(f"[+] Initial theme: {initial_theme}")

    Config.set_theme("dark")
    assert Config.get_theme() == "dark", "Failed to set dark theme"
    print("[OK] Set dark theme successful")

    Config.set_theme("light")
    assert Config.get_theme() == "light", "Failed to set light theme"
    print("[OK] Set light theme successful")

    # 2. FloatingHUD theme switching
    ai_service = AIService()
    hud = FloatingHUD(ai_service)
    
    # Test Light mode
    Config.set_theme("light")
    hud._apply_styles()
    hud._clear_content()
    assert "⚡ PeekAI is Ready" in hud.text_viewer.toHtml()
    assert "#ffffff" in hud.styleSheet() or "background-color: #ffffff" in hud.styleSheet()
    print("[OK] FloatingHUD Light theme applied cleanly")

    # Test Dark mode
    Config.set_theme("dark")
    hud._apply_styles()
    hud._clear_content()
    assert "⚡ PeekAI is Ready" in hud.text_viewer.toHtml()
    assert "#16161a" in hud.styleSheet()
    print("[OK] FloatingHUD Dark theme applied cleanly")

    # 3. AppendOverlay theme switching
    overlay = AppendOverlay()
    Config.set_theme("light")
    overlay._apply_styles()
    assert "#ffffff" in overlay.styleSheet()
    print("[OK] AppendOverlay Light theme applied cleanly")

    Config.set_theme("dark")
    overlay._apply_styles()
    assert "#16161a" in overlay.styleSheet()
    print("[OK] AppendOverlay Dark theme applied cleanly")

    # 4. SettingsDialog theme switching
    dialog = SettingsDialog()
    Config.set_theme("light")
    dialog._load_current_values()
    assert dialog.theme_combo.currentIndex() == 0
    print("[OK] SettingsDialog loads Light theme by default")

    dialog.theme_combo.setCurrentIndex(1)
    # trigger theme change
    dialog._on_theme_changed()
    assert "#141417" in dialog.styleSheet()
    print("[OK] SettingsDialog live switches to Dark theme")

    dialog.theme_combo.setCurrentIndex(0)
    dialog._on_theme_changed()
    assert "#ffffff" in dialog.styleSheet()
    print("[OK] SettingsDialog live switches to Light theme")

    # Restore default light theme
    Config.set_theme("light")
    print("=== All Theme Tests Passed 100% Successfully! ===")


if __name__ == "__main__":
    test_theme_system()
