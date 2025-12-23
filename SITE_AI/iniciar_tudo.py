import os
import sys
import subprocess
import time
import venv
import ctypes
import webbrowser
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent
AI_DIR = Path(r"C:\Users\AMD\Desktop\IA\IA_BRENO")
VENV_DIR = SITE_DIR / ".venv"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_if_needed():
    if not is_admin():
        params = f'"{__file__}"'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit(0)

def ensure_venv():
    if not VENV_DIR.exists():
        venv.EnvBuilder(with_pip=True).create(str(VENV_DIR))
    py = VENV_DIR / "Scripts" / "python.exe"
    return str(py)

def pip_install(py, args):
    subprocess.check_call([py, "-m", "pip", "install"] + args)

def install_dependencies(py):
    subprocess.check_call([py, "-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools"])
    req_site = SITE_DIR / "requirements.txt"
    if req_site.exists():
        subprocess.check_call([py, "-m", "pip", "install", "-r", str(req_site)])
    else:
        pip_install(py, ["flask", "openai", "duckduckgo-search", "requests", "beautifulsoup4", "colorama"])
    req_ai = AI_DIR / "requirements.txt"
    if req_ai.exists():
        subprocess.check_call([py, "-m", "pip", "install", "-r", str(req_ai)])

def start_server(py):
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    return subprocess.Popen([py, str(SITE_DIR / "app.py")], cwd=str(SITE_DIR), env=env)

def wait_server(url="http://127.0.0.1:5000/", timeout=60):
    import urllib.request
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url) as r:
                if r.status == 200:
                    return True
        except:
            time.sleep(1)
    return False

def main():
    elevate_if_needed()
    py = ensure_venv()
    install_dependencies(py)
    p = start_server(py)
    ok = wait_server()
    if ok:
        webbrowser.open("http://127.0.0.1:5000/")
        print("Site iniciado em http://127.0.0.1:5000/")
    else:
        print("Falha ao iniciar o site.")
    p.wait()

if __name__ == "__main__":
    main()
