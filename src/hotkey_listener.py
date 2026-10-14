"""Global hotkey listener using Windows native state and normalized key tracking."""
import sys
import time
import logging
import ctypes
from typing import Optional, Set
from PyQt6.QtCore import QObject, pyqtSignal
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

logger = logging.getLogger("PeekAI.HotkeyListener")


class HotkeyListener(QObject):
    """
    Listens for global shortcuts in background thread and emits Qt signals.
    Combines pynput hooks with Windows GetAsyncKeyState for 100% reliable modifier detection.
    """

    full_peek_triggered = pyqtSignal()
    snippet_peek_triggered = pyqtSignal()
    append_peek_triggered = pyqtSignal()
    copy_peek_triggered = pyqtSignal()
    settings_triggered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._listener: Optional[keyboard.Listener] = None
        self._current_keys: Set[str] = set()
        self._last_trigger_time: float = 0
        self._debounce_seconds: float = 0.4

    def _is_ctrl_down(self) -> bool:
        if "ctrl" in self._current_keys:
            return True
        if sys.platform == "win32":
            try:
                u32 = ctypes.windll.user32
                # VK_CONTROL (0x11), VK_LCONTROL (0xA2), VK_RCONTROL (0xA3)
                if (u32.GetAsyncKeyState(0x11) | u32.GetAsyncKeyState(0xA2) | u32.GetAsyncKeyState(0xA3)) & 0x8000:
                    return True
            except Exception:
                pass
        return False

    def _is_shift_down(self) -> bool:
        if "shift" in self._current_keys:
            return True
        if sys.platform == "win32":
            try:
                u32 = ctypes.windll.user32
                # VK_SHIFT (0x10), VK_LSHIFT (0xA0), VK_RSHIFT (0xA1)
                if (u32.GetAsyncKeyState(0x10) | u32.GetAsyncKeyState(0xA0) | u32.GetAsyncKeyState(0xA1)) & 0x8000:
                    return True
            except Exception:
                pass
        return False

    def _is_alt_down(self) -> bool:
        if "alt" in self._current_keys:
            return True
        if sys.platform == "win32":
            try:
                u32 = ctypes.windll.user32
                # VK_MENU (0x12), VK_LMENU (0xA4), VK_RMENU (0xA5)
                if (u32.GetAsyncKeyState(0x12) | u32.GetAsyncKeyState(0xA4) | u32.GetAsyncKeyState(0xA5)) & 0x8000:
                    return True
            except Exception:
                pass
        return False

    def _is_key_c(self, key) -> bool:
        vk = getattr(key, "vk", None)
        if vk in (67, 0x43):
            return True
        char = getattr(key, "char", None)
        if char and char in ("c", "C", "\x03"):
            return True
        return False

    def _is_key_a(self, key) -> bool:
        vk = getattr(key, "vk", None)
        if vk in (65, 0x41):
            return True
        char = getattr(key, "char", None)
        if char and char in ("a", "A", "\x01"):
            return True
        return False

    def _is_key_x(self, key) -> bool:
        vk = getattr(key, "vk", None)
        if vk in (88, 0x58):
            return True
        char = getattr(key, "char", None)
        if char and char in ("x", "X", "\x18"):
            return True
        return False

    def _is_key_s(self, key) -> bool:
        vk = getattr(key, "vk", None)
        if vk in (83, 0x53):
            return True
        char = getattr(key, "char", None)
        if char and char in ("s", "S", "\x13"):
            return True
        return False

    def _is_key_space(self, key) -> bool:
        if key == Key.space:
            return True
        vk = getattr(key, "vk", None)
        if vk == 32:
            return True
        char = getattr(key, "char", None)
        if char == " ":
            return True
        return False

    def _normalize(self, key) -> Optional[str]:
        if key in (Key.ctrl, Key.ctrl_l, Key.ctrl_r):
            return "ctrl"
        if key in (Key.shift, Key.shift_l, Key.shift_r):
            return "shift"
        if key in (Key.alt, Key.alt_l, Key.alt_r):
            return "alt"
        if self._is_key_space(key):
            return "space"
        if self._is_key_x(key):
            return "x"
        if self._is_key_a(key):
            return "a"
        if self._is_key_c(key):
            return "c"
        if self._is_key_s(key):
            return "s"

        vk = getattr(key, "vk", None)
        if vk in (17, 162, 163):
            return "ctrl"
        if vk in (16, 160, 161):
            return "shift"
        if vk in (18, 164, 165):
            return "alt"

        char = getattr(key, "char", None)
        if char:
            return char.lower()
        return None

    def _on_press(self, key):
        norm = self._normalize(key)
        if norm:
            self._current_keys.add(norm)

        now = time.time()
        if now - self._last_trigger_time < self._debounce_seconds:
            return

        ctrl = self._is_ctrl_down()
        shift = self._is_shift_down()
        alt = self._is_alt_down()

        # 0. Check Stealth Copy (Ctrl + Alt + C or Ctrl + Shift + C)
        if ((ctrl and alt and self._is_key_c(key)) or
            {"ctrl", "alt", "c"}.issubset(self._current_keys) or
            (ctrl and shift and self._is_key_c(key)) or
            {"ctrl", "shift", "c"}.issubset(self._current_keys)):
            self._last_trigger_time = now
            logger.info("HotKey Triggered: Stealth Copy Clean Answer (Ctrl+Alt+C / Ctrl+Shift+C)")
            self.copy_peek_triggered.emit()
            return

        # 1. Check Append Peek (Ctrl + Shift + A or a)
        if (ctrl and shift and self._is_key_a(key)) or {"ctrl", "shift", "a"}.issubset(self._current_keys):
            self._last_trigger_time = now
            logger.info("HotKey Triggered: Append Scrolled Screen (Ctrl+Shift+A)")
            self.append_peek_triggered.emit()
            return

        # 2. Check Snippet Peek (Ctrl + Shift + X)
        if (ctrl and shift and self._is_key_x(key)) or {"ctrl", "shift", "x"}.issubset(self._current_keys):
            self._last_trigger_time = now
            logger.info("HotKey Triggered: Snippet Region Peek (Ctrl+Shift+X)")
            self.snippet_peek_triggered.emit()
            return

        # 3. Check Full Screen Peek (Ctrl + Shift + Space)
        if (ctrl and shift and self._is_key_space(key)) or {"ctrl", "shift", "space"}.issubset(self._current_keys):
            self._last_trigger_time = now
            logger.info("HotKey Triggered: Full Screen Peek (Ctrl+Shift+Space)")
            self.full_peek_triggered.emit()
            return

        # 4. Check Settings Dialog (Ctrl + Shift + S)
        if (ctrl and shift and self._is_key_s(key)) or {"ctrl", "shift", "s"}.issubset(self._current_keys):
            self._last_trigger_time = now
            logger.info("HotKey Triggered: Settings Dialog (Ctrl+Shift+S)")
            self.settings_triggered.emit()
            return

    def _on_release(self, key):
        norm = self._normalize(key)
        if norm and norm in self._current_keys:
            self._current_keys.discard(norm)

        # Resynchronize modifiers if physically released
        if "ctrl" in self._current_keys and not self._is_ctrl_down():
            self._current_keys.discard("ctrl")
        if "shift" in self._current_keys and not self._is_shift_down():
            self._current_keys.discard("shift")
        if "alt" in self._current_keys and not self._is_alt_down():
            self._current_keys.discard("alt")

    def _win32_event_filter(self, msg, data):
        """
        Low-level Windows keyboard filter.
        When PeekAI hotkeys are detected, triggers the action and SUPPRESSES the keystroke
        from reaching the active browser / exam window (returns False).
        This prevents browser shortcuts (e.g. Chrome Ctrl+Shift+A Tab Search, Edge Ctrl+Shift+S)
        and exam anti-cheating scripts from detecting hotkey activity!
        """
        VK_SPACE = 0x20
        VK_X = 0x58
        VK_A = 0x41
        VK_C = 0x43
        VK_S = 0x53

        vk = getattr(data, "vkCode", None)
        if vk not in (VK_SPACE, VK_X, VK_A, VK_C, VK_S):
            return True

        ctrl = self._is_ctrl_down()
        shift = self._is_shift_down()
        alt = self._is_alt_down()

        if not ctrl:
            return True

        WM_KEYDOWN = 0x0100
        WM_KEYUP = 0x0101
        WM_SYSKEYDOWN = 0x0104
        WM_SYSKEYUP = 0x0105

        is_down = (msg in (WM_KEYDOWN, WM_SYSKEYDOWN))

        matched = False
        signal_to_emit = None

        if (ctrl and alt and vk == VK_C) or (ctrl and shift and vk == VK_C):
            matched = True
            signal_to_emit = self.copy_peek_triggered
        elif ctrl and shift and vk == VK_A:
            matched = True
            signal_to_emit = self.append_peek_triggered
        elif ctrl and shift and vk == VK_X:
            matched = True
            signal_to_emit = self.snippet_peek_triggered
        elif ctrl and shift and vk == VK_SPACE:
            matched = True
            signal_to_emit = self.full_peek_triggered
        elif ctrl and shift and vk == VK_S:
            matched = True
            signal_to_emit = self.settings_triggered

        if matched:
            if is_down:
                now = time.time()
                if now - self._last_trigger_time >= self._debounce_seconds:
                    self._last_trigger_time = now
                    logger.info("Win32 Filter Hotkey Triggered & Suppressed: vk=0x%02X", vk)
                    if signal_to_emit:
                        signal_to_emit.emit()
            # Suppress key from reaching Chrome / Edge / exam portal!
            return False

        return True

    def start(self):
        """Starts the global key listener with Windows native key suppression."""
        self.stop()
        self._current_keys.clear()
        try:
            kwargs = {
                "on_press": self._on_press,
                "on_release": self._on_release,
            }
            if sys.platform == "win32":
                kwargs["win32_event_filter"] = self._win32_event_filter

            self._listener = keyboard.Listener(**kwargs)
            self._listener.daemon = True
            self._listener.start()
            logger.info("Global hotkey listener started successfully (Win32 key suppression active).")
        except Exception as e:
            logger.error("Failed to start hotkey listener: %s", e)

    def stop(self):
        """Stops the active keyboard listener."""
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None
        self._current_keys.clear()
