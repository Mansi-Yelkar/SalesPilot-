"""
run.py — One-click runner script for SalesPilot AI.
Simply click the Play (▶) button on the top right in VS Code!
"""

import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

# Ensure we use the virtual environment python/uvicorn
VENV_UVICORN = ROOT_DIR / "venv" / "Scripts" / "uvicorn.exe"

def main():
    print("=" * 60)
    print("🚀 Starting SalesPilot AI Server (Fortivex AI)...")
    print("👉 Open your browser at: http://localhost:8000")
    print("👉 Press Ctrl+C in this terminal to stop.")
    print("=" * 60)

    if VENV_UVICORN.exists():
        cmd = [str(VENV_UVICORN), "backend.main:app", "--port", "8000"]
    else:
        cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--port", "8000"]

    try:
        subprocess.run(cmd, cwd=str(ROOT_DIR))
    except KeyboardInterrupt:
        print("\n👋 SalesPilot AI Server stopped.")

if __name__ == "__main__":
    main()
