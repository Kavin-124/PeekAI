"""Settings dialog for configuring Gemini API Key and preferences."""
import webbrowser
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QFrame, QSizePolicy, QCheckBox, QApplication
)
from google import genai
from src.config import Config
from src.autostart import is_autostart_enabled, enable_autostart, disable_autostart


class SettingsDialog(QDialog):
    """Configuration dialog for API keys and models."""

    settings_saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PeekAI - Settings")
        self.setMinimumSize(540, 560)
        self.resize(540, 580)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self._init_ui()
        self._apply_styles()
        self._load_current_values()

    def showEvent(self, event):
        super().showEvent(event)
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.availableGeometry()
            x = screen_geo.x() + (screen_geo.width() - self.width()) // 2
            y = screen_geo.y() + (screen_geo.height() - self.height()) // 2
            self.move(x, y)
        self.raise_()
        self.activateWindow()

    def _apply_styles(self, theme=None):
        if theme is None:
            theme = Config.get_theme()
        if theme == "dark":
            self._apply_dark_styles()
        else:
            self._apply_light_styles()

    def _apply_light_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                color: #0f172a;
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            }
            #headerLabel {
                font-size: 20px;
                font-weight: bold;
                color: #0f172a;
            }
            #subLabel {
                color: #64748b;
                font-size: 13px;
            }
            #sectionLabel {
                font-weight: 600;
                color: #1e293b;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #f8fafc;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                min-height: 22px;
            }
            QLineEdit:focus {
                border: 1px solid #4f46e5;
                background-color: #ffffff;
            }
            QComboBox {
                background-color: #f8fafc;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
                min-height: 24px;
            }
            QComboBox:focus {
                border: 1px solid #4f46e5;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 32px;
                border-left: 1px solid #cbd5e1;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748b;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                selection-background-color: #4f46e5;
                selection-color: #ffffff;
                padding: 6px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #f1f5f9;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 9px 16px;
                font-weight: 600;
                font-size: 13px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
            QPushButton#primaryBtn {
                background-color: #4f46e5;
                border: 1px solid #4338ca;
                color: #ffffff;
            }
            QPushButton#primaryBtn:hover {
                background-color: #4338ca;
            }
            QPushButton#linkBtn {
                background: transparent;
                border: none;
                color: #4f46e5;
                text-decoration: underline;
                padding: 0px;
                font-weight: 500;
                font-size: 12px;
                min-height: 0px;
            }
            QPushButton#linkBtn:hover {
                color: #4338ca;
            }
            QPushButton#toggleEyeBtn {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 14px;
                min-height: 22px;
            }
            QPushButton#toggleEyeBtn:hover {
                background-color: #e2e8f0;
            }
            #infoFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
            #infoTitle {
                font-weight: bold;
                color: #4f46e5;
                font-size: 13px;
            }
            #hotkeyInfo {
                color: #334155;
                font-size: 12px;
                line-height: 1.6;
            }
            QCheckBox {
                color: #1e293b;
                font-size: 13px;
                spacing: 8px;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #cbd5e1;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #4f46e5;
                border: 1px solid #4338ca;
            }
        """)

    def _apply_dark_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #141417;
                color: #f4f4f5;
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            }
            #headerLabel {
                font-size: 20px;
                font-weight: bold;
                color: #ffffff;
            }
            #subLabel {
                color: #a1a1aa;
                font-size: 13px;
            }
            #sectionLabel {
                font-weight: 600;
                color: #f4f4f5;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #222226;
                color: #ffffff;
                border: 1px solid #3b3b45;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                min-height: 22px;
            }
            QLineEdit:focus {
                border: 1px solid #6366f1;
                background-color: #28282e;
            }
            QComboBox {
                background-color: #222226;
                color: #ffffff;
                border: 1px solid #3b3b45;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
                min-height: 24px;
            }
            QComboBox:focus {
                border: 1px solid #6366f1;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 32px;
                border-left: 1px solid #3b3b45;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #cbd5e1;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e24;
                color: #ffffff;
                border: 1px solid #3b3b45;
                selection-background-color: #6366f1;
                selection-color: #ffffff;
                padding: 6px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #26262c;
                color: #f4f4f5;
                border: 1px solid #3f3f4c;
                border-radius: 8px;
                padding: 9px 16px;
                font-weight: 600;
                font-size: 13px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #35353e;
            }
            QPushButton#primaryBtn {
                background-color: #6366f1;
                border: 1px solid #4f46e5;
                color: #ffffff;
            }
            QPushButton#primaryBtn:hover {
                background-color: #4f46e5;
            }
            QPushButton#linkBtn {
                background: transparent;
                border: none;
                color: #818cf8;
                text-decoration: underline;
                padding: 0px;
                font-weight: 500;
                font-size: 12px;
                min-height: 0px;
            }
            QPushButton#linkBtn:hover {
                color: #a5b4fc;
            }
            QPushButton#toggleEyeBtn {
                background-color: #2a2a32;
                border: 1px solid #3b3b45;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 14px;
                min-height: 22px;
            }
            #infoFrame {
                background-color: #1c1c22;
                border: 1px solid #2e2e38;
                border-radius: 10px;
            }
            #infoTitle {
                font-weight: bold;
                color: #818cf8;
                font-size: 13px;
            }
            #hotkeyInfo {
                color: #cbd5e1;
                font-size: 12px;
                line-height: 1.6;
            }
            QCheckBox {
                color: #e2e8f0;
                font-size: 13px;
                spacing: 8px;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #4b4b58;
                background-color: #222228;
            }
            QCheckBox::indicator:checked {
                background-color: #6366f1;
                border: 1px solid #818cf8;
            }
        """)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        header_label = QLabel("⚡ PeekAI Configuration")
        header_label.setObjectName("headerLabel")
        header_layout.addWidget(header_label)

        sub_label = QLabel("Configure your Gemini Flash Vision credentials and appearance preferences.")
        sub_label.setObjectName("subLabel")
        header_layout.addWidget(sub_label)
        layout.addLayout(header_layout)

        # API Key Section
        api_layout = QVBoxLayout()
        api_layout.setSpacing(8)

        key_header_layout = QHBoxLayout()
        key_label = QLabel("Gemini API Key:")
        key_label.setObjectName("sectionLabel")
        key_header_layout.addWidget(key_label)
        key_header_layout.addStretch()

        get_key_btn = QPushButton("Get Free API Key ↗")
        get_key_btn.setObjectName("linkBtn")
        get_key_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        get_key_btn.clicked.connect(lambda: webbrowser.open("https://aistudio.google.com/apikey"))
        key_header_layout.addWidget(get_key_btn)
        api_layout.addLayout(key_header_layout)

        # Input box with Show/Hide toggle
        key_input_layout = QHBoxLayout()
        key_input_layout.setSpacing(6)

        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("Paste your key here (AIzaSy...)")
        key_input_layout.addWidget(self.key_input)

        self.eye_btn = QPushButton("👁️")
        self.eye_btn.setObjectName("toggleEyeBtn")
        self.eye_btn.setToolTip("Show / Hide API Key")
        self.eye_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eye_btn.clicked.connect(self._toggle_echo_mode)
        key_input_layout.addWidget(self.eye_btn)

        api_layout.addLayout(key_input_layout)
        layout.addLayout(api_layout)

        # Model Selection
        model_layout = QVBoxLayout()
        model_layout.setSpacing(8)

        model_label = QLabel("Vision AI Model:")
        model_label.setObjectName("sectionLabel")
        model_layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gemini-3.5-flash-lite",
            "gemini-3-flash-preview",
            "gemini-flash-latest",
        ])
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # Theme Selection
        theme_layout = QVBoxLayout()
        theme_layout.setSpacing(8)

        theme_label = QLabel("Appearance Theme:")
        theme_label.setObjectName("sectionLabel")
        theme_layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            "Light Theme (Clean & Modern)",
            "Dark Theme (Stealth Black)",
        ])
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Autostart Checkbox
        self.autostart_cb = QCheckBox("🚀 Start PeekAI automatically when Windows boots")
        self.autostart_cb.setChecked(is_autostart_enabled())
        layout.addWidget(self.autostart_cb)

        # Info Box about Hotkeys
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(14, 12, 14, 12)
        info_layout.setSpacing(6)

        info_title = QLabel("⌨️ Active Hotkeys")
        info_title.setObjectName("infoTitle")
        info_layout.addWidget(info_title)

        hotkey_info = QLabel(
            "• <b>Ctrl + Shift + Space:</b> Full-Screen Peek (Instant capture)<br>"
            "• <b>Ctrl + Shift + X:</b> Snippet Region Peek (Drag to crop)<br>"
            "• <b>Ctrl + Shift + A:</b> Append Scrolled Screen (Combine multi-part question)<br>"
            "• <b>Ctrl + Alt + C:</b> Stealth Copy (Quickly copy answer/code)<br>"
            "• <b>Ctrl + Shift + S:</b> Settings & Theme Dialog (Or click ⚙️)<br>"
            "• <b>Esc:</b> Dismiss Floating HUD or Cancel Selection"
        )
        hotkey_info.setObjectName("hotkeyInfo")
        hotkey_info.setWordWrap(True)
        info_layout.addWidget(hotkey_info)
        layout.addWidget(info_frame)

        layout.addStretch()

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.test_btn = QPushButton("Test API Key")
        self.test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.test_btn.clicked.connect(self._test_api_key)
        btn_layout.addWidget(self.test_btn)

        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setObjectName("primaryBtn")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

    def _toggle_echo_mode(self):
        if self.key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.eye_btn.setText("🔒")
        else:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.eye_btn.setText("👁️")

    def _load_current_values(self):
        current_key = Config.get_api_key()
        if current_key:
            self.key_input.setText(current_key)

        current_model = Config.get_model()
        idx = self.model_combo.findText(current_model)
        if idx >= 0:
            self.model_combo.setCurrentIndex(idx)

        current_theme = Config.get_theme()
        theme_idx = 1 if current_theme == "dark" else 0
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentIndex(theme_idx)
        self.theme_combo.blockSignals(False)
        self._apply_styles(current_theme)

    def _on_theme_changed(self):
        selected_theme = "dark" if "dark" in self.theme_combo.currentText().lower() else "light"
        self._apply_styles(selected_theme)

    def _test_api_key(self):
        import time
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Missing Key", "Please enter an API Key to test.")
            return

        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing...")
        client = genai.Client(api_key=key)
        preferred_model = self.model_combo.currentText()
        candidate_models = [preferred_model] + [m for m in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-3.8-flash"] if m != preferred_model]

        last_error = None
        succeeded_model = None

        for model_name in candidate_models:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents="Reply with 'OK'"
                    )
                    if response and response.text:
                        succeeded_model = model_name
                        break
                except Exception as e:
                    last_error = e
                    # If 503 high demand, short delay and retry
                    if "503" in str(e) or "UNAVAILABLE" in str(e):
                        time.sleep(1.2)
                        continue
                    else:
                        # If invalid key (400/403), stop immediately
                        break
            if succeeded_model:
                break

        self.test_btn.setEnabled(True)
        self.test_btn.setText("Test API Key")

        if succeeded_model:
            # Update combo box if we switched to a working model
            idx = self.model_combo.findText(succeeded_model)
            if idx >= 0:
                self.model_combo.setCurrentIndex(idx)

            if succeeded_model == preferred_model:
                QMessageBox.information(self, "Success", f"Connection successful! Your API key is valid on {succeeded_model}.")
            else:
                QMessageBox.information(
                    self,
                    "Success with Alternate Model",
                    f"Your API key is 100% valid!\n\n'{preferred_model}' is currently experiencing high demand on Google servers, so PeekAI automatically switched to '{succeeded_model}' for instant reliability."
                )
        else:
            QMessageBox.critical(self, "Connection Error", f"API connection test failed:\n{str(last_error)}")

    def _save_settings(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Missing Key", "Please enter a valid Gemini API Key.")
            return

        Config.set_api_key(key)
        Config.set_model(self.model_combo.currentText())

        selected_theme = "dark" if "dark" in self.theme_combo.currentText().lower() else "light"
        Config.set_theme(selected_theme)

        if self.autostart_cb.isChecked():
            enable_autostart()
        else:
            disable_autostart()

        self.settings_saved.emit()
        self.accept()
