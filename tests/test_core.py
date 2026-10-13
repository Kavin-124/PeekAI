"""Verification tests for PeekAI modules."""
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import Config
from src.capture import capture_screen
from src.ai_service import AIService


def test_config():
    print("Testing Config...")
    assert Config.DEFAULT_MODEL == "gemini-3.5-flash-lite"
    assert Config.get_hotkey_full() == "<ctrl>+<shift>+<space>"
    assert Config.get_hotkey_append() == "<ctrl>+<shift>+a"
    print("[OK] Config OK")


def test_capture():
    print("Testing Screen Capture...")
    img_bytes, pil_img, b64_str = capture_screen()
    assert len(img_bytes) > 0, "Image bytes should not be empty"
    assert pil_img.width > 0 and pil_img.height > 0, "Image dimension should be valid"
    assert len(b64_str) > 0, "Base64 string should not be empty"
    print(f"[OK] Capture OK (Captured resolution: {pil_img.width}x{pil_img.height}, PNG size: {len(img_bytes)} bytes)")


def test_capture_bbox():
    print("Testing Bounding Box Capture...")
    bbox = (50, 50, 200, 150)
    img_bytes, pil_img, _ = capture_screen(bbox=bbox)
    assert len(img_bytes) > 0
    assert pil_img.width >= 200 and pil_img.height >= 150
    print(f"[OK] Bounding Box Capture OK (Captured resolution: {pil_img.width}x{pil_img.height})")


def test_ai_service_init():
    print("Testing AI Service initialization...")
    ai = AIService()
    assert ai is not None
    print("[OK] AI Service OK")


if __name__ == "__main__":
    print("=== Running PeekAI Verification Tests ===")
    test_config()
    test_capture()
    test_capture_bbox()
    test_ai_service_init()
    print("=== All Tests Passed Successfully! ===")
