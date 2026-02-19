"""
Student Performance Analysis & Prediction System
================================================
Entry point for the application - launches the Streamlit dashboard
"""

import os
import sys
import subprocess

def setup_directories():
    """Create necessary project directories"""
    directories = ["data", "models", "reports", "reports/charts", "exports"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    print("=" * 70)
    print("     STUDENT PERFORMANCE ANALYSIS & PREDICTION SYSTEM")
    print("=" * 70)
    print()
    print("🚀 Launching Dashboard...")
    print("   → http://localhost:8501")
    print("   → Press Ctrl+C to stop")
    print("-" * 70)
    
    setup_directories()
    subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])

if __name__ == "__main__":
    try:
        import streamlit
    except ImportError:
        print("❌ Please install: pip install -r requirements.txt")
        sys.exit(1)
    main()