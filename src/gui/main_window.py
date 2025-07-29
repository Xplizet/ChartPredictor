"""
Main application window for ChartPredictor
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLabel, QPushButton, QTabWidget, 
                             QGroupBox, QSplitter, QProgressBar, QLineEdit,
                             QComboBox, QMessageBox, QMenuBar, QToolBar, 
                             QStatusBar, QFileDialog, QDialog, QCheckBox,
                             QSpinBox, QDoubleSpinBox, QFormLayout, QDialogButtonBox,
                             QScrollArea, QFrame, QTreeWidget, QTreeWidgetItem)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QAction, QFont
from typing import Optional, Dict, Any
import json
import os
from pathlib import Path
from datetime import datetime
from loguru import logger

from config.settings import AppSettings
from core.chart_extractor import ChartExtractor
from core.predictor import ChartPredictor
from core.live_data_fetcher import LiveDataFetcher, MarketDataRequest
from utils.export_manager import ExportManager
from .settings_dialog import SettingsDialog




class LiveDataWorker(QThread):
    """Worker thread for live data analysis"""
    
    progress_updated = pyqtSignal(int, str)
    analysis_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, request: MarketDataRequest, settings: AppSettings):
        super().__init__()
        self.request = request
        self.settings = settings
        self.live_fetcher = LiveDataFetcher(settings)
        self.chart_extractor = ChartExtractor(settings)
        self.predictor = ChartPredictor(settings)
        
    def run(self):
        """Run live data analysis"""
        try:
            # Step 1: Fetch live data
            self.progress_updated.emit(20, f"Fetching live data for {self.request.symbol}...")
            chart_data = self.live_fetcher.fetch_chart_data(self.request)
            
            # Step 2: Technical analysis
            self.progress_updated.emit(50, "Calculating technical indicators...")
            technical_analysis = self.chart_extractor.calculate_technical_indicators(chart_data)
            
            # Step 3: Pattern recognition (simplified for live data)
            self.progress_updated.emit(70, "Analyzing patterns...")
            patterns = self.predictor.detect_patterns(chart_data)
            
            # Step 4: Price prediction
            self.progress_updated.emit(85, "Generating predictions...")
            predictions = self.predictor.predict_price_movement(chart_data, technical_analysis)
            
            # Step 5: Trading signals
            self.progress_updated.emit(95, "Generating trading signals...")
            signals = self.predictor.generate_trading_signals(predictions, technical_analysis)
            
            # Compile results
            results = {
                'data_source': 'live_api',
                'symbol': self.request.symbol,
                'chart_data': chart_data,
                'technical_analysis': technical_analysis,
                'patterns': patterns,
                'predictions': predictions,
                'signals': signals,
                'timestamp': datetime.now().isoformat()
            }
            
            self.progress_updated.emit(100, "Live analysis complete!")
            self.analysis_completed.emit(results)
            
        except Exception as e:
            logger.error(f"Live data analysis failed: {e}")
            self.error_occurred.emit(str(e))


class PatternCategoryWidget(QFrame):
    """Custom widget for displaying categorized patterns with collapsible sections"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.patterns_by_category = {}
        
    def setup_ui(self):
        """Setup the categorized pattern display UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(8)
        
        # Pattern summary bar
        self.summary_frame = QFrame()
        self.summary_frame.setFrameStyle(QFrame.Shape.Box)
        self.summary_frame.setObjectName("patternSummaryFrame")  # Use object name for theme targeting
        self.summary_layout = QHBoxLayout(self.summary_frame)
        self.summary_label = QLabel("📊 Pattern Summary: No patterns detected")
        self.summary_label.setObjectName("patternSummaryLabel")  # Use object name for theme targeting
        self.summary_layout.addWidget(self.summary_label)
        self.layout.addWidget(self.summary_frame)
        
        # Scroll area for pattern categories
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(12)
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.layout.addWidget(self.scroll_area)
        
        # Category sections (will be created dynamically)
        self.category_sections = {}
        
    def categorize_patterns(self, patterns: list) -> Dict[str, list]:
        """Categorize patterns by type and confidence"""
        categories = {
            'high_priority': [],  # Rare/important patterns (any confidence)
            'high_confidence': [],  # High confidence patterns (>60%)
            'medium_confidence': [],  # Medium confidence patterns (40-60%)
            'low_confidence': [],  # Low confidence patterns (<40%)
            'reversal': [],       # Double Bottom, Double Top, Head & Shoulders
            'continuation': [],   # Triangles, Consolidation
            'momentum': [],       # Breakouts
            'trend': []          # Trend Channels
        }
        
        for pattern in patterns:
            name = getattr(pattern, 'name', '').lower()
            pattern_type = getattr(pattern, 'pattern_type', 'neutral')
            confidence = getattr(pattern, 'confidence', 0)
            
            # Categorize by confidence level first
            if confidence >= 0.6:
                categories['high_confidence'].append(pattern)
            elif confidence >= 0.4:
                categories['medium_confidence'].append(pattern)
            else:
                categories['low_confidence'].append(pattern)
            
            # Categorize based on pattern name and type
            if any(keyword in name for keyword in ['breakout', 'breakdown']):
                categories['momentum'].append(pattern)
                # Also add to high priority if high confidence
                if confidence > 0.7:
                    categories['high_priority'].append(pattern)
                    
            elif 'head' in name and 'shoulders' in name:
                categories['reversal'].append(pattern)
                categories['high_priority'].append(pattern)  # H&S is always high priority
                
            elif any(keyword in name for keyword in ['triangle', 'consolidation']):
                categories['continuation'].append(pattern)
                # Add triangles to high priority (less common)
                if 'triangle' in name:
                    categories['high_priority'].append(pattern)
                    
            elif 'trend' in name or 'channel' in name:
                categories['trend'].append(pattern)
                
            elif any(keyword in name for keyword in ['double bottom', 'double top']):
                categories['reversal'].append(pattern)
                
            else:
                # Default to reversal for unknown patterns
                categories['reversal'].append(pattern)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def get_pattern_color(self, pattern) -> str:
        """Get color coding for pattern based on type and direction"""
        name = getattr(pattern, 'name', '').lower()
        pattern_type = getattr(pattern, 'pattern_type', 'neutral')
        
        # Color coding based on pattern characteristics
        if pattern_type == 'bullish':
            return "#10B981"  # Emerald 500 - Bullish
        elif pattern_type == 'bearish':
            return "#EF4444"  # Red 500 - Bearish
        elif pattern_type == 'neutral' or any(keyword in name for keyword in ['triangle', 'consolidation']):
            return "#F59E0B"  # Amber 500 - Neutral
        else:
            return "#3B82F6"  # Blue 500 - Reversal patterns
    
    def create_category_section(self, category_name: str, patterns: list, is_expanded: bool = True) -> QFrame:
        """Create a collapsible section for a pattern category"""
        section = QFrame()
        section.setFrameStyle(QFrame.Shape.Box)
        section.setObjectName("patternSection")  # Use object name for theme targeting
        
        layout = QVBoxLayout(section)
        layout.setSpacing(4)
        
        # Category header with toggle button
        header = QFrame()
        header.setObjectName("patternHeader")  # Use object name for theme targeting
        header_layout = QHBoxLayout(header)
        
        # Category icon and title
        category_info = self.get_category_info(category_name)
        toggle_btn = QPushButton(f"{'▼' if is_expanded else '▶'} {category_info['icon']} {category_info['title']} ({len(patterns)})")
        toggle_btn.setObjectName("patternToggleBtn")  # Use object name for theme targeting
        
        header_layout.addWidget(toggle_btn)
        header_layout.addStretch()
        layout.addWidget(header)
        
        # Pattern content area
        content = QFrame()
        content.setVisible(is_expanded)
        content.setObjectName("patternContent")  # Use object name for theme targeting
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(6)
        
        # For large pattern lists, show only first 15 patterns initially with "Show More" option
        patterns_to_show = patterns[:15] if len(patterns) > 15 else patterns
        remaining_patterns = patterns[15:] if len(patterns) > 15 else []
        
        # Add initial patterns to content
        for pattern in patterns_to_show:
            pattern_widget = self.create_pattern_widget(pattern)
            content_layout.addWidget(pattern_widget)
        
        # Add "Show More" functionality for large lists
        if remaining_patterns:
            show_more_container = QFrame()
            show_more_layout = QVBoxLayout(show_more_container)
            show_more_layout.setContentsMargins(0, 0, 0, 0)
            
            show_more_btn = QPushButton(f"▼ Show {len(remaining_patterns)} more patterns")
            show_more_btn.setObjectName("patternToggleBtn")
            
            # Container for additional patterns (hidden initially)
            additional_content = QFrame()
            additional_content.setVisible(False)
            additional_layout = QVBoxLayout(additional_content)
            additional_layout.setSpacing(6)
            
            for pattern in remaining_patterns:
                pattern_widget = self.create_pattern_widget(pattern)
                additional_layout.addWidget(pattern_widget)
            
            def toggle_additional():
                is_visible = additional_content.isVisible()
                additional_content.setVisible(not is_visible)
                show_more_btn.setText(f"{'▲ Show fewer' if not is_visible else f'▼ Show {len(remaining_patterns)} more patterns'}")
            
            show_more_btn.clicked.connect(toggle_additional)
            
            show_more_layout.addWidget(show_more_btn)
            show_more_layout.addWidget(additional_content)
            content_layout.addWidget(show_more_container)
        
        layout.addWidget(content)
        
        # Connect toggle functionality
        def toggle_section():
            is_visible = content.isVisible()
            content.setVisible(not is_visible)
            toggle_btn.setText(f"{'▶' if is_visible else '▼'} {category_info['icon']} {category_info['title']} ({len(patterns)})")
        
        toggle_btn.clicked.connect(toggle_section)
        
        return section
    
    def get_category_info(self, category_name: str) -> Dict[str, str]:
        """Get display information for category"""
        category_map = {
            'high_priority': {'icon': '⭐', 'title': 'HIGH-PRIORITY PATTERNS', 'desc': 'Rare and significant patterns'},
            'high_confidence': {'icon': '🎯', 'title': 'HIGH CONFIDENCE PATTERNS', 'desc': 'Patterns with >60% confidence'},
            'medium_confidence': {'icon': '📊', 'title': 'MEDIUM CONFIDENCE PATTERNS', 'desc': 'Patterns with 40-60% confidence'},
            'low_confidence': {'icon': '🔍', 'title': 'LOW CONFIDENCE PATTERNS', 'desc': 'Patterns with <40% confidence'},
            'reversal': {'icon': '🔄', 'title': 'REVERSAL PATTERNS', 'desc': 'Trend reversal indicators'},
            'continuation': {'icon': '📈', 'title': 'CONTINUATION PATTERNS', 'desc': 'Trend continuation signals'},
            'momentum': {'icon': '🚀', 'title': 'MOMENTUM PATTERNS', 'desc': 'Breakout and momentum signals'},
            'trend': {'icon': '📏', 'title': 'TREND PATTERNS', 'desc': 'Trend-following patterns'}
        }
        return category_map.get(category_name, {'icon': '📊', 'title': category_name.upper(), 'desc': ''})
    
    def create_pattern_widget(self, pattern) -> QFrame:
        """Create a widget for displaying individual pattern"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.NoFrame)
        widget.setObjectName("patternWidget")  # Use object name for theme targeting
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Pattern details
        name = getattr(pattern, 'name', 'Unknown')
        confidence = getattr(pattern, 'confidence', 0)
        pattern_type = getattr(pattern, 'pattern_type', 'neutral')
        description = getattr(pattern, 'description', '')
        
        # Color indicator
        color = self.get_pattern_color(pattern)
        color_indicator = QLabel("●")
        color_indicator.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
        layout.addWidget(color_indicator)
        
        # Pattern info
        info_layout = QVBoxLayout()
        
        # Main pattern info
        main_label = QLabel(f"{name}: {confidence:.1%} confidence")
        main_label.setObjectName("patternMainLabel")  # Use object name for theme targeting
        info_layout.addWidget(main_label)
        
        # Details
        if hasattr(pattern, 'details') and pattern.details:
            details_label = QLabel(pattern.details)
            details_label.setObjectName("patternDetailsLabel")  # Use object name for theme targeting
            info_layout.addWidget(details_label)
        
        # Description (if available)
        if description:
            desc_label = QLabel(description)
            desc_label.setObjectName("patternDescLabel")  # Use object name for theme targeting
            info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return widget
    
    def update_patterns(self, patterns: list):
        """Update the pattern display with new data"""
        # Clear existing sections
        for section in self.category_sections.values():
            section.setParent(None)
        self.category_sections.clear()
        
        if not patterns:
            self.summary_label.setText("📊 Pattern Summary: No patterns detected")
            # Add empty state message
            empty_label = QLabel("No significant patterns detected in the current analysis.")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setObjectName("patternEmptyLabel")  # Use object name for theme targeting
            self.scroll_layout.addWidget(empty_label)
            return
        
        # Categorize patterns
        categorized = self.categorize_patterns(patterns)
        
        # Fallback: if no patterns were categorized (edge case), put them all in reversal
        if not categorized:
            categorized = {'reversal': patterns}
        
        # Update summary
        total_patterns = len(patterns)
        category_counts = [f"{info['icon']} {len(cat_patterns)}" for category, cat_patterns in categorized.items() 
                          for info in [self.get_category_info(category)]]
        summary_text = f"📊 Pattern Summary: {total_patterns} patterns • " + " | ".join(category_counts)
        self.summary_label.setText(summary_text)
        
        # Create sections in priority order - confidence first, then pattern type
        section_order = ['high_priority', 'high_confidence', 'medium_confidence', 'low_confidence', 
                        'momentum', 'continuation', 'trend', 'reversal']
        
        for category in section_order:
            if category in categorized:
                patterns_list = categorized[category]
                
                # Enhanced expansion logic:
                # 1. Always expand high_priority and high_confidence
                # 2. Always expand if <= 15 patterns (increased for better UX)
                # 3. Always expand medium_confidence (important for user understanding)
                # 4. Collapse low_confidence by default (less important)
                # 5. Always expand momentum, continuation, trend
                # 6. For large categories, still expand them if they're the main category
                is_expanded = (
                    category in ['high_priority', 'high_confidence', 'medium_confidence'] or 
                    len(patterns_list) <= 15 or 
                    category in ['momentum', 'continuation', 'trend'] or
                    (category == 'reversal' and len(patterns_list) <= 25) or
                    len(patterns_list) == max(len(cat_patterns) for cat_patterns in categorized.values())
                )
                
                section = self.create_category_section(category, patterns_list, is_expanded)
                self.category_sections[category] = section
                self.scroll_layout.addWidget(section)
        
        # Add stretch at the end
        self.scroll_layout.addStretch()

