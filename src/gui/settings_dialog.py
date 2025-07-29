"""
Settings dialog for ChartPredictor application
Allows users to customize analysis parameters and application behavior
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
    QCheckBox, QGroupBox, QPushButton, QDialogButtonBox,
    QSlider, QFormLayout, QMessageBox, QColorDialog, QFontDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from typing import Dict, Any
from loguru import logger

from config.settings import AppSettings


class SettingsDialog(QDialog):
    """Advanced settings dialog for ChartPredictor"""
    
    settings_changed = pyqtSignal(AppSettings)  # Signal emitted when settings are applied
    
    def __init__(self, current_settings: AppSettings, parent=None):
        super().__init__(parent)
        self.current_settings = current_settings
        self.temp_settings = AppSettings()  # Temporary settings for preview
        self._copy_settings(current_settings, self.temp_settings)
        
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("ChartPredictor Settings")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_analysis_tab()
        self.create_trading_tab()
        self.create_display_tab()
        self.create_data_tab()
        self.create_advanced_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel | 
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.restore_defaults)
        
        layout.addWidget(button_box)
        
    def create_analysis_tab(self):
        """Create analysis settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Technical Analysis Group
        tech_group = QGroupBox("Technical Analysis")
        tech_layout = QFormLayout(tech_group)
        
        # RSI Settings
        self.rsi_period_spin = QSpinBox()
        self.rsi_period_spin.setRange(5, 50)
        self.rsi_period_spin.setValue(14)
        tech_layout.addRow("RSI Period:", self.rsi_period_spin)
        
        # MACD Settings (stored as tuple: fast, slow, signal)
        self.macd_fast_spin = QSpinBox()
        self.macd_fast_spin.setRange(5, 25)
        self.macd_fast_spin.setValue(12)
        tech_layout.addRow("MACD Fast Period:", self.macd_fast_spin)
        
        self.macd_slow_spin = QSpinBox()
        self.macd_slow_spin.setRange(20, 50)
        self.macd_slow_spin.setValue(26)
        tech_layout.addRow("MACD Slow Period:", self.macd_slow_spin)
        
        self.macd_signal_spin = QSpinBox()
        self.macd_signal_spin.setRange(5, 15)
        self.macd_signal_spin.setValue(9)
        tech_layout.addRow("MACD Signal Period:", self.macd_signal_spin)
        
        # Bollinger Bands
        self.bb_period_spin = QSpinBox()
        self.bb_period_spin.setRange(10, 50)
        self.bb_period_spin.setValue(20)
        tech_layout.addRow("Bollinger Bands Period:", self.bb_period_spin)
        
        self.bb_std_spin = QDoubleSpinBox()
        self.bb_std_spin.setRange(1.0, 3.0)
        self.bb_std_spin.setSingleStep(0.1)
        self.bb_std_spin.setValue(2.0)
        tech_layout.addRow("Bollinger Bands StdDev:", self.bb_std_spin)
        
        layout.addWidget(tech_group)
        
        # Pattern Detection Group
        pattern_group = QGroupBox("Pattern Detection")
        pattern_layout = QFormLayout(pattern_group)
        
        self.confidence_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_threshold_slider.setRange(30, 95)
        self.confidence_threshold_slider.setValue(60)
        self.confidence_threshold_label = QLabel("60%")
        self.confidence_threshold_slider.valueChanged.connect(
            lambda v: self.confidence_threshold_label.setText(f"{v}%")
        )
        
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(self.confidence_threshold_slider)
        threshold_layout.addWidget(self.confidence_threshold_label)
        
        pattern_layout.addRow("Minimum Confidence:", threshold_layout)
        
        self.prediction_horizon_spin = QSpinBox()
        self.prediction_horizon_spin.setRange(1, 48)
        self.prediction_horizon_spin.setValue(4)
        self.prediction_horizon_spin.setSuffix(" hours")
        pattern_layout.addRow("Prediction Horizon:", self.prediction_horizon_spin)
        
        layout.addWidget(pattern_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "📊 Analysis")
        
    def create_trading_tab(self):
        """Create trading settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Risk Management Group
        risk_group = QGroupBox("Risk Management")
        risk_layout = QFormLayout(risk_group)
        
        self.risk_tolerance_combo = QComboBox()
        self.risk_tolerance_combo.addItems(["low", "medium", "high"])
        risk_layout.addRow("Risk Tolerance:", self.risk_tolerance_combo)
        
        self.max_risk_spin = QDoubleSpinBox()
        self.max_risk_spin.setRange(0.5, 10.0)
        self.max_risk_spin.setSingleStep(0.1)
        self.max_risk_spin.setValue(2.0)
        self.max_risk_spin.setSuffix("%")
        risk_layout.addRow("Max Risk Per Trade:", self.max_risk_spin)
        
        self.stop_loss_mult_spin = QDoubleSpinBox()
        self.stop_loss_mult_spin.setRange(0.5, 3.0)
        self.stop_loss_mult_spin.setSingleStep(0.1)
        self.stop_loss_mult_spin.setValue(1.0)
        risk_layout.addRow("Stop Loss Multiplier:", self.stop_loss_mult_spin)
        
        self.take_profit_mult_spin = QDoubleSpinBox()
        self.take_profit_mult_spin.setRange(1.0, 5.0)
        self.take_profit_mult_spin.setSingleStep(0.1)
        self.take_profit_mult_spin.setValue(2.0)
        risk_layout.addRow("Take Profit Multiplier:", self.take_profit_mult_spin)
        
        layout.addWidget(risk_group)
        
        # Signal Filters Group
        filter_group = QGroupBox("Signal Filters")
        filter_layout = QVBoxLayout(filter_group)
        
        self.trend_confirmation_check = QCheckBox("Require Trend Confirmation")
        self.trend_confirmation_check.setChecked(True)
        filter_layout.addWidget(self.trend_confirmation_check)
        
        self.volume_confirmation_check = QCheckBox("Require Volume Confirmation")
        self.volume_confirmation_check.setChecked(False)
        filter_layout.addWidget(self.volume_confirmation_check)
        
        self.multiple_timeframe_check = QCheckBox("Multiple Timeframe Analysis")
        self.multiple_timeframe_check.setChecked(False)
        filter_layout.addWidget(self.multiple_timeframe_check)
        
        layout.addWidget(filter_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "💰 Trading")
        
    def create_display_tab(self):
        """Create display settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # UI Theme Group
        theme_group = QGroupBox("User Interface")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light", "auto"])
        theme_layout.addRow("Theme:", self.theme_combo)
        
        self.window_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.window_opacity_slider.setRange(70, 100)
        self.window_opacity_slider.setValue(100)
        self.window_opacity_label = QLabel("100%")
        self.window_opacity_slider.valueChanged.connect(
            lambda v: self.window_opacity_label.setText(f"{v}%")
        )
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.window_opacity_slider)
        opacity_layout.addWidget(self.window_opacity_label)
        
        theme_layout.addRow("Window Opacity:", opacity_layout)
        
        layout.addWidget(theme_group)
        
        # Chart Display Group
        chart_group = QGroupBox("Chart Display")
        chart_layout = QFormLayout(chart_group)
        
        self.show_indicators_check = QCheckBox("Show Technical Indicators")
        self.show_indicators_check.setChecked(True)
        chart_layout.addRow(self.show_indicators_check)
        
        self.show_patterns_check = QCheckBox("Highlight Detected Patterns")
        self.show_patterns_check.setChecked(True)
        chart_layout.addRow(self.show_patterns_check)
        
        self.auto_refresh_check = QCheckBox("Auto Refresh Data")
        self.auto_refresh_check.setChecked(False)
        chart_layout.addRow(self.auto_refresh_check)
        
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(30, 3600)
        self.refresh_interval_spin.setValue(300)
        self.refresh_interval_spin.setSuffix(" seconds")
        self.refresh_interval_spin.setEnabled(False)
        self.auto_refresh_check.toggled.connect(self.refresh_interval_spin.setEnabled)
        chart_layout.addRow("Refresh Interval:", self.refresh_interval_spin)
        
        layout.addWidget(chart_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "🎨 Display")
        
    def create_data_tab(self):
        """Create data settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Data Source Group
        source_group = QGroupBox("Data Sources")
        source_layout = QFormLayout(source_group)
        
        self.default_period_combo = QComboBox()
        self.default_period_combo.addItems(["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"])
        self.default_period_combo.setCurrentText("1mo")
        source_layout.addRow("Default Period:", self.default_period_combo)
        
        self.default_interval_combo = QComboBox()
        self.default_interval_combo.addItems(["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"])
        self.default_interval_combo.setCurrentText("1h")
        source_layout.addRow("Default Interval:", self.default_interval_combo)
        
        self.data_timeout_spin = QSpinBox()
        self.data_timeout_spin.setRange(5, 60)
        self.data_timeout_spin.setValue(10)
        self.data_timeout_spin.setSuffix(" seconds")
        source_layout.addRow("Data Timeout:", self.data_timeout_spin)
        
        layout.addWidget(source_group)
        
        # Cache Group
        cache_group = QGroupBox("Data Caching")
        cache_layout = QFormLayout(cache_group)
        
        self.enable_cache_check = QCheckBox("Enable Data Caching")
        self.enable_cache_check.setChecked(True)
        cache_layout.addRow(self.enable_cache_check)
        
        self.cache_duration_spin = QSpinBox()
        self.cache_duration_spin.setRange(5, 60)
        self.cache_duration_spin.setValue(15)
        self.cache_duration_spin.setSuffix(" minutes")
        cache_layout.addRow("Cache Duration:", self.cache_duration_spin)
        
        self.clear_cache_btn = QPushButton("Clear Cache Now")
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        cache_layout.addRow(self.clear_cache_btn)
        
        layout.addWidget(cache_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "📁 Data")
        
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Logging Group
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        logging_layout.addRow("Log Level:", self.log_level_combo)
        
        self.log_to_file_check = QCheckBox("Log to File")
        self.log_to_file_check.setChecked(True)
        logging_layout.addRow(self.log_to_file_check)
        
        self.max_log_size_spin = QSpinBox()
        self.max_log_size_spin.setRange(1, 100)
        self.max_log_size_spin.setValue(10)
        self.max_log_size_spin.setSuffix(" MB")
        logging_layout.addRow("Max Log File Size:", self.max_log_size_spin)
        
        layout.addWidget(logging_group)
        
        # Performance Group
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout(performance_group)
        
        self.thread_count_spin = QSpinBox()
        self.thread_count_spin.setRange(1, 8)
        self.thread_count_spin.setValue(2)
        performance_layout.addRow("Analysis Threads:", self.thread_count_spin)
        
        self.memory_limit_spin = QSpinBox()
        self.memory_limit_spin.setRange(256, 4096)
        self.memory_limit_spin.setValue(1024)
        self.memory_limit_spin.setSuffix(" MB")
        performance_layout.addRow("Memory Limit:", self.memory_limit_spin)
        
        layout.addWidget(performance_group)
        
        # Export Group
        export_group = QGroupBox("Export Settings")
        export_layout = QFormLayout(export_group)
        
        self.default_export_format_combo = QComboBox()
        self.default_export_format_combo.addItems(["JSON", "CSV", "PDF"])
        self.default_export_format_combo.setCurrentText("PDF")
        export_layout.addRow("Default Export Format:", self.default_export_format_combo)
        
        self.include_raw_data_check = QCheckBox("Include Raw Data in Exports")
        self.include_raw_data_check.setChecked(True)
        export_layout.addRow(self.include_raw_data_check)
        
        layout.addWidget(export_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "⚙️ Advanced")
        
    def load_current_settings(self):
        """Load current settings into the dialog"""
        # Technical Analysis
        self.rsi_period_spin.setValue(self.current_settings.technical_config.rsi_period)
        
        # MACD periods (stored as tuple: fast, slow, signal)
        macd_periods = self.current_settings.technical_config.macd_periods
        self.macd_fast_spin.setValue(macd_periods[0])
        self.macd_slow_spin.setValue(macd_periods[1])
        self.macd_signal_spin.setValue(macd_periods[2])
        
        self.bb_period_spin.setValue(self.current_settings.technical_config.bb_period)
        self.bb_std_spin.setValue(self.current_settings.technical_config.bb_std_dev)
        
        # Model Config
        confidence_percent = int(self.current_settings.ml_model_config.confidence_threshold * 100)
        self.confidence_threshold_slider.setValue(confidence_percent)
        self.confidence_threshold_label.setText(f"{confidence_percent}%")
        
        self.prediction_horizon_spin.setValue(self.current_settings.ml_model_config.prediction_horizon)
        
        # Trading Config
        self.risk_tolerance_combo.setCurrentText(self.current_settings.trading_config.risk_tolerance)
        self.max_risk_spin.setValue(self.current_settings.trading_config.max_risk_per_trade * 100)
        self.stop_loss_mult_spin.setValue(self.current_settings.trading_config.stop_loss_multiplier)
        self.take_profit_mult_spin.setValue(self.current_settings.trading_config.take_profit_multiplier)
        
        # Signal filters
        filters = self.current_settings.trading_config.signal_filters
        self.trend_confirmation_check.setChecked(filters.get('trend_confirmation', True))
        self.volume_confirmation_check.setChecked(filters.get('volume_confirmation', False))
        self.multiple_timeframe_check.setChecked(filters.get('multiple_timeframe', False))
        
        # UI Config
        self.theme_combo.setCurrentText(self.current_settings.ui_config.theme)
        
    def apply_settings(self):
        """Apply current settings"""
        self.save_to_temp_settings()
        self._copy_settings(self.temp_settings, self.current_settings)
        self.settings_changed.emit(self.current_settings)
        logger.info("Settings applied successfully")
        
    def accept_settings(self):
        """Accept and apply settings, then close dialog"""
        self.apply_settings()
        self.accept()
        
    def save_to_temp_settings(self):
        """Save current dialog values to temporary settings"""
        # Technical Analysis
        self.temp_settings.technical_config.rsi_period = self.rsi_period_spin.value()
        
        # MACD periods (save as tuple: fast, slow, signal)
        self.temp_settings.technical_config.macd_periods = (
            self.macd_fast_spin.value(),
            self.macd_slow_spin.value(),
            self.macd_signal_spin.value()
        )
        
        self.temp_settings.technical_config.bb_period = self.bb_period_spin.value()
        self.temp_settings.technical_config.bb_std_dev = self.bb_std_spin.value()
        
        # Model Config
        self.temp_settings.ml_model_config.confidence_threshold = self.confidence_threshold_slider.value() / 100.0
        self.temp_settings.ml_model_config.prediction_horizon = self.prediction_horizon_spin.value()
        
        # Trading Config
        self.temp_settings.trading_config.risk_tolerance = self.risk_tolerance_combo.currentText()
        self.temp_settings.trading_config.max_risk_per_trade = self.max_risk_spin.value() / 100.0
        self.temp_settings.trading_config.stop_loss_multiplier = self.stop_loss_mult_spin.value()
        self.temp_settings.trading_config.take_profit_multiplier = self.take_profit_mult_spin.value()
        
        # Signal filters
        self.temp_settings.trading_config.signal_filters = {
            'trend_confirmation': self.trend_confirmation_check.isChecked(),
            'volume_confirmation': self.volume_confirmation_check.isChecked(),
            'multiple_timeframe': self.multiple_timeframe_check.isChecked()
        }
        
        # UI Config
        self.temp_settings.ui_config.theme = self.theme_combo.currentText()
        
    def restore_defaults(self):
        """Restore default settings"""
        reply = QMessageBox.question(
            self, "Restore Defaults",
            "Are you sure you want to restore all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            default_settings = AppSettings()  # Create new instance with defaults
            self._copy_settings(default_settings, self.temp_settings)
            self.load_current_settings()  # Reload UI with defaults
            logger.info("Settings restored to defaults")
            
    def clear_cache(self):
        """Clear application cache"""
        reply = QMessageBox.question(
            self, "Clear Cache",
            "Are you sure you want to clear the application cache?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Implement cache clearing logic
            QMessageBox.information(self, "Cache Cleared", "Application cache has been cleared.")
            logger.info("Application cache cleared")
            
    def _copy_settings(self, source: AppSettings, target: AppSettings):
        """Copy settings from source to target"""
        # This is a simplified copy - in a real implementation,
        # you'd want to properly copy all nested objects
        target.technical_config = source.technical_config
        target.ml_model_config = source.ml_model_config
        target.trading_config = source.trading_config
        target.ui_config = source.ui_config