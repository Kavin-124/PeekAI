import os
import sys
import re
from typing import Optional, Union, List
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QImage, QClipboard, QFont, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser,
    QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect,
    QApplication, QSizePolicy, QMenu
)
from src.ai_service import AIService
from src.config import Config
from src.stealth import apply_stealth_flags, stealth_show, stealth_hide


def extract_clean_answer(raw: str) -> str:
    """
    Extracts only the pure answer or code from the AI response.
    Eliminates snapshot headers, Markdown wrappers, commentary, and metadata.
    """
    if not raw:
        return ""

    # Strip snapshot headers like "📸 Attached Scrolled Snapshot #..."
    cleaned = re.sub(r'(?:---\s*)?📸[^\n]*\n?', '', raw, flags=re.IGNORECASE)
    cleaned = re.sub(r'\*Synthesizing all sections[^\n]*\*\n?', '', cleaned, flags=re.IGNORECASE).strip()

    # 1. Code block extraction (matches ```python, ```python 3, ```, with \n or \r\n, closed or unclosed)
    code_blocks = re.findall(r'```[^\r\n]*[\r\n]+(.*?)(?:```|\Z)', cleaned, re.DOTALL)
    if code_blocks:
        valid_blocks = [b.strip() for b in code_blocks if b.strip()]
        if valid_blocks:
            # Pick the largest or latest substantial code block
            largest_code = max(valid_blocks, key=len)
            last_code = valid_blocks[-1]
            if len(largest_code) > len(last_code) * 2:
                return largest_code
            return last_code

    # 2. Check for explicit MCQ / Direct Answer lines
    # E.g. "🎯 **Correct Option: B — In-place Sorting**", "**Correct Option:** B) ...", "**Answer:** C", "**Output:** 42"
    mcq_match = re.search(
        r'(?:🎯\s*)?[\*\#\_\s]*(?:Correct\s+(?:Option|Answer)|Answer|Option|Output)[\*\#\_\s]*[:\-–—]?\s*([^\r\n]+)',
        cleaned,
        re.IGNORECASE
    )
    if mcq_match:
        ans = mcq_match.group(1).strip()
        # Clean leading/trailing markdown decorators (*, _, `, #)
        ans = re.sub(r'^[\*\_`#]+', '', ans)
        ans = re.sub(r'[\*\_`#]+$', '', ans).strip()
        # Ensure it is a concise answer rather than an entire paragraph
        if ans and len(ans) <= 200:
            return ans

    # 3. Strip explanation, proof, and complexity sections if present
    lines = cleaned.splitlines()
    filtered = []
    stop_headings = (
        "complexity analysis", "complexity:", "explanation:", "approach:", "time complexity:",
        "space complexity:", "how it works:", "step-by-step:", "decisive proof", "💡 decisive proof",
        "proof:", "why ", "trap explanation"
    )
    for line in lines:
        lower = line.strip().lower()
        plain_line = re.sub(r'^[^\w]+', '', lower)
        if any(plain_line.startswith(h) or lower.startswith(h) for h in stop_headings) and filtered:
            break
        filtered.append(line)

    result = "\n".join(filtered).strip()
    return result if result else cleaned


class StreamWorker(QThread):
    """Background worker to stream Gemini AI responses without blocking Qt main loop."""

    chunk_received = pyqtSignal(str)
    stream_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, ai_service: AIService, image_bytes: Optional[Union[bytes, List[bytes]]] = None, followup_text: Optional[str] = None):
        super().__init__()
        self.ai_service = ai_service
        self.image_bytes = image_bytes
        self.followup_text = followup_text

    def run(self):
        try:
            if self.followup_text:
                for chunk in self.ai_service.send_followup_stream(self.followup_text):
                    self.chunk_received.emit(chunk)
            elif self.image_bytes:
                for chunk in self.ai_service.analyze_screen_stream(self.image_bytes):
                    self.chunk_received.emit(chunk)
            self.stream_finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))





