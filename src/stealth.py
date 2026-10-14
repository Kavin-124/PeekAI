"""
Stealth window management and OS-level focus protection for PeekAI.
Ensures zero focus loss, zero window activation, and complete invisibility
to anti-cheating and proctoring systems (NeoPAT, Mettl, HackerEarth, Mercer, etc.).
"""
import sys
import ctypes
import logging
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

logger = logging.getLogger("PeekAI.Stealth")

# Win32 Constants
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008

SW_SHOWNOACTIVATE = 4
SW_HIDE = 0

HWND_TOPMOST = -1

SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020
SWP_SHOWWINDOW = 0x0040
SWP_HIDEWINDOW = 0x0080

WDA_NONE = 0x00000000
WDA_EXCLUDEFROMCAPTURE = 0x00000011


def apply_stealth_flags(widget: QWidget):
    """
    Applies Qt flags and Windows native extended styles to guarantee:
    1. Window DOES NOT accept focus (WindowDoesNotAcceptFocus).
    2. Window NEVER activates when shown or clicked (WS_EX_NOACTIVATE).
    3. Window is excluded from desktop screen grabs & screen sharing (WDA_EXCLUDEFROMCAPTURE).
    """
    # 1. Qt Window Flags & Attributes
    widget.setWindowFlags(
        Qt.WindowType.FramelessWindowHint
        | Qt.WindowType.WindowStaysOnTopHint
        | Qt.WindowType.Tool
        | Qt.WindowType.WindowDoesNotAcceptFocus
    )
    widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    widget.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
    widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    # 2. Windows Native Extended Styles
    if sys.platform == "win32":
        try:
            user32 = ctypes.windll.user32
            hwnd = int(widget.winId())

            # 64-bit safe Get/SetWindowLong
            if hasattr(user32, "GetWindowLongPtrW"):
                get_long = user32.GetWindowLongPtrW
                set_long = user32.SetWindowLongPtrW
            else:
                get_long = user32.GetWindowLongW
                set_long = user32.SetWindowLongW

            current_style = get_long(hwnd, GWL_EXSTYLE)
            new_style = current_style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TOPMOST
            set_long(hwnd, GWL_EXSTYLE, new_style)

            # SWP_FRAMECHANGED commits the style change to the window frame immediately
            user32.SetWindowPos(
                hwnd,
                0,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED
            )

            # Hardware-exclude window from all screen captures and proctor screen-shares
            if hasattr(user32, "SetWindowDisplayAffinity"):
                user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)

        except Exception as e:
            logger.warning(f"Could not apply Windows stealth flags: {e}")


def stealth_show(widget: QWidget):
    """
    Shows widget on top in pure stealth mode without stealing focus or activating.
    If the active foreground window somehow flickers, immediately restores focus
    to the underlying exam/browser window.
    """
    if sys.platform == "win32":
        try:
            user32 = ctypes.windll.user32
            # Record current active foreground window (e.g. Chrome / exam window)
            fg_hwnd = user32.GetForegroundWindow()

            apply_stealth_flags(widget)
            widget.setVisible(True)

            hwnd = int(widget.winId())
            # Show without activating, and set topmost without activating!
            user32.ShowWindow(hwnd, SW_SHOWNOACTIVATE)
            user32.SetWindowPos(
                hwnd,
                HWND_TOPMOST,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
            )

            # Extra guarantee: If foreground changed, force it back to the exam window!
            if fg_hwnd and user32.GetForegroundWindow() != fg_hwnd and fg_hwnd != hwnd:
                user32.SetForegroundWindow(fg_hwnd)
            return
        except Exception as e:
            logger.warning(f"Error in stealth_show: {e}")

    # Fallback for non-Windows
    widget.setVisible(True)


def stealth_hide(widget: QWidget):
    """Hides widget cleanly without triggering OS focus redistribution."""
    if sys.platform == "win32":
        try:
            user32 = ctypes.windll.user32
            hwnd = int(widget.winId())
            user32.ShowWindow(hwnd, SW_HIDE)
            widget.setVisible(False)
            return
        except Exception:
            pass
    widget.hide()
