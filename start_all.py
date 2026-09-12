"""
Combined Launcher for VFSTR AI Accreditation Academic Agent:
- Starts FastAPI REST API Backend (preferred port: 8000, dynamic fallback)
- Starts Streamlit Web Application (preferred port: 8501, dynamic fallback)
- Reuses already-healthy active backend to avoid duplicate processes
- Dynamically passes backend port and API URL to the frontend environment
- Safely manages and terminates child processes on Windows exit (Ctrl+C / SIGINT / SIGTERM)
- Automatically launches the web application in the default browser
"""

import subprocess
import time
import sys
import os
import socket
import json
import urllib.request
import urllib.error
import webbrowser
import threading
import atexit
import signal
from typing import List, Optional, Tuple

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Track only processes started by THIS launcher instance for safe cleanup
_CHILD_PROCESSES: List[subprocess.Popen] = []
_SHUTDOWN_IN_PROGRESS = False


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """
    Checks whether a local TCP port is available for binding on Windows / Linux / macOS.
    Returns True if port is free to bind, False if occupied.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.4)
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def check_existing_backend_health(port: int, host: str = "127.0.0.1") -> bool:
    """
    Checks if an already-running process on the port is our own VFSTR Accreditation Agent backend.
    Returns True if healthy backend is responding, False otherwise.
    """
    url = f"http://{host}:{port}/api/health"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VFSTR-Launcher-Check"})
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                if "VFSTR AI Accreditation Agent" in data.get("service", "") or data.get("status") == "online":
                    return True
    except Exception:
        pass
    return False


def find_available_port(
    preferred_port: int,
    service_name: str = "Service",
    host: str = "127.0.0.1",
    max_attempts: int = 50
) -> int:
    """
    Finds the first available port starting from preferred_port.
    Logs a descriptive message if a port conflict is encountered.
    """
    if is_port_available(preferred_port, host):
        return preferred_port

    for candidate in range(preferred_port + 1, preferred_port + max_attempts):
        if is_port_available(candidate, host):
            print(f"[PORT NOTICE] {service_name} port {preferred_port} is already occupied. Selecting available port {candidate}.")
            return candidate

    print(f"[PORT WARNING] Could not find free port in range {preferred_port}-{preferred_port+max_attempts}. Using {preferred_port}.")
    return preferred_port


def cleanup_child_processes(signum=None, frame=None):
    """
    Gracefully and safely terminates ONLY child processes spawned by this launcher.
    Never kills unrelated system or Python processes.
    """
    global _SHUTDOWN_IN_PROGRESS
    if _SHUTDOWN_IN_PROGRESS:
        return
    _SHUTDOWN_IN_PROGRESS = True

    print("\n[INFO] Gracefully shutting down application services...")
    for proc in _CHILD_PROCESSES:
        if proc and proc.poll() is None:
            try:
                proc.terminate()
            except Exception:
                pass

    # Allow grace period for clean termination
    time.sleep(1.0)

    for proc in _CHILD_PROCESSES:
        if proc and proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass

    print("[OK] All launcher child processes terminated.")


def open_browser_delayed(url: str, delay: float = 2.5):
    """Opens the application in the system's default browser after server initializes."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    # Register safe process cleanup hooks
    atexit.register(cleanup_child_processes)
    try:
        signal.signal(signal.SIGINT, cleanup_child_processes)
        signal.signal(signal.SIGTERM, cleanup_child_processes)
    except Exception:
        pass

    project_dir = os.path.dirname(os.path.abspath(__file__))
    host = os.getenv("HOST", "127.0.0.1")

    # Read preferred ports from environment or defaults
    preferred_backend_port = int(os.getenv("BACKEND_PORT", os.getenv("PORT", "8000")))
    preferred_frontend_port = int(os.getenv("STREAMLIT_SERVER_PORT", os.getenv("FRONTEND_PORT", "8501")))

    print("=" * 78)
    print("  🏛️  VIGNAN UNIVERSITY (VFSTR) AI ACCREDITATION ACADEMIC AGENT")
    print("=" * 78)

    # 1. Evaluate Backend Port & Duplicate Protection
    backend_port = preferred_backend_port
    backend_proc: Optional[subprocess.Popen] = None
    existing_backend_found = False

    if not is_port_available(preferred_backend_port, host):
        # Check if it is an existing active VFSTR backend instance
        if check_existing_backend_health(preferred_backend_port, host):
            print(f"[INFO] Existing VFSTR AI Accreditation Backend detected online on http://{host}:{preferred_backend_port}.")
            print(f"[INFO] Reusing active backend service at http://{host}:{preferred_backend_port}/api/health.")
            existing_backend_found = True
            backend_port = preferred_backend_port
        else:
            # Port is occupied by another application, select next free port
            backend_port = find_available_port(preferred_backend_port + 1, "Backend", host)

    if not existing_backend_found:
        print(f"[1/2] Launching FastAPI REST API Backend on http://{host}:{backend_port} ...")
        
        backend_env = os.environ.copy()
        backend_env["PYTHONIOENCODING"] = "utf-8"
        backend_env["BACKEND_PORT"] = str(backend_port)
        backend_env["HOST"] = host

        backend_proc = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn", "backend.api:app",
                "--host", host,
                "--port", str(backend_port),
                "--reload"
            ],
            cwd=project_dir,
            env=backend_env
        )
        _CHILD_PROCESSES.append(backend_proc)

        # Wait briefly for backend initialization
        for _ in range(10):
            time.sleep(0.3)
            if check_existing_backend_health(backend_port, host):
                break

        print(f"[OK] Backend API is live on http://{host}:{backend_port}/api/health")
        print(f"[OK] Interactive Swagger Docs: http://{host}:{backend_port}/docs")

    # 2. Evaluate Frontend Port
    frontend_port = find_available_port(preferred_frontend_port, "Frontend", host)
    frontend_url = f"http://localhost:{frontend_port}"

    print(f"[2/2] Launching Streamlit Web UI on {frontend_url} ...")

    # Configure child environment for frontend so it connects to the exact backend port
    frontend_env = os.environ.copy()
    frontend_env["PYTHONIOENCODING"] = "utf-8"
    frontend_env["BACKEND_PORT"] = str(backend_port)
    frontend_env["BACKEND_API_URL"] = f"http://{host}:{backend_port}"
    frontend_env["STREAMLIT_SERVER_PORT"] = str(frontend_port)

    # Launch browser automatically in background
    threading.Thread(target=open_browser_delayed, args=(frontend_url, 2.5), daemon=True).start()

    try:
        frontend_proc = subprocess.Popen(
            [
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", str(frontend_port),
                "--server.headless", "false"
            ],
            cwd=project_dir,
            env=frontend_env
        )
        _CHILD_PROCESSES.append(frontend_proc)

        # Keep launcher waiting for frontend process
        frontend_proc.wait()

    except KeyboardInterrupt:
        pass
    finally:
        cleanup_child_processes()


if __name__ == "__main__":
    main()
