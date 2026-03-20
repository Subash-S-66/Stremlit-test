import sys
import os
import subprocess
import time
import webbrowser
from threading import Thread

def get_base_path():
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return base_path

def start_streamlit(app_path):
    # Set the command to run Streamlit
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"  # Run headless so it doesn't try to open browser from streamlit directly
    env["STREAMLIT_SERVER_PORT"] = "8501"

    # Call Streamlit module directly
    subprocess.call(
        [sys.executable, "-m", "streamlit", "run", app_path],
        env=env,
        cwd=os.path.dirname(app_path)
    )

if __name__ == "__main__":
    # Determine the path to app.py
    app_path = os.path.join(get_base_path(), "app.py")

    if not os.path.exists(app_path):
        print(f"Error: Could not find app.py at {app_path}")
        sys.exit(1)

    # Start the Streamlit server in a separate thread
    thread = Thread(target=start_streamlit, args=(app_path,))
    thread.daemon = True
    thread.start()

    # Wait a moment for the server to spin up
    print("Starting AI Question Paper Generator...")
    time.sleep(3)

    # Open the user's default web browser
    webbrowser.open("http://localhost:8501")

    # Keep the main thread alive so the Streamlit server continues to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        sys.exit(0)
