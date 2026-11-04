#!/usr/bin/env python3
"""Start SealSend on Windows, macOS or Linux.

Double-click start-windows.bat, start-mac.command or start-linux.sh (or run `python run.py`).
The first run creates a private Python environment in .venv and installs everything (needs internet once).
"""
import os
import socket
import subprocess
import sys
import threading
import venv
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
REQ = ROOT / "requirements-app.txt"


def venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def ensure_environment() -> None:
    if sys.version_info < (3, 10):
        print("SealSend needs Python 3.10 or newer. Download it from https://www.python.org/downloads/")
        input("Press Enter to close...")
        sys.exit(1)
    if os.environ.get("SEALSEND_NO_VENV") or Path(sys.prefix).resolve() == VENV.resolve():
        return
    if not venv_python().exists():
        print("First run: preparing SealSend (about 1-3 minutes, needs internet once)...")
        venv.EnvBuilder(with_pip=True).create(VENV)
    marker = VENV / ".installed"
    if not marker.exists() or marker.read_text() != REQ.read_text():
        print("Installing components...")
        subprocess.check_call([str(venv_python()), "-m", "pip", "install", "--disable-pip-version-check", "-q", "-r", str(REQ)])
        marker.write_text(REQ.read_text())
    sys.exit(subprocess.call([str(venv_python()), str(ROOT / "run.py"), *sys.argv[1:]]))


def free_port(start: int) -> int:
    for port in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise SystemExit(f"No free port between {start} and {start + 19}")


def main() -> None:
    ensure_environment()
    port = free_port(int(os.environ.get("SEALSEND_PORT", "8000")))
    os.environ["SEALSEND_PORT"] = str(port)
    sys.path.insert(0, str(ROOT))
    import uvicorn
    from sealsend import config

    local = f"http://localhost:{port}"
    print("\n  SealSend is running\n")
    print(f"  On this computer:      {local}")
    print(f"  Phone/iPad (same Wi-Fi): http://{config.lan_ip()}:{port}")
    print("\n  Keep this window open while you use SealSend. Close it (or press Ctrl+C) to stop.\n")
    if not os.environ.get("SEALSEND_NO_BROWSER"):
        threading.Timer(1.5, lambda: webbrowser.open(local)).start()
    uvicorn.run("sealsend.main:app", host="0.0.0.0", port=port, log_level="warning")


if __name__ == "__main__":  # required on Windows/macOS: worker processes re-import this file
    main()
