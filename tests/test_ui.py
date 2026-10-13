"""Verification test for PeekAI UI components."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication
from src.ai_service import AIService
from src.ui.floating_hud import FloatingHUD, extract_clean_answer
from src.ui.snippet_overlay import SnippetOverlay
from src.ui.append_overlay import AppendOverlay
from src.ui.tray_icon import TrayIcon
from src.ui.settings_dialog import SettingsDialog


def test_ui_components():
    print("Testing UI Components...")
    app = QApplication.instance() or QApplication([])

    ai_service = AIService()
    hud = FloatingHUD(ai_service)
    assert hud is not None

    snippet = SnippetOverlay()
    assert snippet is not None

    append_bar = AppendOverlay()
    assert append_bar is not None

    tray = TrayIcon()
    assert tray is not None

    settings = SettingsDialog()
    assert settings is not None

    print("[OK] All UI Components Instantiated Successfully")


def test_clean_answer_extraction():
    print("Testing Clean Answer Extraction...")
    # 1. Code solution (user screenshot case)
    sample_code_response = """📸 **Attached Scrolled Snapshot #2**
*Synthesizing all sections to analyze complete problem & constraints...*

Optimal Solution (Python 3)
```python
class Solution:
    def minInsertions(self, s: str) -> int:
        return 0
```

Complexity Analysis
• Time Complexity: $O(N)$
"""
    clean_code = extract_clean_answer(sample_code_response)
    assert "class Solution:" in clean_code
    assert "📸" not in clean_code
    assert "Complexity Analysis" not in clean_code
    assert clean_code.startswith("class Solution:")
    assert clean_code.endswith("return 0")
    print("[OK] Pure code successfully extracted without metadata or complexity!")

    # 2. MCQ option extraction (Old format)
    sample_mcq = """📸 Attached Snapshot #1
**Correct Option:** B) O(log n)

Explanation:
Binary search splits in half.
"""
    clean_mcq = extract_clean_answer(sample_mcq)
    assert clean_mcq == "B) O(log n)"

    # 3. Competition-grade MCQ format with emoji and decisive proof
    sample_mcq_proof = """🎯 **Correct Option: B — In-place Sorting**

**💡 Decisive Proof:**
• Merge Sort requires O(n) auxiliary memory.
• In-place sorting requires O(1) auxiliary space.
"""
    clean_mcq_proof = extract_clean_answer(sample_mcq_proof)
    assert clean_mcq_proof == "B — In-place Sorting", f"Expected 'B — In-place Sorting', got {clean_mcq_proof!r}"
    print("[OK] Pure MCQ options and Decisive Proof parsed cleanly!")


def test_hud_copy():
    print("Testing HUD Copy Action...")
    app = QApplication.instance() or QApplication([])
    ai_service = AIService()
    hud = FloatingHUD(ai_service)

    # Test code block copy
    hud.full_response_text = "Header\n```python\nprint('hello')\n```\nFooter"
    hud._copy_answer()
    clipboard_text = QApplication.clipboard().text()
    assert clipboard_text == "print('hello')"
    print(f"[OK] Clipboard text is pure code: {clipboard_text!r}")

    # Test MCQ answer copy
    hud.full_response_text = "🎯 **Correct Option: C — 12**\n\n**💡 Decisive Proof:**\n• x evaluates to 12"
    hud._copy_answer()
    clipboard_text = QApplication.clipboard().text()
    assert clipboard_text == "C — 12", f"Expected 'C — 12', got {clipboard_text!r}"
    print(f"[OK] Clipboard text is pure MCQ option: {clipboard_text!r}")


if __name__ == "__main__":
    test_ui_components()
    test_clean_answer_extraction()
    test_hud_copy()
    print("=== All UI & Copy Tests Passed! ===")
