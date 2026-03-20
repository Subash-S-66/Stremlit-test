# 🎓 AI Question Paper Generator

A production-ready application that generates professional, university-level question papers using the Google Gemini AI. It allows custom point distribution, automated mix difficulty splitting, and direct PDF downloads.

## 🚀 Setup & Run (Development)

1. **Clone & Navigate to directory:**
   ```bash
   cd question_paper_generator
   ```

2. **Install Requirements:**
   Make sure you have Python 3.9+ installed.
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Copy the example environment file and insert your API key:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and replace `your_api_key_here` with your actual Google Gemini API Key.

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
   The application will automatically open in your default web browser (usually at `http://localhost:8501`).

---

## 📦 Build Windows Executable (.exe)

To package this Streamlit application into a standalone Windows `.exe` that behaves like a real application (complete with a desktop icon), follow these steps **on a Windows machine**:

### Prerequisites
- Python installed and added to your `PATH`.
- A `.ico` icon file for your app (place it in the `assets/` folder, e.g., `assets/icon.ico`). If you don't have one, PyInstaller will use a default icon.

### Build Steps

1. **Install Dependencies (if not already done):**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Run PyInstaller:**
   Streamlit apps require special handling when packaged. We use a dedicated entry script (`run_app.py`) to launch Streamlit from within the executable.

   Run this exact command from the root of the project:
   ```cmd
   pyinstaller --noconfirm --onedir --windowed --icon="assets/icon.ico" --add-data "app.py;." --add-data "config.py;." --add-data "generator.py;." --add-data "validator.py;." --add-data "pdf_builder.py;." --add-data "utils.py;." --add-data ".env;." --add-data "assets;assets" --hidden-import "streamlit" --hidden-import "google.generativeai" --hidden-import "reportlab" --hidden-import "dotenv" run_app.py
   ```
   *(Note: If you don't have an `icon.ico`, remove the `--icon="assets/icon.ico"` flag).*

3. **Add Streamlit Internal Files (Crucial Step for Streamlit + PyInstaller):**
   PyInstaller often misses Streamlit's frontend assets and internal configuration. You must copy the Streamlit module folder into your build directory.

   Find your Python's `site-packages/streamlit` folder (you can find the path by running `python -c "import streamlit, os; print(os.path.dirname(streamlit.__file__))"`).

   Copy that entire `streamlit` folder into `dist/run_app/_internal/` (or `dist/run_app/` depending on your PyInstaller version).

4. **Run Your App:**
   Navigate to the `dist/run_app/` folder. You will find `run_app.exe`. Double click it! A local server will start in the background, and it will automatically open your default web browser to the application, acting like a desktop program.

5. **Create Desktop Shortcut:**
   Right-click `run_app.exe`, select "Create shortcut", and drag that shortcut to your Desktop. You can rename the shortcut to "AI Question Paper Generator".
