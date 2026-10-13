"""Helper script to enable or disable Windows Startup auto-launch and Desktop shortcut for PeekAI."""
import os
import sys
import subprocess
from pathlib import Path

# Project root directory
PROJECT_DIR = Path(__file__).resolve().parent.parent
VBS_PATH = PROJECT_DIR / "launch_silent.vbs"


def get_special_folder(folder_name: str) -> Path:
    """Gets exact Windows localized / redirected special folder path."""
    ps_cmd = f"[Environment]::GetFolderPath('{folder_name}')"
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, check=True)
    return Path(res.stdout.strip())


def create_silent_launcher():
    """Creates a VBScript launcher that starts PeekAI with zero console flicker."""
    vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{PROJECT_DIR}"
WshShell.Run """.venv\\Scripts\\pythonw.exe"" main.py", 0, False
'''
    VBS_PATH.write_text(vbs_content, encoding="utf-8")


def enable_autostart() -> bool:
    """Creates shortcut in Windows Startup directory."""
    create_silent_launcher()
    try:
        startup_dir = get_special_folder("Startup")
        shortcut_path = startup_dir / "PeekAI.lnk"
        ps_cmd = (
            f'$ws = New-Object -ComObject WScript.Shell; '
            f'$s = $ws.CreateShortcut("{shortcut_path}"); '
            f'$s.TargetPath = "wscript.exe"; '
            f'$s.Arguments = "`"{VBS_PATH}`""; '
            f'$s.WorkingDirectory = "{PROJECT_DIR}"; '
            f'$s.Description = "PeekAI Instant Screen Copilot"; '
            f'$s.Save()'
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Failed to enable autostart: {e}")
        return False


def disable_autostart() -> bool:
    """Removes shortcut from Windows Startup directory."""
    try:
        startup_dir = get_special_folder("Startup")
        shortcut_path = startup_dir / "PeekAI.lnk"
        if shortcut_path.exists():
            shortcut_path.unlink()
        return True
    except Exception as e:
        print(f"Failed to disable autostart: {e}")
        return False


def is_autostart_enabled() -> bool:
    try:
        startup_dir = get_special_folder("Startup")
        shortcut_path = startup_dir / "PeekAI.lnk"
        return shortcut_path.exists()
    except Exception:
        return False


def create_desktop_shortcut() -> bool:
    """Creates a shortcut on the Windows Desktop."""
    create_silent_launcher()
    try:
        desktop_dir = get_special_folder("Desktop")
        shortcut_path = desktop_dir / "PeekAI.lnk"
        icon_path = PROJECT_DIR / "assets" / "icon.ico"
        icon_arg = f'$s.IconLocation = "{icon_path},0"; ' if icon_path.exists() else ""
        ps_cmd = (
            f'$ws = New-Object -ComObject WScript.Shell; '
            f'$s = $ws.CreateShortcut("{shortcut_path}"); '
            f'$s.TargetPath = "{PROJECT_DIR}\\.venv\\Scripts\\pythonw.exe"; '
            f'$s.Arguments = "`"{PROJECT_DIR}\\main.py`""; '
            f'$s.WorkingDirectory = "{PROJECT_DIR}"; '
            f'{icon_arg}'
            f'$s.Description = "PeekAI Instant Screen Copilot"; '
            f'$s.Save()'
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Failed to create Desktop shortcut: {e}")
        return False


def create_start_menu_shortcut() -> bool:
    """Creates a shortcut in the Windows Start Menu Programs directory."""
    create_silent_launcher()
    try:
        programs_dir = get_special_folder("Programs")
        shortcut_path = programs_dir / "PeekAI.lnk"
        ps_cmd = (
            f'$ws = New-Object -ComObject WScript.Shell; '
            f'$s = $ws.CreateShortcut("{shortcut_path}"); '
            f'$s.TargetPath = "wscript.exe"; '
            f'$s.Arguments = "`"{VBS_PATH}`""; '
            f'$s.WorkingDirectory = "{PROJECT_DIR}"; '
            f'$s.Description = "PeekAI Instant Screen Copilot"; '
            f'$s.Save()'
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Failed to create Start Menu shortcut: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--disable":
        disable_autostart()
        print("Auto-start disabled.")
    elif len(sys.argv) > 1 and sys.argv[1] == "--desktop":
        if create_desktop_shortcut():
            print("Desktop shortcut created.")
    elif len(sys.argv) > 1 and sys.argv[1] == "--startmenu":
        if create_start_menu_shortcut():
            print("Start Menu shortcut created.")
    else:
        auto_ok = enable_autostart()
        desk_ok = create_desktop_shortcut()
        if auto_ok and desk_ok:
            print("[OK] Auto-start on Windows boot enabled & Desktop shortcut created successfully!")
        else:
            print("[WARNING] Setup finished with partial status:", auto_ok, desk_ok)
