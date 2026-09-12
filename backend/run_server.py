"""
Backend Server Runner for FastAPI.
Launches the Uvicorn server on configured or fallback available port (UTF-8 safe).
"""

import sys
import os
import socket

# Set UTF-8 encoding for standard output if available
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import uvicorn


def is_port_free(port: int, host: str = "127.0.0.1") -> bool:
    """Checks whether a port is currently free for binding on host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def find_free_port(preferred: int, host: str = "127.0.0.1", max_tries: int = 50) -> int:
    """Finds an available port starting from preferred."""
    for p in range(preferred, preferred + max_tries):
        if is_port_free(p, host):
            return p
    return preferred


if __name__ == "__main__":
    preferred_port = int(os.getenv("BACKEND_PORT", os.getenv("PORT", "8000")))
    host = os.getenv("HOST", "127.0.0.1")
    selected_port = find_free_port(preferred_port, host)
    if selected_port != preferred_port:
        print(f"[PORT INFO] Backend port {preferred_port} is already occupied. Selecting available port {selected_port}.")
    print(f"[INFO] Starting VFSTR AI Accreditation Agent FastAPI Backend on http://{host}:{selected_port} ...")
    uvicorn.run("backend.api:app", host=host, port=selected_port, log_level="info", reload=False)