class ResultsPanel(QWidget):
    """Panel for displaying analysis results"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the results panel UI"""
        layout = QVBoxLayout(self)
        
        # Technical Analysis Section
        tech_group = QGroupBox("Technical Analysis")
        tech_layout = QVBoxLayout(tech_group)
        self.tech_text = QTextEdit()
        self.tech_text.setMaximumHeight(200)
        tech_layout.addWidget(self.tech_text)
        
        # Enhanced Pattern Recognition Section
        pattern_group = QGroupBox("Chart Patterns")
        pattern_layout = QVBoxLayout(pattern_group)
        
        # Replace simple text widget with categorized pattern widget
        self.pattern_widget = PatternCategoryWidget()
        pattern_layout.addWidget(self.pattern_widget)
        
        # Predictions Section
        pred_group = QGroupBox("Price Predictions")
        pred_layout = QVBoxLayout(pred_group)
        self.pred_text = QTextEdit()
        self.pred_text.setMaximumHeight(150)
        pred_layout.addWidget(self.pred_text)
        
        # Trading Signals Section
        signal_group = QGroupBox("Trading Signals")
        signal_layout = QVBoxLayout(signal_group)
        self.signal_text = QTextEdit()
        self.signal_text.setMaximumHeight(200)
        signal_layout.addWidget(self.signal_text)
        
        layout.addWidget(tech_group)
        layout.addWidget(pattern_group)
        layout.addWidget(pred_group)
        layout.addWidget(signal_group)
        layout.addStretch()
        
    def update_results(self, results: dict):
        """Update the display with analysis results"""
        try:
            # Update technical analysis
            tech_data = results.get('technical_analysis', {})
            tech_text = self.format_technical_analysis(tech_data)
            self.tech_text.setPlainText(tech_text)
            
            # Update patterns with new categorized widget
            patterns = results.get('patterns', [])
            self.pattern_widget.update_patterns(patterns)
            
            # Update predictions
            predictions = results.get('predictions', {})
            pred_text = self.format_predictions(predictions)
            self.pred_text.setPlainText(pred_text)
            
            # Update signals
            signals = results.get('signals', {})
            signal_text = self.format_signals(signals)
            self.signal_text.setPlainText(signal_text)
            
        except Exception as e:
            logger.error(f"Failed to update results display: {e}")
            
    def format_technical_analysis(self, tech_data: dict) -> str:
        """Format technical analysis data for display"""
        if not tech_data:
            return "No technical analysis data available"
            
        text = []
        for indicator, value in tech_data.items():
            if isinstance(value, (int, float)):
                text.append(f"{indicator.upper()}: {value:.2f}")
            else:
                text.append(f"{indicator.upper()}: {value}")
        return "\n".join(text)
        
    def format_patterns(self, patterns: list) -> str:
        """Format pattern recognition results"""
        if not patterns:
            return "No significant patterns detected"
            
        text = []
        for pattern in patterns:
            # Pattern is a dataclass, access attributes directly
            confidence = getattr(pattern, 'confidence', 0)
            name = getattr(pattern, 'name', 'Unknown')
            pattern_type = getattr(pattern, 'pattern_type', 'neutral')
            description = getattr(pattern, 'description', '')
            
            # Format with pattern type indicator
            type_indicator = "📈" if pattern_type == "bullish" else "📉" if pattern_type == "bearish" else "➡️"
            text.append(f"{type_indicator} {name}: {confidence:.1%} confidence")
            if description:
                text.append(f"   {description}")
        return "\n".join(text)
        
    def format_predictions(self, predictions) -> str:
        """Format predictions data for display"""
        if not predictions:
            return "No predictions available"
            
        text = []
        
        # Handle both dict and object formats
        if hasattr(predictions, 'direction'):
            direction = predictions.direction
            confidence = predictions.confidence
            target_price = predictions.target_price
            time_horizon = predictions.time_horizon
        else:
            direction = predictions.get('direction', 'Unknown')
            confidence = predictions.get('confidence', 0)
            target_price = predictions.get('target_price', 0)
            time_horizon = predictions.get('time_horizon', 'Unknown')
        
        # Add direction indicator
        direction_indicator = "📈" if direction == "UP" else "📉" if direction == "DOWN" else "➡️"
        
        text.append(f"{direction_indicator} Direction: {direction}")
        text.append(f"📊 Confidence: {confidence:.1%}")
        text.append(f"🎯 Target Price: {target_price}")
        text.append(f"⏰ Time Horizon: {time_horizon}")
        
        return "\n".join(text)
        
    def format_signals(self, signals) -> str:
        """Format trading signals"""
        if not signals:
            return "No trading signals generated"
            
        text = []
        # Handle both dict and dataclass objects
        if hasattr(signals, '__dict__'):  # Dataclass
            action = getattr(signals, 'action', 'HOLD')
            strength = getattr(signals, 'strength', 'Medium')
            entry = getattr(signals, 'entry_price', 'N/A')
            stop_loss = getattr(signals, 'stop_loss', 'N/A')
            take_profit = getattr(signals, 'take_profit', 'N/A')
            risk_reward = getattr(signals, 'risk_reward_ratio', 'N/A')
        else:  # Dict
            action = signals.get('action', 'HOLD')
            strength = signals.get('strength', 'Medium')
            entry = signals.get('entry_price', 'N/A')
            stop_loss = signals.get('stop_loss', 'N/A')
            take_profit = signals.get('take_profit', 'N/A')
            risk_reward = signals.get('risk_reward_ratio', 'N/A')
        
        # Add action indicator
        action_indicator = "🟢" if action == "BUY" else "🔴" if action == "SELL" else "🟡"
        
        text.append(f"{action_indicator} Action: {action}")
        text.append(f"💪 Strength: {strength}")
        text.append(f"💰 Entry Price: {entry}")
        text.append(f"🛡️ Stop Loss: {stop_loss}")
        text.append(f"🎯 Take Profit: {take_profit}")
        text.append(f"⚖️ Risk/Reward: {risk_reward}")
        
        return "\n".join(text)


