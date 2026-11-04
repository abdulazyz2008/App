#!/usr/bin/env python3
"""Start SealSend on Windows, macOS or Linux.

Double-click start-windows.bat, start-mac.command or start-linux.sh (or run `python run.py`).
The first run creates a private Python environment in .venv and installs everything (needs internet once).
"""
import getpass
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tarfile
import threading
import time
import urllib.request
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


# ---------------------------------------------------------------- free public link (Cloudflare Quick Tunnel)
TUNNEL_ASSETS = {
    ("windows", "amd64"): "cloudflared-windows-amd64.exe", ("windows", "x86_64"): "cloudflared-windows-amd64.exe",
    ("windows", "arm64"): "cloudflared-windows-amd64.exe",  # runs under Windows-on-ARM emulation
    ("darwin", "arm64"): "cloudflared-darwin-arm64.tgz", ("darwin", "x86_64"): "cloudflared-darwin-amd64.tgz",
    ("linux", "x86_64"): "cloudflared-linux-amd64", ("linux", "amd64"): "cloudflared-linux-amd64",
    ("linux", "aarch64"): "cloudflared-linux-arm64", ("linux", "arm64"): "cloudflared-linux-arm64",
}


def _download(url: str, dest: Path) -> None:
    try:
        with urllib.request.urlopen(url, timeout=120) as r, open(dest, "wb") as f:
            shutil.copyfileobj(r, f)
    except Exception:  # e.g. missing SSL certificates on a fresh macOS Python: fall back to the system curl
        subprocess.check_call(["curl", "-fsSL", "-o", str(dest), url])


def get_cloudflared() -> str:
    found = shutil.which("cloudflared")
    if found:
        return found
    key = (platform.system().lower(), platform.machine().lower())
    asset = TUNNEL_ASSETS.get(key)
    if not asset:
        raise SystemExit(f"Online mode isn't available for {key[0]} on {key[1]}. Use the normal start file instead.")
    tools = ROOT / ".tools"
    tools.mkdir(exist_ok=True)
    exe = tools / ("cloudflared.exe" if key[0] == "windows" else "cloudflared")
    if not exe.exists():
        print("First online start: downloading Cloudflare's free tunnel tool (20-55 MB, once)...")
        url = f"https://github.com/cloudflare/cloudflared/releases/latest/download/{asset}"
        if asset.endswith(".tgz"):
            tgz = tools / asset
            _download(url, tgz)
            with tarfile.open(tgz) as t:
                member = next(m for m in t.getmembers() if m.name.endswith("cloudflared"))
                member.name = "cloudflared"
                t.extract(member, tools)
            tgz.unlink()
        else:
            _download(url, exe)
        exe.chmod(0o755)
    return str(exe)


def start_tunnel(port: int) -> tuple[subprocess.Popen, str]:
    proc = subprocess.Popen([get_cloudflared(), "tunnel", "--no-autoupdate", "--url", f"http://localhost:{port}"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    found: list[str] = []

    def reader():
        for line in proc.stdout:  # keep draining so the tunnel never blocks on a full pipe
            m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", line)
            if m and not found:
                found.append(m.group(0))

    threading.Thread(target=reader, daemon=True).start()
    deadline = time.time() + 90
    while not found and time.time() < deadline and proc.poll() is None:
        time.sleep(0.3)
    if not found:
        proc.terminate()
        raise SystemExit("Couldn't open the public link (no internet, or Cloudflare is busy). Try again in a minute, "
                         "or use the normal start file.")
    return proc, found[0]


def ensure_password() -> None:
    from sealsend import settings
    if settings.admin_configured():
        return
    print("\nYour link will be public, so set a password first (8+ characters).")
    while True:
        a = getpass.getpass("  New password: ")
        b = getpass.getpass("  Repeat it:    ")
        if len(a) >= 8 and a == b:
            settings.set_admin_password(a)
            print("  Password saved.\n")
            return
        print("  Passwords must match and be at least 8 characters. Try again.")


def main() -> None:
    ensure_environment()
    online = "--online" in sys.argv
    port = free_port(int(os.environ.get("SEALSEND_PORT", "8000")))
    os.environ["SEALSEND_PORT"] = str(port)
    sys.path.insert(0, str(ROOT))
    tunnel = None
    if online:
        tunnel, public = start_tunnel(port)
        os.environ["SEALSEND_HOSTED_URL"] = public  # links and QR codes use the public address
        os.environ["SEALSEND_TEMPORARY_URL"] = "1"
    import uvicorn
    from sealsend import config

    local = f"http://localhost:{port}"
    if online:
        ensure_password()
        print("\n  SealSend is ONLINE\n")
        print(f"  Your link (works on any device, anywhere):\n\n      {public}\n")
        print("  The link stays the same until you close this window. Next time you start, you get a new link.")
        print("  Keep this computer on and this window open while people use it.\n")
    else:
        print("\n  SealSend is running\n")
        print(f"  On this computer:      {local}")
        print(f"  Phone/iPad (same Wi-Fi): http://{config.lan_ip()}:{port}")
        print("\n  Keep this window open while you use SealSend. Close it (or press Ctrl+C) to stop.\n")
    if not os.environ.get("SEALSEND_NO_BROWSER"):
        threading.Timer(1.5, lambda: webbrowser.open(public if online else local)).start()
    try:
        uvicorn.run("sealsend.main:app", host="127.0.0.1" if online else "0.0.0.0", port=port, log_level="warning",
                    proxy_headers=True, forwarded_allow_ips="127.0.0.1")
    finally:
        if tunnel:
            tunnel.terminate()


if __name__ == "__main__":  # required on Windows/macOS: worker processes re-import this file
    main()
