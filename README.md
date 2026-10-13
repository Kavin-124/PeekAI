<div align="center">

<img src="assets/banner.svg" alt="PeekAI Banner" width="100%" />

<br/><br/>

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6%20Glassmorphic-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![Google Gemini](https://img.shields.io/badge/Vision%20AI-Google%20Gemini%20Flash-8E44AD?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![OS Windows](https://img.shields.io/badge/OS-Windows%2010%20%2F%2011-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-F1C40F?style=for-the-badge)](LICENSE)

<br/>

<p align="center">
  <b>Instant screen reasoning • Multi-page question stitching • Clean code extraction • Zero focus loss</b>
</p>

[Key Features](#-key-features) •
[UI Showcase](#-ui--themes-showcase) •
[Global Shortcuts](#-global-shortcuts-matrix) •
[Architecture & Stealth](#-stealth-focus-protection-engine) •
[Feature Comparison](#-how-peekai-compares) •
[Quick Start](#-quick-start) •
[Testing](#-automated-verification--stress-tests)

</div>

---

## 🌟 Overview

**PeekAI** is a high-performance Windows desktop copilot powered by Google's **Gemini Vision** models. Built for competitive programmers, developers, students, and researchers, PeekAI delivers sub-second visual intelligence directly from your screen with a single global keystroke.

Unlike standard screen capture tools, PeekAI is engineered with a **native OS-level stealth engine** (`WS_EX_NOACTIVATE` + `WindowDoesNotAcceptFocus`). The floating HUD stays completely invisible to proctoring monitors, online assessment portals (such as **NeoPAT, Mettl, HackerEarth, and Mercer**), and full-screen browser tabs — **never stealing window focus or triggering focus-loss alerts**.

---

## 📸 UI & Themes Showcase

<div align="center">
  <img src="assets/screenshots/peekai_themes_showcase.png" alt="PeekAI Light and Dark Theme Showcase" width="100%" style="border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);" />
  <p><i>Left: ☀️ Modern Light Theme (Clean &amp; High-Contrast) • Right: 🌙 Stealth Dark Theme (Real-Time Code Analysis &amp; Complexity Breakdown)</i></p>
</div>

---

## ✨ Key Features

### ⚡ 1. Sub-30ms Instant Screen Analysis (`Ctrl + Shift + Space`)
* Captures high-resolution screen frames in under **30 milliseconds** via low-level Windows display memory buffers (`mss`).
* Streams structured reasoning, code solutions, or document summaries in real time with token-by-token rendering.

### ✂️ 2. Snippet Region Drag & Crop (`Ctrl + Shift + X`)
* Pixel-precise translucent crosshair cropper.
* Drag to isolate a stubborn compiler trace, a specific graph, an architecture diagram, or an individual MCQ without cluttering AI context with background windows.

### 📸 3. Multi-Slice Snap & Append (`Ctrl + Shift + A`)
* Solves the **"long scrolling question"** problem!
* Captures the first section, lets you scroll down through code/problem constraints, and appends consecutive slices. PeekAI synthesizes all snapshots together into one cohesive, comprehensive answer.

### 🔒 4. Zero-Focus-Stealing Stealth Engine
* Uses Windows native `WS_EX_NOACTIVATE` extended window styles.
* Clicking anywhere on the PeekAI HUD, copying code, or reading answers **does not strip keyboard or window focus** from your underlying exam tab or IDE.

### 📋 5. Stealth Copy: Pure Code & Answer Extractor (`Ctrl + Alt + C`)
* Strips conversational filler and extracts **only the clean, runnable code** (Python, C++, Java, etc.) or **decisive MCQ answer choice** straight to your clipboard.

### ☀️ 6. Modern Light & 🌙 Stealth Dark Themes
* **Modern Light Theme** *(Default)*: Clean `#ffffff` card with slate typography and soft drop-shadow, blending naturally with white browser pages and exam portals.
* **Classic Dark Theme**: Stealth pitch-black glassmorphic palette.
* **Instant Live Preview**: Toggle themes on the fly from Settings (`Ctrl + Shift + S`) without restarting the app.

### 💬 7. Contextual Multi-Turn Follow-Up Chat
* Ask clarifying questions, request alternative algorithms, or change programming languages in the HUD's bottom prompt bar within the same visual snapshot context.

---

## ⌨️ Global Shortcuts Matrix

| Keystroke | Function | Description | Context / Use Case |
| :--- | :--- | :--- | :--- |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Space</kbd> | **Full Screen Peek** | Captures and analyzes entire primary monitor | Instant full-page question solving |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>X</kbd> | **Snippet Crop Peek** | Drag crosshair to select a custom region | Isolate error stack traces or specific MCQs |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>A</kbd> | **Snap & Append** | Combine scrolled multi-part questions | Multi-page questions, long code constraints |
| <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>C</kbd> | **Stealth Copy** | Extracts pure code or clean MCQ option | Zero-focus copy directly into clipboard |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd> | **Settings & Themes** | Instant configuration modal (or click <kbd>⚙️</kbd> on HUD) | Live theme switcher, API key & model settings |
| <kbd>Esc</kbd> | **Dismiss / Minimize** | Hides floating HUD to system tray or cancels crop | Immediate emergency dismissal |

---

## 📊 How PeekAI Compares

| Capability | Standard Snipping / OCR Tools | Web-Based LLMs (ChatGPT / Claude) | ⚡ PeekAI |
| :--- | :---: | :---: | :---: |
| **Window Focus Retention** | ❌ Steals focus (Triggers alert) | ❌ Requires tab switching | ✅ **100% Immune (`WS_EX_NOACTIVATE`)** |
| **Frame Capture Speed** | ⚠️ ~300ms – 800ms | ❌ Manual upload required | ✅ **&lt; 30ms Direct Framebuffer** |
| **Multi-Page Question Stitching** | ❌ Single screenshot only | ⚠️ Multiple manual uploads | ✅ **1-Click Snap & Append (`Ctrl+Shift+A`)** |
| **Pure Code Extraction** | ❌ Copies entire prose | ⚠️ Code markdown fences | ✅ **Pure Code / MCQ Extractor (`Ctrl+Alt+C`)** |
| **Real-Time Token Streaming** | ❌ No streaming | ⚠️ Browser window only | ✅ **Glassmorphic Floating Overlay** |
| **Theme Adaptability** | ❌ Static OS theme | ⚠️ Browser-dependent | ✅ **Seamless Light &amp; Dark Live Switcher** |
| **Proctoring Protection** | ❌ Triggers `window.onblur` | ❌ Triggers `visibilitychange` | ✅ **Zero OS Focus Events Emitted** |

---

## 🏗️ Stealth Focus-Protection Engine

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 Developer / Student
    participant OS as 🪟 Windows OS Kernel
    participant Hook as ⌨️ Hotkey Listener (pynput)
    participant Core as ⚡ PeekAI App
    participant Cap as 📸 mss Capture Engine
    participant AI as 🧠 Google Gemini Vision API
    participant HUD as 🪟 Stealth HUD (WS_EX_NOACTIVATE)

    Note over User,OS: Active Exam / Browser Window Retains 100% Focus
    User->>Hook: Press Ctrl+Shift+Space / Ctrl+Shift+A
    Hook->>Core: Emit Trigger Signal (< 1ms)
    Core->>Cap: Grab Direct Framebuffer
    Cap-->>Core: Raw RGB Bytes (18-28ms)
    Core->>HUD: Show Window in Stealth Mode (0 Focus Loss)
    Core->>AI: Stream Multimodal Payload (HTTPS)
    loop Real-Time Token Streaming
        AI-->>HUD: Stream Markdown / Code Chunks
        HUD-->>User: Instant Display in Real-Time
    end
    User->>Hook: Press Ctrl+Alt+C
    Hook->>HUD: Trigger Stealth Copy Command
    HUD-->>User: Pure Code / Clean MCQ Option Copied to Clipboard
```

> [!IMPORTANT]
> **Proctoring Immunity**: Online assessment portals detect tab-switching using JavaScript `window.onblur` and `document.visibilitychange` event listeners. Because PeekAI runs with Windows native `WS_EX_NOACTIVATE` extended style, Windows **never fires a blur event** on your underlying window, guaranteeing zero focus loss warnings.

---

## 🚀 Quick Start

### 1. Prerequisites
* **Windows 10 / 11** (64-bit)
* **Python 3.10+** (Tested on Python 3.12, 3.13, 3.14)
* **Google Gemini API Key** — [Get your free key from Google AI Studio](https://aistudio.google.com/apikey)

### 2. Installation

```powershell
# Clone the repository
git clone https://github.com/Kavin-124/PeekAI.git
cd PeekAI

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install production dependencies
pip install -r requirements.txt
```

### 3. Setup API Key

Copy the sample environment configuration:
```powershell
copy .env.example .env
```

Add your Gemini API Key in `.env`:
```env
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere...
PEEK_MODEL=gemini-3.5-flash-lite
PEEK_THEME=light
```
*(Alternatively, simply launch PeekAI — the app will automatically prompt you with the Settings dialog on first run).*

### 4. Launch PeekAI

Double-click **`run_peekai.bat`** or run from PowerShell:

```powershell
.\.venv\Scripts\python main.py
```

> [!TIP]
> **Zero Console Window**: Double-clicking `run_peekai.bat` launches PeekAI silently in the background with a system tray icon.

---

## 📁 Repository Structure

```
PeekAI/
├── assets/
│   ├── banner.svg               # Modern vector hero banner
│   ├── icon.ico                 # High-resolution application icon
│   ├── icon.png                 # Glassmorphic branding badge
│   └── screenshots/
│       ├── peekai_light_mode.png        # Modern Light Theme HUD card
│       ├── peekai_dark_solution.png     # Stealth Dark Theme with Python code
│       └── peekai_themes_showcase.png   # Side-by-side comparison showcase
├── src/
│   ├── __init__.py
│   ├── ai_service.py            # Gemini Flash Vision multimodal pipeline & streaming
│   ├── autostart.py             # Windows startup & desktop shortcut automation
│   ├── capture.py               # Fast memory-buffered screen capture (mss + Pillow)
│   ├── config.py                # Configuration loader & persistent theme manager
│   ├── hotkey_listener.py       # Low-level Windows global key hooks (pynput + Win32)
│   └── ui/
│       ├── __init__.py
│       ├── append_overlay.py    # Floating scroll-guide pill for multi-part captures
│       ├── floating_hud.py      # Glassmorphic HUD overlay (Light & Dark themes)
│       ├── settings_dialog.py   # Settings manager (API keys, models, themes)
│       ├── snippet_overlay.py   # Fullscreen region selection sniper overlay
│       └── tray_icon.py         # Windows taskbar notification tray integration
├── tests/
│   ├── stress_test_1000.py      # 1,000-cycle focus immunity & endurance stress test
│   ├── test_core.py             # Screen capture & AI service unit tests
│   ├── test_followup.py         # Multi-turn chat context verification
│   ├── test_stealth.py          # Native WS_EX_NOACTIVATE verification test
│   ├── test_theme.py            # Dynamic Light/Dark theme switching test
│   └── test_ui.py               # UI components & clean answer extraction test
├── .env.example                 # Environment configuration template
├── .gitignore                   # Excludes .env, .venv, and logs
├── LICENSE                      # MIT Open-Source License
├── main.py                      # App lifecycle, IPC single-instance, signal router
├── README.md                    # Project documentation
├── requirements.txt             # Pinned production dependencies
├── run_peekai.bat               # 1-click silent background launcher
└── run_peekai_debug.bat         # Verbose debug launcher with error trapping
```

---

## 🧪 Automated Verification & Stress Tests

PeekAI includes an automated test suite covering performance, visual themes, and focus retention:

```powershell
# Run the complete test suite
.\.venv\Scripts\python -c "import tests.test_core as t1, tests.test_stealth as t2, tests.test_ui as t3, tests.test_theme as t4; t1.test_config(); t1.test_capture(); t2.test_stealth_hud(); t3.test_ui_components(); t4.test_theme_system(); print('\n>>> ALL MODULES, STEALTH FLAGS, & THEMES 100% VERIFIED! <<<')"
```

### Benchmark Metrics:
* ⚡ **Frame Grab Latency**: `18ms – 28ms`
* ⚡ **First Token Response**: `< 1.2s` on `gemini-3.5-flash-lite`
* 🔒 **Focus Retention Rate**: `100% / 1,000 test cycles` (0 focus-lost triggers detected)

---

## 🛡️ Privacy & Security

* **Local-First & Ephemeral**: Screenshots are never saved to disk or uploaded to third-party databases. Frames live purely in volatile memory buffers and are transmitted directly to Google's official Gemini API over TLS encryption.
* **Credential Isolation**: Your `GEMINI_API_KEY` stays exclusively on your machine in `.env` and is strictly ignored from version control via `.gitignore`.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <b>Built with ❤️ by <a href="https://github.com/Kavin-124">Kavin</a> for peak productivity and seamless screen intelligence.</b>
</div>