class OptimizedResultsPanel(QWidget):
    """Optimized panel focusing on Chart Patterns and Price Predictions"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the optimized results panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Chart Patterns Section (Primary - gets most space)
        pattern_group = QGroupBox("Chart Patterns")
        pattern_layout = QVBoxLayout(pattern_group)
        
        # Enhanced Pattern Recognition with more space
        self.pattern_widget = PatternCategoryWidget()
        pattern_layout.addWidget(self.pattern_widget)
        
        # Price Predictions Section (Secondary)
        pred_group = QGroupBox("Price Predictions")
        pred_layout = QVBoxLayout(pred_group)
        self.pred_text = QTextEdit()
        self.pred_text.setMaximumHeight(180)  # Slightly larger than before
        self.pred_text.setMinimumHeight(150)
        pred_layout.addWidget(self.pred_text)
        
        # Add sections with better proportions
        layout.addWidget(pattern_group, 3)  # 75% of space to patterns
        layout.addWidget(pred_group, 1)     # 25% of space to predictions
        
    def update_results(self, results: dict):
        """Update the display with analysis results"""
        try:
            # Update patterns with new categorized widget
            patterns = results.get('patterns', [])
            self.pattern_widget.update_patterns(patterns)
            
            # Update predictions
            predictions = results.get('predictions', {})
            pred_text = self.format_predictions(predictions)
            self.pred_text.setPlainText(pred_text)
            
        except Exception as e:
            logger.error(f"Failed to update results display: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def format_predictions(self, predictions) -> str:
        """Format predictions data for display"""
        if not predictions:
            return "No predictions available"
            
        text = []
        
        # Handle both dict and object formats
        if hasattr(predictions, 'direction'):
            direction = predictions.direction
            confidence = predictions.confidence
            target_price = predictions.target_price
            time_horizon = predictions.time_horizon
        else:
            direction = predictions.get('direction', 'Unknown')
            confidence = predictions.get('confidence', 0)
            target_price = predictions.get('target_price', 0)
            time_horizon = predictions.get('time_horizon', 'Unknown')
        
        text.append(f"🎯 Direction: {direction}")
        text.append(f"📊 Confidence: {confidence:.1%}")
        text.append(f"💰 Target Price: ${target_price:.2f}")
        text.append(f"⏰ Time Horizon: {time_horizon}")
        
        return "\n".join(text)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, settings: AppSettings):
        super().__init__()
        self.settings = settings
        self.current_analysis = None
        self.analysis_worker = None
        
        # Initialize analysis components
        self.chart_extractor = ChartExtractor(settings)
        self.predictor = ChartPredictor(settings)
        
        # Track theme for changes
        self.current_theme = settings.ui_config.theme
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        
        # Apply window settings
        self.resize(settings.window_width, settings.window_height)
        self.setWindowTitle("ChartPredictor - Live Market Analysis")
        
    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Live Data Input + Additional Results
        left_panel = QFrame()
        self.left_layout = QVBoxLayout(left_panel)
        
        # Market Data Input Section (always visible)
        symbol_group = QGroupBox("Live Market Data Analysis")
        symbol_layout = QVBoxLayout(symbol_group)
        
        # Symbol input
        symbol_input_layout = QHBoxLayout()
        symbol_input_layout.addWidget(QLabel("Symbol:"))
        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("e.g., AAPL, BTC-USD, TSLA, NVDA")
        self.symbol_input.returnPressed.connect(self.fetch_live_data)  # Allow Enter key
        symbol_input_layout.addWidget(self.symbol_input)
        symbol_layout.addLayout(symbol_input_layout)
        
        # Timeframe and period controls
        controls_layout = QHBoxLayout()
        
        # Timeframe selection
        controls_layout.addWidget(QLabel("Interval:"))
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"])
        self.timeframe_combo.setCurrentText("1h")
        controls_layout.addWidget(self.timeframe_combo)
        
        # Period selection
        controls_layout.addWidget(QLabel("Period:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems(["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"])
        self.period_combo.setCurrentText("1mo")
        controls_layout.addWidget(self.period_combo)
        
        symbol_layout.addLayout(controls_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        self.fetch_btn = QPushButton("🔄 Analyze Market Data")
        self.fetch_btn.clicked.connect(self.fetch_live_data)
        self.fetch_btn.setDefault(True)  # Make it the default button
        buttons_layout.addWidget(self.fetch_btn)
        
        symbol_layout.addLayout(buttons_layout)
        
        # Market status indicator
        self.market_status_label = QLabel("Ready to analyze live market data")
        self.market_status_label.setObjectName("marketStatusLabel")
        symbol_layout.addWidget(self.market_status_label)
        
        self.left_layout.addWidget(symbol_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.left_layout.addWidget(self.progress_bar)
        
        # Placeholder for additional sections (will be added after analysis)
        self.left_results_container = QWidget()
        self.left_results_layout = QVBoxLayout(self.left_results_container)
        self.left_results_container.setVisible(False)  # Hidden initially
        self.left_layout.addWidget(self.left_results_container)
        
        # Add stretch at the end (will be reduced after analysis)
        self.left_layout.addStretch()
        
        # Right panel - Primary Results (Chart Patterns + Predictions)
        self.results_panel = OptimizedResultsPanel()
        
        # Add panels to splitter with better initial proportions
        splitter.addWidget(left_panel)
        splitter.addWidget(self.results_panel)
        splitter.setSizes([400, 600])  # Give more space to right panel initially
        
        main_layout.addWidget(splitter)
        
    def setup_menu(self):
        """Setup application menu"""
        menubar = self.menuBar()
        
        # Market menu
        market_menu = menubar.addMenu("&Market")
        
        analyze_action = QAction("&Analyze Symbol...", self)
        analyze_action.setShortcut("Ctrl+A")
        analyze_action.triggered.connect(self.focus_symbol_input)
        market_menu.addAction(analyze_action)
        
        market_menu.addSeparator()
        
        refresh_action = QAction("&Refresh Analysis", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.fetch_live_data)
        market_menu.addAction(refresh_action)
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        export_action = QAction("&Export Results...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        backtest_action = QAction("&Run Backtest...", self)
        backtest_action.setShortcut("Ctrl+B")
        backtest_action.triggered.connect(self.run_backtest)
        file_menu.addAction(backtest_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        """Setup application toolbar"""
        toolbar = self.addToolBar("Main")
        
        analyze_action = QAction("🔄 Analyze", self)
        analyze_action.setToolTip("Analyze market data (Ctrl+A)")
        analyze_action.triggered.connect(self.focus_symbol_input)
        toolbar.addAction(analyze_action)
        
        toolbar.addSeparator()
        
        refresh_action = QAction("🔄 Refresh", self)
        refresh_action.setToolTip("Refresh current analysis (F5)")
        refresh_action.triggered.connect(self.fetch_live_data)
        toolbar.addAction(refresh_action)
        
    def setup_statusbar(self):
        """Setup status bar"""
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        

        
    def fetch_live_data(self):
        """Fetch live market data and analyze"""
        symbol = self.symbol_input.text().strip().upper()
        if not symbol:
            QMessageBox.warning(self, "No Symbol", "Please enter a stock symbol (e.g., AAPL, BTC-USD)")
            return
            
        # Create market data request
        request = MarketDataRequest(
            symbol=symbol,
            period=self.period_combo.currentText(),
            interval=self.timeframe_combo.currentText(),
            source="yahoo"
        )
        
        # Disable UI during analysis
        self.fetch_btn.setEnabled(False)
        self.symbol_input.setEnabled(False)
        self.timeframe_combo.setEnabled(False)
        self.period_combo.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start live data worker
        self.live_worker = LiveDataWorker(request, self.settings)
        self.live_worker.progress_updated.connect(self.update_progress)
        self.live_worker.analysis_completed.connect(self.live_analysis_complete)
        self.live_worker.error_occurred.connect(self.live_analysis_error)
        self.live_worker.start()
        
    def update_progress(self, percentage: int, message: str):
        """Update progress bar and status"""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        
    def focus_symbol_input(self):
        """Focus on symbol input field for quick access"""
        self.symbol_input.setFocus()
        self.symbol_input.selectAll()
        
    def live_analysis_complete(self, results: dict):
        """Handle completed live data analysis"""
        self.current_analysis = results
        self.results_panel.update_results(results)
        self.populate_left_panel_results(results)
        
        # Re-enable UI
        self.fetch_btn.setEnabled(True)
        self.symbol_input.setEnabled(True)
        self.timeframe_combo.setEnabled(True)
        self.period_combo.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        symbol = results.get('symbol', 'Unknown')
        self.status_label.setText(f"Live analysis complete for {symbol}")
        
        logger.info(f"Live data analysis completed successfully for {symbol}")
        
    def live_analysis_error(self, error_message: str):
        """Handle live data analysis error"""
        QMessageBox.critical(self, "Live Data Error", f"Live data analysis failed: {error_message}")
        
        # Re-enable UI
        self.fetch_btn.setEnabled(True)
        self.symbol_input.setEnabled(True)
        self.timeframe_combo.setEnabled(True)
        self.period_combo.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Live analysis failed")
        
    def export_results(self):
        """Export analysis results to various formats"""
        if not hasattr(self, 'current_analysis') or not self.current_analysis:
            QMessageBox.information(self, "No Results", "No analysis results to export. Please run an analysis first.")
            return
        
        try:
            # Initialize export manager
            export_manager = ExportManager()
            supported_formats = export_manager.get_supported_formats()
            
            # Create file dialog
            symbol = self.current_analysis.get('symbol', 'unknown')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"chartpredictor_{symbol}_{timestamp}"
            
            # Build filter string for supported formats
            filter_parts = []
            if 'json' in supported_formats:
                filter_parts.append("JSON Files (*.json)")
            if 'csv' in supported_formats:
                filter_parts.append("CSV Files (*.csv)")
            if 'pdf' in supported_formats:
                filter_parts.append("PDF Reports (*.pdf)")
            filter_parts.append("All Files (*)")
            
            filter_string = ";;".join(filter_parts)
            
            # Show save dialog
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self,
                "Export Analysis Results",
                default_filename,
                filter_string
            )
            
            if not file_path:
                return  # User cancelled
            
            # Determine format from file extension or selected filter
            file_path = Path(file_path)
            if selected_filter.startswith("JSON"):
                format_type = "json"
                if not file_path.suffix:
                    file_path = file_path.with_suffix(".json")
            elif selected_filter.startswith("CSV"):
                format_type = "csv"
                if not file_path.suffix:
                    file_path = file_path.with_suffix(".csv")
            elif selected_filter.startswith("PDF"):
                format_type = "pdf"
                if not file_path.suffix:
                    file_path = file_path.with_suffix(".pdf")
            else:
                # Determine from extension
                extension = file_path.suffix.lower()
                if extension == '.json':
                    format_type = "json"
                elif extension == '.csv':
                    format_type = "csv"
                elif extension == '.pdf':
                    format_type = "pdf"
                else:
                    format_type = "json"  # Default fallback
                    file_path = file_path.with_suffix(".json")
            
            # Validate format is supported
            if format_type not in supported_formats:
                if 'pdf' not in supported_formats and format_type == 'pdf':
                    QMessageBox.warning(self, "Format Not Supported", 
                                      "PDF export requires the ReportLab library.\n"
                                      "Install it with: pip install reportlab\n"
                                      "Exporting as JSON instead.")
                    format_type = "json"
                    file_path = file_path.with_suffix(".json")
                else:
                    QMessageBox.warning(self, "Format Not Supported", 
                                      f"Format '{format_type}' is not supported.")
                    return
            
            # Export the results
            success = export_manager.export_results(
                self.current_analysis, 
                str(file_path), 
                format_type
            )
            
            if success:
                if format_type == 'csv':
                    # CSV creates multiple files
                    QMessageBox.information(
                        self, "Export Successful", 
                        f"Analysis results exported successfully!\n\n"
                        f"Multiple CSV files created in:\n{file_path.parent}\n\n"
                        f"Files include:\n"
                        f"• {file_path.stem}_ohlc_data.csv\n"
                        f"• {file_path.stem}_technical_indicators.csv\n"
                        f"• {file_path.stem}_analysis_summary.csv"
                    )
                else:
                    QMessageBox.information(
                        self, "Export Successful", 
                        f"Analysis results exported successfully to:\n{file_path}"
                    )
                
                # Update status
                self.status_label.setText(f"Results exported to {format_type.upper()}")
            else:
                QMessageBox.critical(
                    self, "Export Failed", 
                    f"Failed to export results to {format_type.upper()} format.\n"
                    f"Check the logs for more details."
                )
                
        except Exception as e:
            logger.error(f"Export error: {e}")
            QMessageBox.critical(
                self, "Export Error", 
                f"An error occurred during export:\n{str(e)}"
            )
        
    def show_settings(self):
        """Show settings dialog"""
        try:
            dialog = SettingsDialog(self.settings, self)
            dialog.settings_changed.connect(self.apply_new_settings)
            
            result = dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                # Settings have been applied via the signal
                self.status_label.setText("Settings updated successfully")
                logger.info("Settings dialog completed successfully")
                
        except Exception as e:
            logger.error(f"Settings dialog error: {e}")
            QMessageBox.critical(
                self, "Settings Error", 
                f"An error occurred while opening settings:\n{str(e)}"
            )
    
    def apply_new_settings(self, new_settings: AppSettings):
        """Apply new settings to the application"""
        try:
            # Update internal settings reference
            old_theme = self.current_theme if hasattr(self, 'current_theme') else 'dark'
            self.settings = new_settings
            
            # Save settings to file
            self.settings.save_to_file()
            
            # Apply theme changes immediately if needed
            new_theme = new_settings.ui_config.theme
            logger.info(f"Theme change check: old='{old_theme}' -> new='{new_theme}'")
            
            if old_theme != new_theme:
                logger.info(f"Applying theme change from '{old_theme}' to '{new_theme}'")
                self.apply_theme(new_theme)
                self.current_theme = new_theme  # Update tracked theme
                QMessageBox.information(
                    self, "Theme Applied",
                    f"Theme successfully changed to '{new_theme.title()}' theme!"
                )
            else:
                logger.info("No theme change detected")
            
            # Update analysis components with new settings
            if hasattr(self, 'chart_extractor'):
                # Reinitialize components with new settings
                self.chart_extractor = ChartExtractor(new_settings)
                self.predictor = ChartPredictor(new_settings)
                
            logger.info("New settings applied successfully")
            
        except Exception as e:
            logger.error(f"Failed to apply new settings: {e}")
            QMessageBox.critical(
                self, "Settings Error",
                f"Failed to apply new settings:\n{str(e)}"
            )
    
    def apply_theme(self, theme: str):
        """Apply theme to the application immediately"""
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            
            if theme == "dark":
                self.apply_dark_theme_to_app(app)
            elif theme == "light":
                self.apply_light_theme_to_app(app)
            elif theme == "auto":
                # Default to dark for auto mode
                self.apply_dark_theme_to_app(app)
                
            logger.info(f"Theme changed to: {theme}")
            
        except Exception as e:
            logger.error(f"Failed to apply theme {theme}: {e}")
            
    def apply_dark_theme_to_app(self, app):
        """Apply dark theme styling to the application"""
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
        QTreeWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #5a5a5a;
            border-radius: 3px;
            selection-background-color: #4a4a4a;
            selection-color: #ffffff;
            outline: none;
        }
        QTreeWidget::item {
            background-color: transparent;
            color: #ffffff;
            border: none;
            padding: 4px 8px;
            margin: 1px 0px;
        }
        QTreeWidget::item:selected {
            background-color: #4a4a4a;
            color: #ffffff;
        }
        QTreeWidget::item:hover {
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QTreeWidget::item:selected:hover {
            background-color: #5a5a5a;
            color: #ffffff;
        }
        QTreeWidget::branch {
            background-color: transparent;
        }
        QFrame#patternSection {
            border: 1px solid #5a5a5a;
            border-radius: 6px;
            margin: 2px;
            background-color: #2b2b2b;
        }
        QFrame#patternHeader {
            background-color: #3c3c3c;
            border-radius: 4px;
            border: 1px solid #5a5a5a;
        }
        QPushButton#patternToggleBtn {
            border: none;
            background: transparent;
            color: #ffffff;
            text-align: left;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton#patternToggleBtn:hover {
            background-color: #4a4a4a;
            border-radius: 4px;
        }
        QFrame#patternContent {
            background-color: #2b2b2b;
            border: none;
        }
        QFrame#patternWidget {
            background-color: transparent;
            border: none;
        }
        QFrame#patternWidget:hover {
            background-color: #3c3c3c;
            border-radius: 4px;
        }
        QLabel#patternMainLabel {
            color: #ffffff;
            font-weight: bold;
            font-size: 11px;
        }
        QLabel#patternDetailsLabel {
            color: #cccccc;
            font-size: 10px;
        }
        QLabel#patternDescLabel {
            color: #aaaaaa;
            font-size: 9px;
            font-style: italic;
        }
        QLabel#patternEmptyLabel {
            color: #cccccc;
            font-style: italic;
            padding: 20px;
        }
        QLabel#marketStatusLabel {
            color: #cccccc;
            font-style: italic;
        }
        QFrame#patternSummaryFrame {
            background-color: #3c3c3c;
            border: 1px solid #5a5a5a;
            border-radius: 4px;
            padding: 4px;
        }
        QLabel#patternSummaryLabel {
            color: #ffffff;
            font-weight: bold;
            padding: 4px;
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
        QScrollArea {
            background-color: #2b2b2b;
            border: 1px solid #5a5a5a;
            border-radius: 3px;
        }
        QScrollArea > QWidget > QWidget {
            background-color: #2b2b2b;
        }
        QScrollBar:vertical {
            background-color: #3c3c3c;
            width: 12px;
            border: 1px solid #5a5a5a;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #5a5a5a;
            border-radius: 5px;
            min-height: 20px;
            margin: 1px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #6a6a6a;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        QScrollBar:horizontal {
            background-color: #3c3c3c;
            height: 12px;
            border: 1px solid #5a5a5a;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background-color: #5a5a5a;
            border-radius: 5px;
            min-width: 20px;
            margin: 1px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #6a6a6a;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
        }
        """
        app.setStyleSheet(dark_stylesheet)
        
    def apply_light_theme_to_app(self, app):
        """Apply light theme styling to the application"""
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
        QTreeWidget {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #d0d0d0;
            border-radius: 3px;
            selection-background-color: #e0e0e0;
            selection-color: #000000;
            outline: none;
        }
        QTreeWidget::item {
            background-color: transparent;
            color: #000000;
            border: none;
            padding: 4px 8px;
            margin: 1px 0px;
        }
        QTreeWidget::item:selected {
            background-color: #e0e0e0;
            color: #000000;
        }
        QTreeWidget::item:hover {
            background-color: #f0f0f0;
            color: #000000;
        }
        QTreeWidget::item:selected:hover {
            background-color: #d0d0d0;
            color: #000000;
        }
        QTreeWidget::branch {
            background-color: transparent;
        }
        QFrame#patternSection {
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            margin: 2px;
            background-color: #ffffff;
        }
        QFrame#patternHeader {
            background-color: #f8f9fa;
            border-radius: 4px;
            border: 1px solid #d0d0d0;
        }
        QPushButton#patternToggleBtn {
            border: none;
            background: transparent;
            color: #000000;
            text-align: left;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton#patternToggleBtn:hover {
            background-color: #e9ecef;
            border-radius: 4px;
        }
        QFrame#patternContent {
            background-color: #ffffff;
            border: none;
        }
        QFrame#patternWidget {
            background-color: transparent;
            border: none;
        }
        QFrame#patternWidget:hover {
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        QLabel#patternMainLabel {
            color: #000000;
            font-weight: bold;
            font-size: 11px;
        }
        QLabel#patternDetailsLabel {
            color: #666666;
            font-size: 10px;
        }
        QLabel#patternDescLabel {
            color: #888888;
            font-size: 9px;
            font-style: italic;
        }
        QLabel#patternEmptyLabel {
            color: #666666;
            font-style: italic;
            padding: 20px;
        }
        QLabel#marketStatusLabel {
            color: #666666;
            font-style: italic;
        }
        QFrame#patternSummaryFrame {
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px;
        }
        QLabel#patternSummaryLabel {
            color: #000000;
            font-weight: bold;
            padding: 4px;
        }
        QGroupBox {
            color: #000000;
            border: 1px solid #d0d0d0;
            border-radius: 3px;
            margin-top: 1ex;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #000000;
        }
        QScrollArea {
            background-color: #ffffff;
            border: 1px solid #d0d0d0;
            border-radius: 3px;
        }
        QScrollArea > QWidget > QWidget {
            background-color: #ffffff;
        }
        QScrollBar:vertical {
            background-color: #f0f0f0;
            width: 12px;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #c0c0c0;
            border-radius: 5px;
            min-height: 20px;
            margin: 1px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #a0a0a0;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        QScrollBar:horizontal {
            background-color: #f0f0f0;
            height: 12px;
            border: 1px solid #d0d0d0;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background-color: #c0c0c0;
            border-radius: 5px;
            min-width: 20px;
            margin: 1px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #a0a0a0;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
        }
        """
        app.setStyleSheet(light_stylesheet)
    
    def run_backtest(self):
        """Run backtesting on current analysis results"""
        if not hasattr(self, 'current_analysis') or not self.current_analysis:
            QMessageBox.information(self, "No Analysis", "No analysis results available for backtesting. Please run an analysis first.")
            return
        
        if 'predictions' not in self.current_analysis or 'chart_data' not in self.current_analysis:
            QMessageBox.warning(self, "Incomplete Data", "Current analysis doesn't contain sufficient data for backtesting.")
            return
        
        try:
            # Show progress dialog
            progress_dialog = QMessageBox(self)
            progress_dialog.setWindowTitle("Running Backtest")
            progress_dialog.setText("Running backtesting analysis...\n\nThis may take a few moments.")
            progress_dialog.setStandardButtons(QMessageBox.StandardButton.NoButton)
            progress_dialog.show()
            
            # Process events to show dialog
            from PyQt6.QtWidgets import QApplication
            QApplication.processEvents()
            
            # Run backtest
            prediction = self.current_analysis['predictions']
            chart_data = self.current_analysis['chart_data']
            historical_data = chart_data.ohlc_data if hasattr(chart_data, 'ohlc_data') else []
            
            backtest_results = self.predictor.backtest_prediction(prediction, historical_data)
            
            # Close progress dialog
            progress_dialog.close()
            
            # Show results
            self.show_backtest_results(backtest_results)
            
            # Update status
            self.status_label.setText(f"Backtest completed - Accuracy: {backtest_results['accuracy']:.1%}")
            
        except Exception as e:
            logger.error(f"Backtesting error: {e}")
            if 'progress_dialog' in locals():
                progress_dialog.close()
            QMessageBox.critical(
                self, "Backtesting Error",
                f"An error occurred during backtesting:\n{str(e)}"
            )
    
    def show_backtest_results(self, results: Dict[str, Any]):
        """Display backtesting results in a dialog"""
        from PyQt6.QtWidgets import QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("📈 Backtesting Results")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Create text display
        text_display = QTextEdit()
        text_display.setReadOnly(True)
        
        # Format results
        results_text = self.format_backtest_results(results)
        text_display.setPlainText(results_text)
        
        layout.addWidget(text_display)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def format_backtest_results(self, results: Dict[str, Any]) -> str:
        """Format backtesting results for display"""
        text_parts = []
        
        text_parts.append("🎯 PREDICTION ACCURACY")
        text_parts.append("=" * 50)
        text_parts.append(f"Overall Accuracy: {results['accuracy']:.1%}")
        text_parts.append(f"Total Predictions: {results['total_predictions']}")
        text_parts.append(f"Correct Predictions: {results['correct_predictions']}")
        text_parts.append(f"UP Predictions Accuracy: {results['up_accuracy']:.1%}")
        text_parts.append(f"DOWN Predictions Accuracy: {results['down_accuracy']:.1%}")
        text_parts.append("")
        
        text_parts.append("💰 TRADING PERFORMANCE")
        text_parts.append("=" * 50)
        text_parts.append(f"Total P&L: ${results['profit_loss']:.2f}")
        text_parts.append(f"Total Trades: {results['total_trades']}")
        text_parts.append(f"Winning Trades: {results['winning_trades']}")
        text_parts.append(f"Losing Trades: {results['losing_trades']}")
        text_parts.append(f"Win Rate: {results['win_rate']:.1%}")
        text_parts.append("")
        
        if results['avg_win'] != 0 or results['avg_loss'] != 0:
            text_parts.append("📊 TRADE STATISTICS")
            text_parts.append("=" * 50)
            text_parts.append(f"Average Win: ${results['avg_win']:.2f}")
            text_parts.append(f"Average Loss: ${results['avg_loss']:.2f}")
            if results['avg_loss'] != 0:
                profit_factor = abs(results['avg_win']) / abs(results['avg_loss'])
                text_parts.append(f"Profit Factor: {profit_factor:.2f}")
            text_parts.append("")
        
        text_parts.append("⚠️ RISK METRICS")
        text_parts.append("=" * 50)
        text_parts.append(f"Maximum Drawdown: {results['max_drawdown']:.2%}")
        text_parts.append(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        text_parts.append("")
        
        text_parts.append("ℹ️ BACKTEST INFO")
        text_parts.append("=" * 50)
        text_parts.append(f"Backtest Period: {results['backtest_period']}")
        text_parts.append("")
        
        text_parts.append("📝 INTERPRETATION")
        text_parts.append("=" * 50)
        
        if results['accuracy'] >= 0.6:
            text_parts.append("✅ Good prediction accuracy (≥60%)")
        elif results['accuracy'] >= 0.5:
            text_parts.append("⚠️ Moderate prediction accuracy (50-60%)")
        else:
            text_parts.append("❌ Poor prediction accuracy (<50%)")
        
        if results['win_rate'] >= 0.5 and results['profit_loss'] > 0:
            text_parts.append("✅ Profitable trading strategy")
        elif results['profit_loss'] > 0:
            text_parts.append("⚠️ Marginally profitable strategy")
        else:
            text_parts.append("❌ Unprofitable trading strategy")
        
        if results['sharpe_ratio'] > 1.0:
            text_parts.append("✅ Excellent risk-adjusted returns")
        elif results['sharpe_ratio'] > 0.5:
            text_parts.append("⚠️ Moderate risk-adjusted returns")
        else:
            text_parts.append("❌ Poor risk-adjusted returns")
        
        text_parts.append("")
        text_parts.append("DISCLAIMER: Backtesting results are based on historical")
        text_parts.append("data and do not guarantee future performance. Past")
        text_parts.append("performance is not indicative of future results.")
        
        return "\n".join(text_parts)
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About ChartPredictor", 
                         "ChartPredictor v0.1.0\n\n"
                         "Live market data analysis and prediction tool\n"
                         "Real-time technical analysis with ML predictions\n"
                         "Built with Python and PyQt6")
        
    def populate_left_panel_results(self, results: dict):
        """Populate left panel with Technical Analysis and Trading Signals after analysis"""
        try:
            # Clear any existing results
            for i in reversed(range(self.left_results_layout.count())):
                child = self.left_results_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
            
            # Technical Analysis Section (moved to left panel)
            tech_group = QGroupBox("Technical Analysis")
            tech_layout = QVBoxLayout(tech_group)
            tech_text = QTextEdit()
            tech_text.setMaximumHeight(200)
            tech_text.setMinimumHeight(150)
            
            # Format and set technical analysis data
            tech_data = results.get('technical_analysis', {})
            tech_formatted = self.format_technical_analysis(tech_data)
            tech_text.setPlainText(tech_formatted)
            
            tech_layout.addWidget(tech_text)
            self.left_results_layout.addWidget(tech_group)
            
            # Trading Signals Section (moved to left panel)
            signal_group = QGroupBox("Trading Signals")
            signal_layout = QVBoxLayout(signal_group)
            signal_text = QTextEdit()
            signal_text.setMaximumHeight(200)
            signal_text.setMinimumHeight(150)
            
            # Format and set trading signals data
            signals = results.get('signals', {})
            signal_formatted = self.format_signals(signals)
            signal_text.setPlainText(signal_formatted)
            
            signal_layout.addWidget(signal_text)
            self.left_results_layout.addWidget(signal_group)
            
            # Show the left results container
            self.left_results_container.setVisible(True)
            
        except Exception as e:
            logger.error(f"Failed to populate left panel results: {e}")
    
    def format_technical_analysis(self, tech_data: dict) -> str:
        """Format technical analysis data for display"""
        if not tech_data:
            return "No technical analysis data available"
            
        text = []
        for indicator, value in tech_data.items():
            if isinstance(value, (int, float)):
                text.append(f"{indicator.upper()}: {value:.2f}")
            else:
                text.append(f"{indicator.upper()}: {value}")
        return "\n".join(text)
    
    def format_signals(self, signals) -> str:
        """Format trading signals data for display"""
        if not signals:
            return "No trading signals available"
            
        text = []
        
        # Handle both dict and object formats
        if hasattr(signals, 'action'):
            action = signals.action
            strength = signals.strength
            entry_price = signals.entry_price
            stop_loss = signals.stop_loss
            take_profit = signals.take_profit
            risk_reward = signals.risk_reward_ratio
        else:
            action = signals.get('action', 'Unknown')
            strength = signals.get('strength', 'Unknown')
            entry_price = signals.get('entry_price', 0)
            stop_loss = signals.get('stop_loss', 0)
            take_profit = signals.get('take_profit', 0)
            risk_reward = signals.get('risk_reward_ratio', 0)
        
        # Add appropriate emoji for action
        action_emoji = "🟢" if action == "BUY" else "🔴" if action == "SELL" else "⚪"
        
        text.append(f"{action_emoji} Action: {action}")
        text.append(f"⚡ Strength: {strength}")
        text.append(f"💵 Entry Price: ${entry_price:.2f}")
        text.append(f"🛑 Stop Loss: ${stop_loss:.2f}")
        text.append(f"🎯 Take Profit: ${take_profit:.2f}")
        text.append(f"📊 Risk/Reward: {risk_reward:.1f}")
        
        return "\n".join(text)

    def closeEvent(self, event):
        """Handle application close event"""
        # Stop any running live data analysis
        if hasattr(self, 'live_worker') and self.live_worker and self.live_worker.isRunning():
            self.live_worker.terminate()
            self.live_worker.wait()
            
        # Save settings
        self.settings.window_width = self.width()
        self.settings.window_height = self.height()
        self.settings.save_to_file()
        
        event.accept()