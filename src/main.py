#!/usr/bin/env python3
"""
ChartPredictor - Trading Chart Analysis Desktop Application
Main application entry point
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QStyleFactory
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QIcon
from loguru import logger

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import MainWindow
from config.settings import AppSettings

class ChartPredictorApp:
    """Main application class for ChartPredictor"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.settings = AppSettings()
        
    def setup_logging(self):
        """Configure application logging"""
        log_level = "DEBUG" if self.settings.debug_mode else "INFO"
        logger.add(
            "logs/chartpredictor.log",
            rotation="10 MB",
            retention="1 week",
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        )
        logger.info("ChartPredictor application starting...")
        
    def setup_application(self):
        """Initialize PyQt6 application"""
        # Set application attributes before creating QApplication
        try:
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            # These attributes may not be available in newer Qt versions
            # High DPI scaling is automatic in Qt 6.0+
            pass
        
        self.app = QApplication(sys.argv)
        
        # Set application properties
        self.app.setApplicationName("ChartPredictor")
        self.app.setApplicationVersion("0.1.0")
        self.app.setOrganizationName("ChartPredictor Team")
        self.app.setOrganizationDomain("chartpredictor.com")
        
        # Set application icon
        icon_path = Path("resources/icons/app_icon.png")
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))
            
        # Apply application style
        self.apply_style()
        
    def apply_style(self):
        """Apply application styling and theme"""
        # Set a modern style
        available_styles = QStyleFactory.keys()
        if "Fusion" in available_styles:
            self.app.setStyle("Fusion")
            
        # Apply theme based on settings
        theme = self.settings.ui_config.theme
        if theme == "dark":
            self.apply_dark_theme()
        elif theme == "light":
            self.apply_light_theme()
        elif theme == "auto":
            # For now, default to dark for auto mode
            # Could be enhanced to detect system theme
            self.apply_dark_theme()
            
    def apply_dark_theme(self):
        """Apply dark theme styling"""
        dark_stylesheet = """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QMenuBar {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QMenuBar::item:selected {
            background-color: #5a5a5a;
        }
        QMenu {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #5a5a5a;
        }
        QMenu::item:selected {
            background-color: #5a5a5a;
        }
        QToolBar {
            background-color: #3c3c3c;
            border: none;
        }
        QStatusBar {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
        }
        QPushButton {
            background-color: #4a4a4a;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #5a5a5a;
        }
        QPushButton:pressed {
            background-color: #6a6a6a;
        }
        QTextEdit {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #5a5a5a;
        }
        QLineEdit {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            padding: 2px;
        }
        QComboBox {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            padding: 2px;
        }
        QComboBox::drop-down {
            background-color: #4a4a4a;
            border-left: 1px solid #5a5a5a;
        }
        QComboBox QAbstractItemView {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            selection-background-color: #4a4a4a;
            selection-color: #ffffff;
        }
        QComboBox QAbstractItemView::item {
            background-color: #2b2b2b;
            color: #ffffff;
            padding: 4px;
            border: none;
        }
        QComboBox QAbstractItemView::item:selected {
            background-color: #4a4a4a;
            color: #ffffff;
        }
        QComboBox QAbstractItemView::item:hover {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QGroupBox {
            color: #ffffff;
            border: 1px solid #5a5a5a;
            border-radius: 3px;
            margin-top: 1ex;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QProgressBar {
            border: 1px solid #5a5a5a;
            border-radius: 3px;
            text-align: center;
            background-color: #2b2b2b;
        }
        QProgressBar::chunk {
            background-color: #4a90e2;
            border-radius: 2px;
        }
        QMessageBox {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QMessageBox QLabel {
            color: #ffffff;
            background-color: transparent;
        }
        QMessageBox QPushButton {
            background-color: #4a4a4a;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            padding: 6px 12px;
            border-radius: 3px;
            min-width: 60px;
        }
        QMessageBox QPushButton:hover {
            background-color: #5a5a5a;
        }
        QMessageBox QPushButton:pressed {
            background-color: #6a6a6a;
        }
        QDialog {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QDialog QLabel {
            color: #ffffff;
        }
        QDialog QPushButton {
            background-color: #4a4a4a;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            padding: 6px 12px;
            border-radius: 3px;
            min-width: 60px;
        }
        QDialog QPushButton:hover {
            background-color: #5a5a5a;
        }
        QDialog QPushButton:pressed {
            background-color: #6a6a6a;
        }
        QTabWidget::pane {
            border: 1px solid #5a5a5a;
            background-color: #2b2b2b;
        }
        QTabBar::tab {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            padding: 6px 12px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #2b2b2b;
            border-bottom: 1px solid #2b2b2b;
        }
        QTabBar::tab:hover {
            background-color: #4a4a4a;
        }
        QSpinBox, QDoubleSpinBox {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            padding: 2px;
        }
        QSlider::groove:horizontal {
            border: 1px solid #5a5a5a;
            height: 6px;
            background-color: #3c3c3c;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background-color: #4a90e2;
            border: 1px solid #5a5a5a;
            width: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }
        QSlider::handle:horizontal:hover {
            background-color: #357abd;
        }
        QCheckBox {
            color: #ffffff;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #5a5a5a;
            background-color: #2b2b2b;
        }
        QCheckBox::indicator:checked {
            background-color: #4a90e2;
            border: 1px solid #357abd;
        }
        QAction {
            color: #ffffff;
        }
        QToolButton {
            background-color: #4a4a4a;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            padding: 4px;
            border-radius: 3px;
        }
        QToolButton:hover {
            background-color: #5a5a5a;
        }
        QToolButton:pressed {
            background-color: #6a6a6a;
        }
        QFormLayout QLabel {
            color: #ffffff;
        }
        """
        self.app.setStyleSheet(dark_stylesheet)
        
    def apply_light_theme(self):
        """Apply light theme styling"""
        light_stylesheet = """
        QMainWindow {
            background-color: #ffffff;
            color: #000000;
        }
        QMenuBar {
            background-color: #f0f0f0;
            color: #000000;
            border-bottom: 1px solid #d0d0d0;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        QMenuBar::item:selected {
            background-color: #e0e0e0;
        }
        QMenu {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
        }
        QMenu::item {
            padding: 4px 20px;
        }
        QMenu::item:selected {
            background-color: #e0e0e0;
        }
        QToolBar {
            background-color: #f0f0f0;
            border: none;
            border-bottom: 1px solid #d0d0d0;
        }
        QStatusBar {
            background-color: #f0f0f0;
            color: #000000;
            border-top: 1px solid #d0d0d0;
        }
        QLabel {
            color: #000000;
        }
        QPushButton {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #f0f0f0;
        }
        QPushButton:pressed {
            background-color: #e0e0e0;
        }
        QTextEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
        }
        QLineEdit {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            padding: 2px;
        }
        QComboBox {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            padding: 2px;
        }
        QComboBox::drop-down {
            background-color: #f0f0f0;
            border-left: 1px solid #d0d0d0;
        }
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            selection-background-color: #e0e0e0;
            selection-color: #000000;
        }
        QComboBox QAbstractItemView::item {
            background-color: #ffffff;
            color: #000000;
            padding: 4px;
            border: none;
        }
        QComboBox QAbstractItemView::item:selected {
            background-color: #e0e0e0;
            color: #000000;
        }
        QComboBox QAbstractItemView::item:hover {
            background-color: #f0f0f0;
            color: #000000;
        }
        QGroupBox {
            color: #000000;
            border: 1px solid #d0d0d0;
            border-radius: 3px;
            margin-top: 1ex;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QProgressBar {
            border: 1px solid #d0d0d0;
            border-radius: 3px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #4a90e2;
            border-radius: 2px;
        }
        QMessageBox {
            background-color: #ffffff;
            color: #000000;
        }
        QMessageBox QLabel {
            color: #000000;
            background-color: transparent;
        }
        QMessageBox QPushButton {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            padding: 6px 12px;
            border-radius: 3px;
            min-width: 60px;
        }
        QMessageBox QPushButton:hover {
            background-color: #f0f0f0;
        }
        QMessageBox QPushButton:pressed {
            background-color: #e0e0e0;
        }
        QDialog {
            background-color: #ffffff;
            color: #000000;
        }
        QDialog QLabel {
            color: #000000;
        }
        QDialog QPushButton {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            padding: 6px 12px;
            border-radius: 3px;
            min-width: 60px;
        }
        QDialog QPushButton:hover {
            background-color: #f0f0f0;
        }
        QDialog QPushButton:pressed {
            background-color: #e0e0e0;
        }
        QTabWidget::pane {
            border: 1px solid #d0d0d0;
            background-color: #ffffff;
        }
        QTabBar::tab {
            background-color: #f0f0f0;
            color: #000000;
            border: 1px solid #d0d0d0;
            padding: 6px 12px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom: 1px solid #ffffff;
        }
        QTabBar::tab:hover {
            background-color: #e8e8e8;
        }
        QSpinBox, QDoubleSpinBox {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            padding: 2px;
        }
        QSlider::groove:horizontal {
            border: 1px solid #d0d0d0;
            height: 6px;
            background-color: #f0f0f0;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background-color: #4a90e2;
            border: 1px solid #d0d0d0;
            width: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }
        QSlider::handle:horizontal:hover {
            background-color: #357abd;
        }
        QCheckBox {
            color: #000000;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #d0d0d0;
            background-color: #ffffff;
        }
        QCheckBox::indicator:checked {
            background-color: #4a90e2;
            border: 1px solid #357abd;
        }
        QAction {
            color: #000000;
        }
        QToolButton {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            padding: 4px;
            border-radius: 3px;
        }
        QToolButton:hover {
            background-color: #f0f0f0;
        }
        QToolButton:pressed {
            background-color: #e0e0e0;
        }
        QFormLayout QLabel {
            color: #000000;
        }
        """
        self.app.setStyleSheet(light_stylesheet)
        
    def create_directories(self):
        """Create necessary application directories"""
        directories = [
            "logs",
            "data/models",
            "data/patterns",
            "data/cache",
            "exports"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
    def run(self):
        """Run the application"""
        try:
            # Setup logging
            self.setup_logging()
            
            # Create necessary directories
            self.create_directories()
            
            # Setup Qt application
            self.setup_application()
            
            # Create and show main window
            self.main_window = MainWindow(self.settings)
            self.main_window.show()
            
            logger.info("Application initialized successfully")
            
            # Start event loop
            return self.app.exec()
            
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            if self.app:
                return 1
            return 1
            
        finally:
            logger.info("Application shutting down...")


def main():
    """Main entry point"""
    app = ChartPredictorApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())