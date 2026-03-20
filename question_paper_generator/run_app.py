import sys
import os
import time
import socket
from threading import Thread

def get_base_path():
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return base_path

def wait_for_server(host: str, port: int, timeout: float = 20.0) -> bool:
    """Wait for the Streamlit server to accept connections."""
    end_time = time.time() + timeout
    while time.time() < end_time:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False

def acquire_single_instance_lock(port: int = 65432) -> socket.socket:
    """
    Prevent multiple instances (and multiple windows/tabs).
    Uses a localhost TCP port as a lock.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        s.listen(1)
        return s
    except OSError:
        print("Another instance is already running.")
        s.close()
        sys.exit(0)

if __name__ == "__main__":
    # Force pywebview to use Edge (avoids pythonnet/winforms dependency)
    os.environ.setdefault("PYWEBVIEW_GUI", "edgechromium")

    # Ensure only one instance runs
    _lock = acquire_single_instance_lock()

    # Import after setting PYWEBVIEW_GUI
    import webview

    # Allow file downloads in pywebview
    webview.settings["ALLOW_DOWNLOADS"] = True

    # Open a native desktop window using pywebview (Edge WebView2)
    window = webview.create_window(
        "AI Question Paper Generator",
        "https://question-paper-generator-subash.streamlit.app/",
        width=1200,
        height=800
    )

    webview.start(gui="edgechromium")

    # When the window closes, we exit
    print("Shutting down...")
    sys.exit(0)
