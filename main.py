# main.py
import sys
import logging
import asyncio
import shutil
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
import ctypes

# Try to fix COM initialization error on Windows
if sys.platform == 'win32':
    try:
        ctypes.OleDLL('ole32.dll').CoInitialize(None)
    except Exception:
        pass

from electroninja.config.logging_config import setup_logging
from electroninja.config.settings import Config
from electroninja.ui.main_window import MainWindow
from electroninja.ui.styles import STYLE_SHEET, setup_fonts

def main():
    """Main entry point for the application"""
    setup_logging()
    logger = logging.getLogger('electroninja')
    logger.info("ElectroNinja starting...")

    # Create Qt application
    app = QApplication(sys.argv)
    
    # Setup custom fonts and stylesheet
    setup_fonts(app)
    app.setStyleSheet(STYLE_SHEET)
    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)
    
    # Initialize configuration
    config = Config()
    config.ensure_directories()

    # Create and show main window; store reference to avoid GC.
    window = MainWindow()
    window.show()
    
    logger.info("ElectroNinja UI initialized and ready")
    return app, window


if __name__ == "__main__":
    # Keep a reference to the window so it isn't garbage-collected.
    app, window = main()
    try:
        from qasync import QEventLoop
    except ImportError:
        raise ImportError("Please install qasync: pip install qasync")
    
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    with loop:
        loop.run_forever()
