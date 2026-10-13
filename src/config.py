"""Configuration manager for PeekAI."""
import os
from pathlib import Path
from dotenv import load_dotenv, set_key

# Project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"

# Ensure .env exists
if not ENV_PATH.exists():
    example_path = ROOT_DIR / ".env.example"
    if example_path.exists():
        ENV_PATH.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        ENV_PATH.touch()

# Load environment variables
load_dotenv(dotenv_path=ENV_PATH, override=True)


class Config:
    """Application configuration and persistence."""

    DEFAULT_MODEL = "gemini-3.5-flash-lite"
    DEFAULT_THEME = "light"
    DEFAULT_HOTKEY_FULL = "<ctrl>+<shift>+<space>"
    DEFAULT_HOTKEY_SNIPPET = "<ctrl>+<shift>+x"
    DEFAULT_HOTKEY_APPEND = "<ctrl>+<shift>+a"
    DEFAULT_HOTKEY_COPY = "<ctrl>+<alt>+c"

    @classmethod
    def get_theme(cls) -> str:
        """Returns the configured UI theme ('light' or 'dark'). Defaults to 'light'."""
        return os.environ.get("PEEK_THEME", cls.DEFAULT_THEME).strip().lower()

    @classmethod
    def set_theme(cls, theme_name: str) -> None:
        """Saves chosen theme to .env."""
        theme_name = theme_name.strip().lower()
        os.environ["PEEK_THEME"] = theme_name
        set_key(str(ENV_PATH), "PEEK_THEME", theme_name)

    @classmethod
    def get_hotkey_copy(cls) -> str:
        """Hot key for stealth copying clean answer/code."""
        return os.environ.get("HOTKEY_COPY_ANSWER", cls.DEFAULT_HOTKEY_COPY).strip()

    @classmethod
    def get_api_key(cls) -> str:
        """Returns the configured Gemini API key from environment or .env."""
        # Check system env first, then loaded dotenv
        return os.environ.get("GEMINI_API_KEY", "").strip()

    @classmethod
    def set_api_key(cls, key: str) -> None:
        """Saves the API key to the .env file and sets current environment variable."""
        key = key.strip()
        os.environ["GEMINI_API_KEY"] = key
        set_key(str(ENV_PATH), "GEMINI_API_KEY", key)

    @classmethod
    def get_model(cls) -> str:
        """Returns the Gemini model to use for vision reasoning."""
        return os.environ.get("PEEK_MODEL", cls.DEFAULT_MODEL).strip()

    @classmethod
    def set_model(cls, model_name: str) -> None:
        """Saves chosen model to .env."""
        os.environ["PEEK_MODEL"] = model_name
        set_key(str(ENV_PATH), "PEEK_MODEL", model_name)

    @classmethod
    def get_hotkey_full(cls) -> str:
        """Hot key for full-screen peek."""
        return os.environ.get("HOTKEY_FULL_SCREEN", cls.DEFAULT_HOTKEY_FULL).strip()

    @classmethod
    def get_hotkey_snippet(cls) -> str:
        """Hot key for region snippet peek."""
        return os.environ.get("HOTKEY_SNIPPET", cls.DEFAULT_HOTKEY_SNIPPET).strip()

    @classmethod
    def get_hotkey_append(cls) -> str:
        """Hot key for appending next scrolled snapshot."""
        return os.environ.get("HOTKEY_APPEND", cls.DEFAULT_HOTKEY_APPEND).strip()

    @classmethod
    def is_configured(cls) -> bool:
        """Checks if a valid API key is present."""
        key = cls.get_api_key()
        return bool(key and len(key) > 10)
