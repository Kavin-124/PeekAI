# ⚡ PeekAI — Desktop AI Screen Copilot

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GUI PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![AI Powered](https://img.shields.io/badge/Vision_AI-Google_Gemini-8e44ad.svg)](https://ai.google.dev/)
[![OS Windows](https://img.shields.io/badge/OS-Windows_10%20%2F%2011-0078d4.svg)](https://microsoft.com/windows)
[![License MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**PeekAI** is an ultra-fast, intelligent, glassmorphic desktop screen copilot built for developers, students, and professionals. With a single keystroke, it analyzes what's on your screen, solves coding problems, parses MCQs, summarizes documents, and answers follow-up questions — **without ever stealing focus or triggering exam tab-switch warnings**.

---

## ✨ Key Features

- **⚡ Instant Screen Snapshot (`Ctrl + Shift + Space`)**:
  - Captures primary display in <30ms using low-level `mss`.
  - Streams structured visual insights directly from Google's latest **Gemini Flash Vision** models.

- **✂️ Snippet / Region Crop (`Ctrl + Shift + X`)**:
  - Interactive sniper crosshair overlay to drag, crop, and analyze only the relevant window, terminal error, or code section.

- **📸 Multi-Snapshot Snap & Append (`Ctrl + Shift + A`)**:
  - Solves the long question / multi-page problem! Scroll your document or browser and append multiple screen slices. PeekAI synthesizes all parts together into a unified answer.

- **🔒 Zero-Focus-Stealing Stealth Engine**:
  - Built with native Windows `WS_EX_NOACTIVATE` and Qt `WindowDoesNotAcceptFocus`.
  - Your underlying browser, IDE, or exam portal (NeoPAT, Mettl, HackerEarth, etc.) **never loses window focus**. Zero focus-lost alerts!

- **📋 1-Click Stealth Answer & Pure Code Copy (`Ctrl + Alt + C`)**:
  - Instantly filters out AI chatter and extracts only the clean code or decisive MCQ option into your clipboard.

- **☀️ Light & 🌙 Dark Appearance Themes**:
  - Clean, high-contrast Modern Light Theme by default (blends seamlessly with white browser and exam tabs).
  - Classic Stealth Dark Theme available at the click of a button in Settings.

- **⚙️ Integrated Settings & Theme Switcher (`Ctrl + Shift + S` or `⚙️`)**:
  - Test Gemini API keys live, switch models (`gemini-3.5-flash-lite`, `gemini-3-flash-preview`), and toggle Windows Autostart on boot.

- **💬 Interactive Follow-up Chat**:
  - Type questions directly into the floating HUD to continue discussing the screenshot context in real time.

---

## ⌨️ Global Shortcuts

| Shortcut | Action | Description |
| :--- | :--- | :--- |
| `Ctrl + Shift + Space` | **Full Screen Peek** | Captures and analyzes entire active monitor instantly |
| `Ctrl + Shift + X` | **Snippet Crop Peek** | Drag to select and analyze a specific region |
| `Ctrl + Shift + A` | **Snap & Append** | Capture scrolled slices & synthesize multi-part problems |
| `Ctrl + Alt + C` | **Stealth Copy** | Copies pure code or clean answer without stealing window focus |
| `Ctrl + Shift + S` | **Settings & Themes** | Opens configuration dialog (API key, model, theme toggle) |
| `Esc` | **Dismiss / Minimize** | Minimizes floating HUD or cancels active snippet selection |

---

## 🚀 Quick Start

### 1. Prerequisites
- **Windows 10 / 11**
- **Python 3.10+** (Tested on Python 3.12, 3.13, 3.14)
- **Google Gemini API Key** — [Get your free key at Google AI Studio](https://aistudio.google.com/apikey)

### 2. Installation

Clone this repository and navigate to the folder:

```bash
git clone https://github.com/Kavin-124/PeekAI.git
cd PeekAI
```

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### 3. Setup Credentials

Copy the template configuration file:

```powershell
copy .env.example .env
```

Open `.env` and paste your Gemini API Key:
```env
GEMINI_API_KEY=AIzaSy...
```
*(Or launch the app directly — PeekAI will automatically prompt you with the Settings dialog if no key is found).*

### 4. Launch PeekAI

Double-click **`run_peekai.bat`** (or run from terminal):

```powershell
.\.venv\Scripts\python main.py
```

PeekAI will appear in the top-right corner of your screen ready to assist!

---

## 🏗️ Project Architecture

```
PeekAI/
│
├── main.py                  # Application entry point, IPC single-instance, signal router
├── requirements.txt         # Core dependencies (PyQt6, google-genai, mss, Pillow, pynput)
├── run_peekai.bat           # 1-click silent desktop launcher
├── run_peekai_debug.bat     # Verbose console launcher for debugging
├── .env.example             # Environment configuration template
│
├── src/
│   ├── config.py            # .env loader, model selector & theme persistence
│   ├── capture.py           # Sub-30ms screen capture via mss & Pillow
│   ├── ai_service.py        # Gemini Flash Vision multimodal analysis & token streaming
│   ├── hotkey_listener.py   # Global low-level hook listener via pynput & Win32 API
│   ├── autostart.py         # Windows Startup folder & Desktop shortcut manager
│   │
│   └── ui/
│       ├── floating_hud.py      # Glassmorphic HUD overlay (Light/Dark stylesheets)
│       ├── snippet_overlay.py   # Fullscreen region selection overlay
│       ├── append_overlay.py    # Floating scroll & append helper bar
│       ├── settings_dialog.py   # Configuration manager (API key, models, themes)
│       └── tray_icon.py         # Windows taskbar notification tray integration
│
└── tests/
    ├── test_core.py         # Unit tests for capture, config, and Gemini AI engine
    ├── test_stealth.py      # WS_EX_NOACTIVATE anti-proctoring verification tests
    ├── test_ui.py           # Clean answer extraction & UI component tests
    ├── test_theme.py        # Automated Light & Dark theme toggle tests
    └── stress_test_1000.py  # 1,000-iteration focus stability & performance stress test
```

---

## 🔒 Privacy & Security

- **Local-First & Ephemeral**: PeekAI does NOT save screenshots to your hard drive or upload them to third-party databases. Images are processed in-memory directly via Google's official Gemini API.
- **Your Keys Stay Yours**: Your `GEMINI_API_KEY` is saved locally in your own `.env` file and is never transmitted anywhere other than Google AI Studio.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
Built with ❤️ for ultra-fast productivity.