class FloatingHUD(QWidget):
    """Glassmorphic floating HUD overlay for instant AI screen answers."""

    request_repeek = pyqtSignal()
    request_append = pyqtSignal()
    request_settings = pyqtSignal()

    def __init__(self, ai_service: AIService):
        super().__init__()
        self.ai_service = ai_service
        self.worker: Optional[StreamWorker] = None
        self.full_response_text = ""
        self.drag_position: Optional[QPoint] = None
        self.captured_images: List[bytes] = []
        self.captured_pils = []

        self._init_window_flags()
        self._init_ui()
        self._apply_styles()

    LIGHT_READY_HTML = """
    <div style="text-align: center; padding: 24px 12px; font-family: 'Segoe UI', system-ui, sans-serif;">
        <h3 style="color: #4f46e5; margin-bottom: 6px; font-size: 16px;">⚡ PeekAI is Ready</h3>
        <p style="color: #64748b; font-size: 12px; margin-bottom: 16px;">
            Screen Copilot is listening. Browser focus is 100% protected:
        </p>
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin: 0 auto; text-align: left;">
            <p style="margin: 6px 0; color: #0f172a; font-size: 12px;">
                <span style="background: #ffffff; border: 1px solid #cbd5e1; padding: 2px 7px; border-radius: 4px; font-family: monospace; color: #2563eb;">Ctrl + Shift + Space</span>
                <span style="color: #475569; margin-left: 8px;">Full Screen Snapshot</span>
            </p>
            <p style="margin: 6px 0; color: #0f172a; font-size: 12px;">
                <span style="background: #ffffff; border: 1px solid #cbd5e1; padding: 2px 7px; border-radius: 4px; font-family: monospace; color: #059669;">Ctrl + Shift + X</span>
                <span style="color: #475569; margin-left: 8px;">Crop Region Snapshot</span>
            </p>
            <p style="margin: 6px 0; color: #0f172a; font-size: 12px;">
                <span style="background: #ffffff; border: 1px solid #cbd5e1; padding: 2px 7px; border-radius: 4px; font-family: monospace; color: #7c3aed;">Ctrl + Shift + A</span>
                <span style="color: #475569; margin-left: 8px;"><b>Snap &amp; Append</b> Scrolled Part</span>
            </p>
            <p style="margin: 6px 0; color: #0f172a; font-size: 12px;">
                <span style="background: #ffffff; border: 1px solid #cbd5e1; padding: 2px 7px; border-radius: 4px; font-family: monospace; color: #d97706;">Ctrl + Alt + C</span>
                <span style="color: #475569; margin-left: 8px;"><b>Stealth Copy</b> Answer / Code</span>
            </p>
            <p style="margin: 6px 0; color: #0f172a; font-size: 12px;">
                <span style="background: #ffffff; border: 1px solid #cbd5e1; padding: 2px 7px; border-radius: 4px; font-family: monospace; color: #0284c7;">Ctrl + Shift + S</span>
                <span style="color: #475569; margin-left: 8px;"><b>Settings &amp; Theme</b> (Or click ⚙️)</span>
            </p>
        </div>
        <p style="color: #94a3b8; font-size: 11px; margin-top: 14px;">
            🔒 <i>Zero Focus Stealing: Exam windows will never detect tab-switching!</i>
        </p>
    </div>
    """

    DARK_READY_HTML = """
    <div style="text-align: center; padding: 24px 12px; font-family: 'Segoe UI', system-ui, sans-serif;">
        <h3 style="color: #818cf8; margin-bottom: 6px; font-size: 16px;">⚡ PeekAI is Ready</h3>
        <p style="color: #94a3b8; font-size: 12px; margin-bottom: 16px;">
            Screen Copilot is listening. Browser focus is 100% protected:
        </p>
        <div style="background-color: #1a1a22; border: 1px solid #2e2e3a; border-radius: 8px; padding: 12px 16px; margin: 0 auto; text-align: left;">
            <p style="margin: 6px 0; color: #f1f5f9; font-size: 12px;">
                <span style="background: #2e2e38; padding: 2px 7px; border-radius: 4px; font-family: monospace; color: #60a5fa;">Ctrl + Shift + Space</span>
                <span style="color: #cbd5e1; margin-left: 8px;">Full Screen Snapshot</span>
            </p>
            <p style="margin: 6px 0; color: #f1f5f9; font-size: 12px;">
                <span style="background: #2e2e38; padding: 2px 7px; border-radius: 4px; font-family: monospace; color: #34d399;">Ctrl + Shift + X</span>
                <span style="color: #cbd5e1; margin-left: 8px;">Crop Region Snapshot</span>
            </p>
            <p style="margin: 6px 0; color: #f1f5f9; font-size: 12px;">
                <span style="background: #2e2e38; padding: 2px 7px; border-radius: 4px; font-family: monospace; color: #c084fc;">Ctrl + Shift + A</span>
                <span style="color: #cbd5e1; margin-left: 8px;"><b>Snap &amp; Append</b> Scrolled Part</span>
            </p>
            <p style="margin: 6px 0; color: #f1f5f9; font-size: 12px;">
                <span style="background: #2e2e38; padding: 2px 7px; border-radius: 4px; font-family: monospace; color: #fbbf24;">Ctrl + Alt + C</span>
                <span style="color: #cbd5e1; margin-left: 8px;"><b>Stealth Copy</b> Answer / Code</span>
            </p>
            <p style="margin: 6px 0; color: #f1f5f9; font-size: 12px;">
                <span style="background: #2e2e38; padding: 2px 7px; border-radius: 4px; font-family: monospace; color: #38bdf8;">Ctrl + Shift + S</span>
                <span style="color: #cbd5e1; margin-left: 8px;"><b>Settings &amp; Theme</b> (Or click ⚙️)</span>
            </p>
        </div>
        <p style="color: #64748b; font-size: 11px; margin-top: 14px;">
            🔒 <i>Zero Focus Stealing: Exam windows will never detect tab-switching!</i>
        </p>
    </div>
    """

    READY_HTML = LIGHT_READY_HTML

    def _get_ready_html(self) -> str:
        return self.DARK_READY_HTML if Config.get_theme() == "dark" else self.LIGHT_READY_HTML

    def _init_window_flags(self):
        apply_stealth_flags(self)
        self.resize(520, 640)

        # Set taskbar / window icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Center in top-right area of screen
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = screen_geo.x() + max(20, screen_geo.width() - 560)
            y = screen_geo.y() + 60
            self.move(x, y)

    def showEvent(self, event):
        super().showEvent(event)
        apply_stealth_flags(self)


    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Container Card (for shadow and border)
        self.card = QFrame()
        self.card.setObjectName("cardFrame")
        
        # Shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(24)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(8)
        self.shadow.setColor(QColor(15, 23, 42, 45) if Config.get_theme() != "dark" else QColor(0, 0, 0, 180))
        self.card.setGraphicsEffect(self.shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(12)

        # 1. Header Bar (Draggable)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Logo / Title
        self.logo_label = QLabel("⚡ PeekAI")
        self.logo_label.setObjectName("titleLabel")
        header_layout.addWidget(self.logo_label)

        # Status Badge
        self.status_badge = QLabel("Ready")
        self.status_badge.setObjectName("statusBadge")
        header_layout.addWidget(self.status_badge)

        header_layout.addStretch()

        # Settings button
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setObjectName("iconBtn")
        self.settings_btn.setToolTip("Settings (Theme, Model, API Key)")
        self.settings_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.settings_btn.clicked.connect(self.request_settings.emit)
        header_layout.addWidget(self.settings_btn)

        # Minimize / Close buttons
        self.min_btn = QPushButton("─")
        self.min_btn.setObjectName("iconBtn")
        self.min_btn.setToolTip("Minimize (Esc)")
        self.min_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.min_btn.clicked.connect(self.hide)
        header_layout.addWidget(self.min_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setToolTip("Hide to Tray")
        self.close_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.close_btn.clicked.connect(self.hide)
        header_layout.addWidget(self.close_btn)

        card_layout.addLayout(header_layout)

        # 2. Thumbnail preview bar (collapsible)
        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("previewFrame")
        self.preview_frame.setVisible(False)
        preview_layout = QHBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(8, 4, 8, 4)
        
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(60, 36)
        self.thumb_label.setScaledContents(True)
        preview_layout.addWidget(self.thumb_label)

        self.preview_info = QLabel("Captured screen analyzed")
        self.preview_info.setStyleSheet("color: #a1a1aa; font-size: 11px;")
        preview_layout.addWidget(self.preview_info)
        preview_layout.addStretch()

        card_layout.addWidget(self.preview_frame)

        # 3. Main Markdown Output Viewer
        self.text_viewer = QTextBrowser()
        self.text_viewer.setOpenExternalLinks(True)
        self.text_viewer.setObjectName("textViewer")
        self.text_viewer.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        card_layout.addWidget(self.text_viewer)
        self.text_viewer.setHtml(self._get_ready_html())

        # 4. Action Bar (Copy, Re-peek, Clear)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        self.copy_btn = QPushButton("📋 Copy Answer")
        self.copy_btn.setObjectName("actionBtn")
        self.copy_btn.setToolTip("Click to copy clean answer/code (Right-click for full raw text)")
        self.copy_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.copy_btn.clicked.connect(self._copy_answer)
        self.copy_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.copy_btn.customContextMenuRequested.connect(self._show_copy_menu)
        action_layout.addWidget(self.copy_btn)

        self.repeek_btn = QPushButton("🔄 Re-Peek")
        self.repeek_btn.setObjectName("actionBtn")
        self.repeek_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.repeek_btn.clicked.connect(self.request_repeek.emit)
        action_layout.addWidget(self.repeek_btn)

        self.append_btn = QPushButton("➕ Snap & Append")
        self.append_btn.setObjectName("appendBtn")
        self.append_btn.setToolTip("Scroll down and click to capture & combine the scrolled part (Ctrl+Shift+A)")
        self.append_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.append_btn.clicked.connect(self.request_append.emit)
        action_layout.addWidget(self.append_btn)

        self.clear_btn = QPushButton("🧹 Clear")
        self.clear_btn.setObjectName("actionBtn")
        self.clear_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.clear_btn.clicked.connect(self._clear_content)
        action_layout.addWidget(self.clear_btn)

        action_layout.addStretch()
        card_layout.addLayout(action_layout)

        # 5. Interactive Follow-up Input
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.chat_input = QLineEdit()
        self.chat_input.setObjectName("chatInput")
        self.chat_input.setPlaceholderText("Ask follow-up... (Enter to send)")
        self.chat_input.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.chat_input.returnPressed.connect(self._send_followup)
        input_layout.addWidget(self.chat_input)

        self.send_btn = QPushButton("➤")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.setToolTip("Send follow-up")
        self.send_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.send_btn.clicked.connect(self._send_followup)
        input_layout.addWidget(self.send_btn)

        card_layout.addLayout(input_layout)

        main_layout.addWidget(self.card)

    def _apply_styles(self):
        if Config.get_theme() == "dark":
            self._apply_dark_styles()
        else:
            self._apply_light_styles()

    def _apply_light_styles(self):
        if hasattr(self, 'shadow'):
            self.shadow.setColor(QColor(15, 23, 42, 45))

        self.setStyleSheet("""
            #cardFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
            #titleLabel {
                color: #0f172a;
                font-size: 15px;
                font-weight: 700;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            #statusBadge {
                background-color: #f1f5f9;
                color: #475569;
                border: 1px solid #e2e8f0;
                font-size: 11px;
                padding: 3px 8px;
                border-radius: 10px;
                font-weight: 600;
            }
            #iconBtn {
                background-color: transparent;
                border: none;
                color: #64748b;
                font-size: 14px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 6px;
            }
            #iconBtn:hover {
                background-color: #f1f5f9;
                color: #4f46e5;
            }
            #closeBtn {
                background-color: transparent;
                border: none;
                color: #64748b;
                font-size: 14px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 6px;
            }
            #closeBtn:hover {
                background-color: #f1f5f9;
                color: #ef4444;
            }
            #previewFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            #textViewer {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                color: #0f172a;
                padding: 12px;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 13px;
                line-height: 1.5;
            }
            #actionBtn {
                background-color: #f8fafc;
                color: #1e293b;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 11px;
                font-weight: 600;
            }
            #actionBtn:hover {
                background-color: #f1f5f9;
                color: #0f172a;
                border-color: #94a3b8;
            }
            #appendBtn {
                background-color: #4f46e5;
                color: #ffffff;
                border: 1px solid #4338ca;
                border-radius: 6px;
                padding: 5px 11px;
                font-size: 11px;
                font-weight: 600;
            }
            #appendBtn:hover {
                background-color: #4338ca;
                color: #ffffff;
                border-color: #3730a3;
            }
            #chatInput {
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                color: #0f172a;
                padding: 8px 12px;
                font-size: 13px;
            }
            #chatInput:focus {
                background-color: #ffffff;
                border: 1px solid #4f46e5;
            }
            #sendBtn {
                background-color: #4f46e5;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                width: 36px;
                height: 34px;
            }
            #sendBtn:hover {
                background-color: #4338ca;
            }
        """)

        self.text_viewer.document().setDefaultStyleSheet("""
            body {
                color: #0f172a;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 13px;
                line-height: 1.6;
            }
            h1, h2, h3, h4 {
                color: #0f172a;
                font-weight: 700;
                margin-top: 10px;
                margin-bottom: 4px;
            }
            p {
                margin-bottom: 6px;
                color: #1e293b;
            }
            code {
                background-color: #f1f5f9;
                color: #4338ca;
                padding: 2px 5px;
                border: 1px solid #e2e8f0;
                border-radius: 4px;
                font-family: 'Consolas', 'Cascadia Code', monospace;
                font-size: 12px;
            }
            pre {
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 10px;
                color: #0f172a;
                font-family: 'Consolas', 'Cascadia Code', monospace;
                font-size: 12px;
            }
            ul, ol {
                margin-left: 16px;
                margin-bottom: 6px;
                color: #1e293b;
            }
            li {
                margin-bottom: 2px;
            }
        """)

    def _apply_dark_styles(self):
        if hasattr(self, 'shadow'):
            self.shadow.setColor(QColor(0, 0, 0, 180))

        self.setStyleSheet("""
            #cardFrame {
                background-color: #16161a;
                border: 1px solid #27272e;
                border-radius: 14px;
            }
            #titleLabel {
                color: #ffffff;
                font-size: 15px;
                font-weight: 700;
                font-family: 'Segoe UI', sans-serif;
            }
            #statusBadge {
                background-color: #27272a;
                color: #a1a1aa;
                font-size: 11px;
                padding: 3px 8px;
                border-radius: 10px;
                font-weight: 600;
            }
            #iconBtn {
                background-color: transparent;
                border: none;
                color: #71717a;
                font-size: 14px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 6px;
            }
            #iconBtn:hover {
                background-color: #27272a;
                color: #818cf8;
            }
            #closeBtn {
                background-color: transparent;
                border: none;
                color: #71717a;
                font-size: 14px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 6px;
            }
            #closeBtn:hover {
                background-color: #27272a;
                color: #f43f5e;
            }
            #previewFrame {
                background-color: #1c1c22;
                border: 1px solid #2a2a35;
                border-radius: 8px;
            }
            #textViewer {
                background-color: #121215;
                border: 1px solid #23232b;
                border-radius: 10px;
                color: #e2e8f0;
                padding: 12px;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 13px;
                line-height: 1.5;
            }
            #actionBtn {
                background-color: #222228;
                color: #cbd5e1;
                border: 1px solid #32323e;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 11px;
                font-weight: 600;
            }
            #actionBtn:hover {
                background-color: #2e2e38;
                color: #ffffff;
                border-color: #4b4b5e;
            }
            #appendBtn {
                background-color: #312e81;
                color: #e0e7ff;
                border: 1px solid #4338ca;
                border-radius: 6px;
                padding: 5px 11px;
                font-size: 11px;
                font-weight: 600;
            }
            #appendBtn:hover {
                background-color: #3730a3;
                color: #ffffff;
                border-color: #6366f1;
            }
            #chatInput {
                background-color: #1c1c22;
                border: 1px solid #2c2c38;
                border-radius: 8px;
                color: #f8fafc;
                padding: 8px 12px;
                font-size: 13px;
            }
            #chatInput:focus {
                border: 1px solid #6366f1;
            }
            #sendBtn {
                background-color: #6366f1;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                width: 36px;
                height: 34px;
            }
            #sendBtn:hover {
                background-color: #4f46e5;
            }
        """)

        self.text_viewer.document().setDefaultStyleSheet("""
            body {
                color: #f1f5f9;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 13px;
                line-height: 1.6;
            }
            h1, h2, h3, h4 {
                color: #ffffff;
                font-weight: 600;
                margin-top: 10px;
                margin-bottom: 4px;
            }
            p {
                margin-bottom: 6px;
            }
            code {
                background-color: #24242d;
                color: #818cf8;
                padding: 2px 4px;
                border-radius: 4px;
                font-family: 'Consolas', 'Cascadia Code', monospace;
                font-size: 12px;
            }
            pre {
                background-color: #1a1a20;
                border: 1px solid #2e2e38;
                border-radius: 6px;
                padding: 8px;
                color: #e2e8f0;
                font-family: 'Consolas', 'Cascadia Code', monospace;
                font-size: 12px;
            }
            ul, ol {
                margin-left: 16px;
                margin-bottom: 6px;
            }
            li {
                margin-bottom: 2px;
            }
        """)

    # Window Dragging implementation
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(event)

    def set_status(self, text: str, color_hex: Optional[str] = None):
        self.status_badge.setText(text)
        is_light = (Config.get_theme() != "dark")
        if not color_hex:
            color_hex = "#475569" if is_light else "#a1a1aa"
        bg_color = "#f1f5f9" if is_light else "#27272a"
        border_css = "border: 1px solid #e2e8f0;" if is_light else "border: none;"
        self.status_badge.setStyleSheet(f"""
            background-color: {bg_color};
            color: {color_hex};
            {border_css}
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 10px;
            font-weight: 600;
        """)

    def start_analysis(self, image_bytes: bytes, pil_img=None, append: bool = False):
        """Displays HUD and starts streaming screen analysis (single or multi-snapshot)."""
        if append and self.captured_images:
            self.captured_images.append(image_bytes)
            if pil_img:
                self.captured_pils.append(pil_img)
            self.full_response_text += f"\n\n---\n📸 **Attached Scrolled Snapshot #{len(self.captured_images)}**\n*Synthesizing all sections to analyze complete problem & constraints...*\n\n"
            self.text_viewer.setMarkdown(self.full_response_text)
            self.set_status(f"🔮 Combining {len(self.captured_images)} Screens...", "#a855f7")
            self.preview_info.setText(f"{len(self.captured_images)} Scrolled Slices Combined")
        else:
            self.captured_images = [image_bytes]
            self.captured_pils = [pil_img] if pil_img else []
            self.full_response_text = ""
            self.text_viewer.clear()
            self.set_status("🔮 Analyzing...", "#818cf8")
            if pil_img:
                self._set_thumbnail(pil_img)
            self.preview_info.setText("Captured screen analyzed")

        stealth_show(self)

        # Start streaming worker with list of all captured screenshots
        self._start_worker(image_bytes=self.captured_images)

    def _set_thumbnail(self, pil_img):
        try:
            # Create small thumbnail
            thumb = pil_img.copy()
            thumb.thumbnail((120, 72))
            bytes_io = sys.modules['io'].BytesIO()
            thumb.save(bytes_io, format="PNG")
            qimg = QImage.fromData(bytes_io.getvalue())
            pixmap = QPixmap.fromImage(qimg)
            self.thumb_label.setPixmap(pixmap)
            self.preview_frame.setVisible(True)
        except Exception:
            self.preview_frame.setVisible(False)

    def _send_followup(self):
        text = self.chat_input.text().strip()
        if not text:
            return

        self.chat_input.clear()
        self.full_response_text += f"\n\n---\n**You:** {text}\n\n**PeekAI:** "
        self.text_viewer.setMarkdown(self.full_response_text)
        self._scroll_to_bottom()

        self.set_status("⚡ Thinking...", "#818cf8")
        self._start_worker(followup_text=text)

    def _start_worker(self, image_bytes: Optional[Union[bytes, List[bytes]]] = None, followup_text: Optional[str] = None):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()

        self.worker = StreamWorker(self.ai_service, image_bytes=image_bytes, followup_text=followup_text)
        self.worker.chunk_received.connect(self._on_chunk)
        self.worker.stream_finished.connect(self._on_finished)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.start()

    def _on_chunk(self, chunk: str):
        self.full_response_text += chunk
        self.text_viewer.setMarkdown(self.full_response_text)
        self._scroll_to_bottom()
        self.set_status("⚡ Streaming...", "#34d399")

    def _on_finished(self):
        self.set_status("✓ Ready", "#10b981")
        self._restore_copy_btn_text()

    def _on_error(self, err_msg: str):
        self.set_status("⚠️ Error", "#f43f5e")
        self.full_response_text += f"\n\n❌ **Error:** {err_msg}"
        self.text_viewer.setMarkdown(self.full_response_text)

    def _scroll_to_bottom(self):
        scrollbar = self.text_viewer.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _copy_answer(self):
        # 1. If user selected text manually in text_viewer, copy the selected text
        cursor = self.text_viewer.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText().replace('\u2029', '\n').strip()
            if selected:
                QApplication.clipboard().setText(selected)
                self.copy_btn.setText("✓ Copied Selection!")
                QTimer.singleShot(1500, self._restore_copy_btn_text)
                return

        if not self.full_response_text:
            return

        # 2. Extract clean solution (pure code or MCQ answer)
        clean_ans = extract_clean_answer(self.full_response_text)
        if clean_ans:
            QApplication.clipboard().setText(clean_ans)
            if "```" in self.full_response_text or "\n" in clean_ans:
                self.copy_btn.setText("✓ Code Copied!")
            else:
                self.copy_btn.setText("✓ Answer Copied!")
        else:
            QApplication.clipboard().setText(self.full_response_text)
            self.copy_btn.setText("✓ Copied!")

        QTimer.singleShot(1500, self._restore_copy_btn_text)

    def _restore_copy_btn_text(self):
        if "```" in self.full_response_text:
            self.copy_btn.setText("📋 Copy Code")
        else:
            self.copy_btn.setText("📋 Copy Answer")

    def _show_copy_menu(self, pos):
        menu = QMenu(self)
        is_light = (Config.get_theme() != "dark")
        bg = "#ffffff" if is_light else "#1c1c22"
        fg = "#0f172a" if is_light else "#f4f4f5"
        border = "1px solid #cbd5e1" if is_light else "1px solid #2e2e38"
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {bg};
                color: {fg};
                border: {border};
                border-radius: 6px;
                padding: 4px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }}
            QMenu::item {{
                padding: 5px 16px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: #4f46e5;
                color: #ffffff;
            }}
        """)
        copy_code = menu.addAction("📋 Copy Clean Answer / Code")
        copy_all = menu.addAction("📄 Copy Full Raw Markdown")

        action = menu.exec(self.copy_btn.mapToGlobal(pos))
        if action == copy_code:
            self._copy_answer()
        elif action == copy_all:
            if self.full_response_text:
                QApplication.clipboard().setText(self.full_response_text)
                self.copy_btn.setText("✓ Full Text Copied!")
                QTimer.singleShot(1500, self._restore_copy_btn_text)

    def _clear_content(self):
        self.captured_images.clear()
        self.captured_pils.clear()
        self.full_response_text = ""
        self.text_viewer.setHtml(self._get_ready_html())
        self.preview_frame.setVisible(False)
        self.copy_btn.setText("📋 Copy Answer")
        self.set_status("Ready")
