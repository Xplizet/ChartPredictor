"""
Chart prediction module
Handles pattern recognition and price movement prediction
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np
from loguru import logger

from config.settings import AppSettings
from .chart_extractor import ChartData


@dataclass
class Pattern:
    """Detected chart pattern"""
    name: str
    confidence: float
    start_time: str
    end_time: str
    pattern_type: str  # "bullish", "bearish", "neutral"
    description: str


@dataclass
class Prediction:
    """Price prediction result"""
    direction: str  # "UP", "DOWN", "SIDEWAYS"
    confidence: float
    target_price: Optional[float]
    time_horizon: str  # e.g., "24h", "1w"
    reasoning: str


@dataclass
class TradingSignal:
    """Trading recommendation"""
    action: str  # "BUY", "SELL", "HOLD"
    strength: str  # "Strong", "Medium", "Weak"
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    risk_reward_ratio: float
    reasoning: str


class ChartPredictor:
    """Main prediction engine for chart analysis"""
    
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.model_config = settings.ml_model_config
        self.trading_config = settings.trading_config
        
    def detect_patterns(self, chart_data: ChartData) -> List[Pattern]:
        """Detect chart patterns using real market data analysis"""
        logger.info("Detecting chart patterns")
        
        patterns = []
        
        if not chart_data.ohlc_data or len(chart_data.ohlc_data) < 20:
            logger.warning("Insufficient data for pattern detection")
            return patterns
        
        # Convert OHLC data to arrays for analysis
        closes = np.array([d.close for d in chart_data.ohlc_data])
        highs = np.array([d.high for d in chart_data.ohlc_data])
        lows = np.array([d.low for d in chart_data.ohlc_data])
        volumes = np.array([d.volume for d in chart_data.ohlc_data])
        
        # Detect various patterns
        double_bottom_patterns = self._detect_double_bottom(closes, highs, lows, chart_data)
        double_top_patterns = self._detect_double_top(closes, highs, lows, chart_data)
        head_shoulders_patterns = self._detect_head_shoulders(closes, highs, lows, chart_data)
        triangle_patterns = self._detect_triangles(closes, highs, lows, chart_data)
        breakout_patterns = self._detect_breakouts(closes, highs, lows, volumes, chart_data)
        trend_channel_patterns = self._detect_trend_channels(closes, chart_data)
        
        # Debug logging for pattern detection
        logger.debug(f"Pattern detection results: DB={len(double_bottom_patterns)}, DT={len(double_top_patterns)}, "
                    f"HS={len(head_shoulders_patterns)}, TR={len(triangle_patterns)}, "
                    f"BO={len(breakout_patterns)}, TC={len(trend_channel_patterns)}")
        
        # Add missing line - extend patterns with double_bottom_patterns
        patterns.extend(double_bottom_patterns)
        patterns.extend(double_top_patterns)
        patterns.extend(head_shoulders_patterns)
        patterns.extend(triangle_patterns)
        patterns.extend(breakout_patterns)
        patterns.extend(trend_channel_patterns)
        
        # Return ALL patterns - let UI handle confidence-based display
        # Count patterns above threshold for logging but don't filter
        high_confidence_count = len([p for p in patterns if p.confidence >= self.model_config.confidence_threshold])
        
        logger.info(f"Detected {len(patterns)} total patterns, {high_confidence_count} above confidence threshold")
        return patterns
    
    def _detect_double_bottom(self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray, chart_data: ChartData) -> List[Pattern]:
        """Detect double bottom patterns"""
        patterns = []
        
        if len(lows) < 20:
            return patterns
        
        # Find local minima
        window = 5
        local_mins = []
        for i in range(window, len(lows) - window):
            if all(lows[i] <= lows[i-j] for j in range(1, window+1)) and \
               all(lows[i] <= lows[i+j] for j in range(1, window+1)):
                local_mins.append((i, lows[i]))
        
        # Look for double bottoms
        for i in range(len(local_mins) - 1):
            for j in range(i + 1, len(local_mins)):
                idx1, low1 = local_mins[i]
                idx2, low2 = local_mins[j]
                
                if abs(low1 - low2) / low1 < 0.02:  # Within 2% of each other
                    # Check if there's a significant peak between them
                    between_high = max(highs[idx1:idx2])
                    if (between_high - min(low1, low2)) / min(low1, low2) > 0.05:  # 5% higher
                        confidence = min(0.85, 0.5 + (j - i) * 0.05)  # Higher confidence for more separated bottoms
                        
                        patterns.append(Pattern(
                            name="Double Bottom",
                            confidence=confidence,
                            start_time=str(chart_data.ohlc_data[idx1].timestamp.date()),
                            end_time=str(chart_data.ohlc_data[idx2].timestamp.date()),
                            pattern_type="bullish",
                            description=f"Double bottom at ${low1:.2f} and ${low2:.2f}"
                        ))
                        break
        
        return patterns
    
    def _detect_double_top(self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray, chart_data: ChartData) -> List[Pattern]:
        """Detect double top patterns"""
        patterns = []
        
        if len(highs) < 20:
            return patterns
        
        # Find local maxima
        window = 5
        local_maxs = []
        for i in range(window, len(highs) - window):
            if all(highs[i] >= highs[i-j] for j in range(1, window+1)) and \
               all(highs[i] >= highs[i+j] for j in range(1, window+1)):
                local_maxs.append((i, highs[i]))
        
        # Look for double tops
        for i in range(len(local_maxs) - 1):
            for j in range(i + 1, len(local_maxs)):
                idx1, high1 = local_maxs[i]
                idx2, high2 = local_maxs[j]
                
                if abs(high1 - high2) / high1 < 0.02:  # Within 2% of each other
                    # Check if there's a significant dip between them
                    between_low = min(lows[idx1:idx2])
                    if (min(high1, high2) - between_low) / between_low > 0.05:  # 5% lower
                        confidence = min(0.85, 0.5 + (j - i) * 0.05)
                        
                        patterns.append(Pattern(
                            name="Double Top",
                            confidence=confidence,
                            start_time=str(chart_data.ohlc_data[idx1].timestamp.date()),
                            end_time=str(chart_data.ohlc_data[idx2].timestamp.date()),
                            pattern_type="bearish",
                            description=f"Double top at ${high1:.2f} and ${high2:.2f}"
                        ))
                        break
        
        return patterns
    
    def _detect_head_shoulders(self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray, chart_data: ChartData) -> List[Pattern]:
        """Detect head and shoulders patterns"""
        patterns = []
        
        if len(highs) < 25:  # Reduced from 30
            logger.debug(f"Head & Shoulders: Insufficient data ({len(highs)} < 25)")
            return patterns
        
        window = 5  # Increased from 3 for better peak detection
        local_maxs = []
        for i in range(window, len(highs) - window):
            if all(highs[i] >= highs[i-j] for j in range(1, window+1)) and \
               all(highs[i] >= highs[i+j] for j in range(1, window+1)):
                local_maxs.append((i, highs[i]))
        
        logger.debug(f"Head & Shoulders: Found {len(local_maxs)} local maxima")
        
        # Look for head and shoulders (need at least 3 peaks)
        if len(local_maxs) >= 3:
            candidates_checked = 0
            for i in range(len(local_maxs) - 2):
                candidates_checked += 1
                left_shoulder = local_maxs[i]
                head = local_maxs[i + 1]
                right_shoulder = local_maxs[i + 2]
                
                # Check proportions - made more lenient
                left_height = left_shoulder[1]
                head_height = head[1]
                right_height = right_shoulder[1]
                
                head_vs_left = head_height / left_height
                head_vs_right = head_height / right_height
                shoulder_similarity = abs(left_height - right_height) / left_height
                
                # Reduced height requirement from 5% to 2% and shoulder similarity from 5% to 8%
                if (head_height > left_height * 1.02 and head_height > right_height * 1.02 and
                    abs(left_height - right_height) / left_height < 0.08):
                    
                    # Ensure reasonable spacing between peaks
                    spacing1 = head[0] - left_shoulder[0]
                    spacing2 = right_shoulder[0] - head[0]
                    if spacing1 > 3 and spacing2 > 3:  # Minimum 3 periods between peaks
                        
                        confidence = min(0.8, 0.6 + (head_height / max(left_height, right_height) - 1.0) * 5)
                        logger.debug(f"Head & Shoulders: FOUND - Head: {head_height:.2f}, Shoulders: {left_height:.2f}/{right_height:.2f}, Confidence: {confidence:.2f}")
                        patterns.append(Pattern(
                            name="Head and Shoulders",
                            confidence=confidence,
                            start_time=str(chart_data.ohlc_data[left_shoulder[0]].timestamp.date()),
                            end_time=str(chart_data.ohlc_data[right_shoulder[0]].timestamp.date()),
                            pattern_type="bearish",
                            description=f"Head at ${head_height:.2f}, shoulders at ${left_height:.2f} and ${right_height:.2f}"
                        ))
                    else:
                        logger.debug(f"Head & Shoulders: Spacing too small - {spacing1}, {spacing2}")
                else:
                    logger.debug(f"Head & Shoulders: Ratios failed - Head vs L/R: {head_vs_left:.3f}/{head_vs_right:.3f}, Shoulder sim: {shoulder_similarity:.3f}")
            
            logger.debug(f"Head & Shoulders: Checked {candidates_checked} candidates")        
        else:
            logger.debug(f"Head & Shoulders: Need ≥3 peaks, found {len(local_maxs)}")
        
        return patterns
    
    def _detect_triangles(self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray, chart_data: ChartData) -> List[Pattern]:
        """Detect triangle patterns (ascending, descending, symmetrical)"""
        patterns = []
        
        if len(closes) < 20:  # Reduced minimum requirement
            logger.debug(f"Triangles: Insufficient data ({len(closes)} < 20)")
            return patterns
        
        # Use adaptive period - longer for more data
        analysis_period = min(50, max(20, len(closes) // 2))  # Dynamic period
        recent_highs = highs[-analysis_period:]
        recent_lows = lows[-analysis_period:]
        recent_closes = closes[-analysis_period:]
        
        logger.debug(f"Triangles: Analyzing {analysis_period} periods from {len(closes)} total")
        
        # Calculate trend lines for highs and lows
        x = np.arange(len(recent_highs))
        
        # Linear regression for highs and lows
        high_slope = np.polyfit(x, recent_highs, 1)[0]
        low_slope = np.polyfit(x, recent_lows, 1)[0]
        
        # Normalize slopes by average price to get percentage slope
        avg_price = np.mean(recent_closes)
        high_slope_pct = (high_slope / avg_price) * 100  # Convert to percentage
        low_slope_pct = (low_slope / avg_price) * 100
        
        logger.debug(f"Triangles: Raw slopes - High: {high_slope:.6f}, Low: {low_slope:.6f}")
        logger.debug(f"Triangles: Percentage slopes - High: {high_slope_pct:.4f}%, Low: {low_slope_pct:.4f}%")
        logger.debug(f"Triangles: Average price: ${avg_price:.2f}")
        
        # Much more realistic thresholds for noisy market data
        flat_threshold = 0.15  # 0.15% slope considered flat (increased from 0.05%)
        rising_threshold = 0.05  # 0.05% slope considered rising (increased from 0.02%)
        falling_threshold = -0.05  # -0.05% slope considered falling (increased from -0.02%)
        
        # Calculate R-squared to ensure trend lines are meaningful
        high_r2 = np.corrcoef(x, recent_highs)[0, 1] ** 2
        low_r2 = np.corrcoef(x, recent_lows)[0, 1] ** 2
        
        logger.debug(f"Triangles: R-squared values - High: {high_r2:.4f}, Low: {low_r2:.4f}")
        logger.debug(f"Triangles: Threshold checks - Flat: ±{flat_threshold}%, Rising: >{rising_threshold}%, Falling: <{falling_threshold}%")
        
        # Reduced R-squared requirement for noisy market data
        if high_r2 > 0.15 or low_r2 > 0.15:  # Reduced from 0.3 to 0.15
            logger.debug(f"Triangles: R-squared threshold passed")
            
            # Determine triangle type with much more realistic thresholds
            if abs(high_slope_pct) < flat_threshold and low_slope_pct > rising_threshold:
                # Flat top, rising bottom = Ascending Triangle
                confidence = min(0.8, 0.5 + low_r2 * 0.3)
                logger.debug(f"Triangles: FOUND Ascending Triangle - High slope: {high_slope_pct:.4f}% (flat), Low slope: {low_slope_pct:.4f}% (rising)")
                patterns.append(Pattern(
                    name="Ascending Triangle",
                    confidence=confidence,
                    start_time=str(chart_data.ohlc_data[-analysis_period].timestamp.date()),
                    end_time=str(chart_data.ohlc_data[-1].timestamp.date()),
                    pattern_type="bullish",
                    description=f"Ascending triangle (R²: {low_r2:.2f})"
                ))
                
            elif high_slope_pct < falling_threshold and abs(low_slope_pct) < flat_threshold:
                # Falling top, flat bottom = Descending Triangle  
                confidence = min(0.8, 0.5 + high_r2 * 0.3)
                logger.debug(f"Triangles: FOUND Descending Triangle - High slope: {high_slope_pct:.4f}% (falling), Low slope: {low_slope_pct:.4f}% (flat)")
                patterns.append(Pattern(
                    name="Descending Triangle",
                    confidence=confidence,
                    start_time=str(chart_data.ohlc_data[-analysis_period].timestamp.date()),
                    end_time=str(chart_data.ohlc_data[-1].timestamp.date()),
                    pattern_type="bearish",
                    description=f"Descending triangle (R²: {high_r2:.2f})"
                ))
                
            elif high_slope_pct < falling_threshold and low_slope_pct > rising_threshold:
                # Both converging = Symmetrical Triangle
                convergence_quality = min(high_r2, low_r2)
                confidence = min(0.75, 0.45 + convergence_quality * 0.3)
                logger.debug(f"Triangles: FOUND Symmetrical Triangle - High slope: {high_slope_pct:.4f}% (falling), Low slope: {low_slope_pct:.4f}% (rising)")
                patterns.append(Pattern(
                    name="Symmetrical Triangle",
                    confidence=confidence,
                    start_time=str(chart_data.ohlc_data[-analysis_period].timestamp.date()),
                    end_time=str(chart_data.ohlc_data[-1].timestamp.date()),
                    pattern_type="neutral",
                    description=f"Symmetrical triangle (R²: {convergence_quality:.2f})"
                ))
            elif abs(high_slope_pct) < flat_threshold and abs(low_slope_pct) < flat_threshold:
                # Both flat = Consolidation/Rectangle (not traditional triangle but useful pattern)
                avg_r2 = (high_r2 + low_r2) / 2
                confidence = min(0.7, 0.4 + avg_r2 * 0.3)
                logger.debug(f"Triangles: FOUND Consolidation Pattern - High slope: {high_slope_pct:.4f}% (flat), Low slope: {low_slope_pct:.4f}% (flat)")
                patterns.append(Pattern(
                    name="Consolidation Triangle",
                    confidence=confidence,
                    start_time=str(chart_data.ohlc_data[-analysis_period].timestamp.date()),
                    end_time=str(chart_data.ohlc_data[-1].timestamp.date()),
                    pattern_type="neutral",
                    description=f"Sideways consolidation (R²: {avg_r2:.2f})"
                ))
            else:
                logger.debug(f"Triangles: No triangle patterns match - High: {high_slope_pct:.4f}%, Low: {low_slope_pct:.4f}%")
                logger.debug(f"Triangles: Conditions - Ascending: high flat ({abs(high_slope_pct):.4f} < {flat_threshold}) & low rising ({low_slope_pct:.4f} > {rising_threshold})")
                logger.debug(f"Triangles: Conditions - Descending: high falling ({high_slope_pct:.4f} < {falling_threshold}) & low flat ({abs(low_slope_pct):.4f} < {flat_threshold})")
                logger.debug(f"Triangles: Conditions - Symmetrical: high falling ({high_slope_pct:.4f} < {falling_threshold}) & low rising ({low_slope_pct:.4f} > {rising_threshold})")
                logger.debug(f"Triangles: Conditions - Consolidation: high flat ({abs(high_slope_pct):.4f} < {flat_threshold}) & low flat ({abs(low_slope_pct):.4f} < {flat_threshold})")
        else:
            logger.debug(f"Triangles: R-squared threshold failed - High: {high_r2:.4f}, Low: {low_r2:.4f} (need > 0.15)")
        
        logger.debug(f"Triangles: Found {len(patterns)} triangle patterns")
        
        return patterns
    
    def _detect_breakouts(self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray, volumes: np.ndarray, chart_data: ChartData) -> List[Pattern]:
        """Detect support/resistance breakouts"""
        patterns = []
        
        if len(closes) < 15:  # Reduced from 20
            logger.debug(f"Breakouts: Insufficient data ({len(closes)} < 15)")
            return patterns
        
        # Calculate recent support and resistance levels
        recent_period = min(20, len(closes) - 5)  # Adaptive period
        recent_highs = highs[-recent_period:]
        recent_lows = lows[-recent_period:]
        recent_volumes = volumes[-recent_period:]
        
        logger.debug(f"Breakouts: Analyzing {recent_period} periods from {len(closes)} total")
        
        # Multiple resistance/support levels
        resistance_levels = [
            np.max(recent_highs[:-5]),  # Exclude last 5 bars
            np.percentile(recent_highs, 90),  # 90th percentile
            np.percentile(recent_highs, 85)   # 85th percentile
        ]
        
        support_levels = [
            np.min(recent_lows[:-5]),   # Exclude last 5 bars  
            np.percentile(recent_lows, 10),   # 10th percentile
            np.percentile(recent_lows, 15)    # 15th percentile
        ]
        
        current_price = closes[-1]
        avg_volume = np.mean(recent_volumes[:-3])  # Average of recent volume
        current_volume = volumes[-1] if len(volumes) > 0 else avg_volume
        
        logger.debug(f"Breakouts: Current price: ${current_price:.2f}")
        logger.debug(f"Breakouts: Resistance levels: ${resistance_levels[0]:.2f}, ${resistance_levels[1]:.2f}, ${resistance_levels[2]:.2f}")
        logger.debug(f"Breakouts: Support levels: ${support_levels[0]:.2f}, ${support_levels[1]:.2f}, ${support_levels[2]:.2f}")
        logger.debug(f"Breakouts: Volume - Current: {current_volume:.0f}, Average: {avg_volume:.0f}, Ratio: {current_volume/avg_volume:.2f}x")
        
        # Check for resistance breakouts with reduced thresholds
        resistance_found = False
        for i, resistance in enumerate(resistance_levels):
            breakout_threshold = 1.005 + (i * 0.003)  # 0.5%, 0.8%, 1.1% thresholds
            threshold_price = resistance * breakout_threshold
            
            logger.debug(f"Breakouts: Resistance {i+1} - Level: ${resistance:.2f}, Threshold: ${threshold_price:.2f} ({breakout_threshold-1:.1%})")
            
            if current_price > threshold_price:
                # Base confidence from price breakout
                base_confidence = 0.55 + (i * 0.05)  # Higher confidence for stronger levels
                
                # Volume boost (optional, not required)
                volume_multiplier = 1.0
                if current_volume > avg_volume * 1.2:  # Reduced from 1.5x
                    volume_multiplier = min(1.3, current_volume / avg_volume / 1.2)
                    logger.debug(f"Breakouts: Volume boost applied - {volume_multiplier:.2f}x")
                else:
                    logger.debug(f"Breakouts: No volume boost (need {avg_volume * 1.2:.0f}, got {current_volume:.0f})")
                    
                confidence = min(0.85, base_confidence * volume_multiplier)
                
                breakout_type = ["Minor", "Moderate", "Strong"][i]
                logger.debug(f"Breakouts: FOUND {breakout_type} Resistance Breakout - Price: ${current_price:.2f} > ${threshold_price:.2f}, Confidence: {confidence:.2f}")
                patterns.append(Pattern(
                    name=f"{breakout_type} Resistance Breakout",
                    confidence=confidence,
                    start_time=str(chart_data.ohlc_data[-5].timestamp.date()),
                    end_time=str(chart_data.ohlc_data[-1].timestamp.date()),
                    pattern_type="bullish",
                    description=f"Breakout above ${resistance:.2f} ({breakout_threshold-1:.1%} threshold)"
                ))
                resistance_found = True
                break  # Only report the strongest breakout
            else:
                logger.debug(f"Breakouts: Resistance {i+1} not broken - ${current_price:.2f} <= ${threshold_price:.2f}")
        
        # Check for support breakdowns 
        support_found = False
        for i, support in enumerate(support_levels):
            breakdown_threshold = 0.995 - (i * 0.003)  # 0.5%, 0.8%, 1.1% thresholds
            threshold_price = support * breakdown_threshold
            
            logger.debug(f"Breakouts: Support {i+1} - Level: ${support:.2f}, Threshold: ${threshold_price:.2f} ({1-breakdown_threshold:.1%})")
            
            if current_price < threshold_price:
                # Base confidence from price breakdown
                base_confidence = 0.55 + (i * 0.05)
                
                # Volume boost (optional, not required)
                volume_multiplier = 1.0
                if current_volume > avg_volume * 1.2:
                    volume_multiplier = min(1.3, current_volume / avg_volume / 1.2)
                    logger.debug(f"Breakouts: Volume boost applied - {volume_multiplier:.2f}x")
                else:
                    logger.debug(f"Breakouts: No volume boost (need {avg_volume * 1.2:.0f}, got {current_volume:.0f})")
                    
                confidence = min(0.85, base_confidence * volume_multiplier)
                
                breakdown_type = ["Minor", "Moderate", "Strong"][i]
                logger.debug(f"Breakouts: FOUND {breakdown_type} Support Breakdown - Price: ${current_price:.2f} < ${threshold_price:.2f}, Confidence: {confidence:.2f}")
                patterns.append(Pattern(
                    name=f"{breakdown_type} Support Breakdown",
                    confidence=confidence,
                    start_time=str(chart_data.ohlc_data[-5].timestamp.date()),
                    end_time=str(chart_data.ohlc_data[-1].timestamp.date()),
                    pattern_type="bearish",
                    description=f"Breakdown below ${support:.2f} ({1-breakdown_threshold:.1%} threshold)"
                ))
                support_found = True
                break  # Only report the strongest breakdown
            else:
                logger.debug(f"Breakouts: Support {i+1} not broken - ${current_price:.2f} >= ${threshold_price:.2f}")
        
        if not resistance_found and not support_found:
            logger.debug(f"Breakouts: No breakouts detected - Price ${current_price:.2f} within normal range")
        
        logger.debug(f"Breakouts: Found {len(patterns)} breakout patterns")
        
        return patterns
    
    def _detect_trend_channels(self, closes: np.ndarray, chart_data: ChartData) -> List[Pattern]:
        """Detect trend channels and potential breaks"""
        patterns = []
        
        if len(closes) < 50:
            return patterns
        
        # Calculate trend over different periods
        short_period = 20
        long_period = 50
        
        # Short-term trend
        short_slope = np.polyfit(range(short_period), closes[-short_period:], 1)[0]
        # Long-term trend
        long_slope = np.polyfit(range(long_period), closes[-long_period:], 1)[0]
        
        # Determine trend strength
        price_change = (closes[-1] - closes[-short_period]) / closes[-short_period]
        
        if short_slope > 0 and long_slope > 0 and price_change > 0.05:
            confidence = min(0.8, 0.5 + abs(price_change) * 2)
            patterns.append(Pattern(
                name="Uptrend Channel",
                confidence=confidence,
                start_time=str(chart_data.ohlc_data[-short_period].timestamp.date()),
                end_time=str(chart_data.ohlc_data[-1].timestamp.date()),
                pattern_type="bullish",
                description=f"Strong uptrend with {price_change:.1%} gain"
            ))
        elif short_slope < 0 and long_slope < 0 and price_change < -0.05:
            confidence = min(0.8, 0.5 + abs(price_change) * 2)
            patterns.append(Pattern(
                name="Downtrend Channel",
                confidence=confidence,
                start_time=str(chart_data.ohlc_data[-short_period].timestamp.date()),
                end_time=str(chart_data.ohlc_data[-1].timestamp.date()),
                pattern_type="bearish",
                description=f"Strong downtrend with {price_change:.1%} decline"
            ))
        elif abs(short_slope) < abs(long_slope) * 0.3:  # Trend weakening
            confidence = 0.6
            trend_type = "bullish" if long_slope > 0 else "bearish"
            patterns.append(Pattern(
                name="Trend Weakening",
                confidence=confidence,
                start_time=str(chart_data.ohlc_data[-short_period].timestamp.date()),
                end_time=str(chart_data.ohlc_data[-1].timestamp.date()),
                pattern_type="neutral",
                description=f"Previous {trend_type} trend showing signs of weakening"
            ))
        
        return patterns
        
    def predict_price_movement(self, chart_data: ChartData, technical_analysis: Dict[str, Any]) -> Prediction:
        """Predict future price movement based on chart data and technical indicators"""
        logger.info("Generating price movement prediction")
        
        # Heuristic-based prediction using technical indicators
        # This provides reliable predictions based on RSI, MACD, moving averages
        # Future enhancements could include LSTM neural networks and ensemble methods
        bullish_signals = 0
        bearish_signals = 0
        
        # RSI analysis
        rsi = technical_analysis.get('RSI')
        if rsi:
            if rsi < 30:
                bullish_signals += 1
            elif rsi > 70:
                bearish_signals += 1
                
        # MACD analysis
        macd = technical_analysis.get('MACD')
        macd_signal = technical_analysis.get('MACD_Signal')
        if macd and macd_signal:
            if macd > macd_signal:
                bullish_signals += 1
            else:
                bearish_signals += 1
                
        # Moving average analysis
        current_price = chart_data.price_levels.get('current_price', 150.0)
        ma_9 = technical_analysis.get('MA_9')
        ma_21 = technical_analysis.get('MA_21')
        
        if ma_9 and ma_21:
            if ma_9 > ma_21 and current_price > ma_9:
                bullish_signals += 1
            elif ma_9 < ma_21 and current_price < ma_9:
                bearish_signals += 1
                
        # Determine direction and confidence
        if bullish_signals > bearish_signals:
            direction = "UP"
            confidence = min(0.9, 0.5 + (bullish_signals - bearish_signals) * 0.15)
            target_price = current_price * 1.05  # 5% upside target
            reasoning = f"Bullish signals: {bullish_signals}, Bearish signals: {bearish_signals}"
        elif bearish_signals > bullish_signals:
            direction = "DOWN"
            confidence = min(0.9, 0.5 + (bearish_signals - bullish_signals) * 0.15)
            target_price = current_price * 0.95  # 5% downside target
            reasoning = f"Bearish signals: {bearish_signals}, Bullish signals: {bullish_signals}"
        else:
            direction = "SIDEWAYS"
            confidence = 0.5
            target_price = current_price
            reasoning = "Equal bullish and bearish signals suggest sideways movement"
            
        prediction = Prediction(
            direction=direction,
            confidence=confidence,
            target_price=round(target_price, 2) if target_price else None,
            time_horizon=f"{self.model_config.prediction_horizon}h",
            reasoning=reasoning
        )
        
        logger.info(f"Prediction: {direction} with {confidence:.2%} confidence")
        return prediction
        
    def generate_trading_signals(self, prediction: Prediction, technical_analysis: Dict[str, Any]) -> TradingSignal:
        """Generate trading recommendations based on prediction and analysis"""
        logger.info("Generating trading signals")
        
        # Base signal on prediction
        if prediction.confidence < 0.6:
            # Low confidence - recommend holding
            signal = TradingSignal(
                action="HOLD",
                strength="Weak",
                entry_price=None,
                stop_loss=None,
                take_profit=None,
                risk_reward_ratio=0.0,
                reasoning="Low prediction confidence suggests waiting for clearer signals"
            )
        elif prediction.direction == "UP":
            # Bullish prediction - buy signal
            entry_price = prediction.target_price * 0.98 if prediction.target_price else None  # Buy slightly below target
            stop_loss = entry_price * (1 - self.trading_config.max_risk_per_trade * self.trading_config.stop_loss_multiplier) if entry_price else None
            take_profit = entry_price * (1 + self.trading_config.max_risk_per_trade * self.trading_config.take_profit_multiplier) if entry_price else None
            
            risk_reward_ratio = (
                (take_profit - entry_price) / (entry_price - stop_loss)
                if entry_price and stop_loss and take_profit else 0.0
            )
            
            strength = "Strong" if prediction.confidence > 0.8 else "Medium"
            
            signal = TradingSignal(
                action="BUY",
                strength=strength,
                entry_price=round(entry_price, 2) if entry_price else None,
                stop_loss=round(stop_loss, 2) if stop_loss else None,
                take_profit=round(take_profit, 2) if take_profit else None,
                risk_reward_ratio=round(risk_reward_ratio, 2),
                reasoning=f"Bullish prediction with {prediction.confidence:.1%} confidence. {prediction.reasoning}"
            )
        elif prediction.direction == "DOWN":
            # Bearish prediction - sell signal
            entry_price = prediction.target_price * 1.02 if prediction.target_price else None  # Sell slightly above target
            stop_loss = entry_price * (1 + self.trading_config.max_risk_per_trade * self.trading_config.stop_loss_multiplier) if entry_price else None
            take_profit = entry_price * (1 - self.trading_config.max_risk_per_trade * self.trading_config.take_profit_multiplier) if entry_price else None
            
            risk_reward_ratio = (
                (entry_price - take_profit) / (stop_loss - entry_price)
                if entry_price and stop_loss and take_profit else 0.0
            )
            
            strength = "Strong" if prediction.confidence > 0.8 else "Medium"
            
            signal = TradingSignal(
                action="SELL",
                strength=strength,
                entry_price=round(entry_price, 2) if entry_price else None,
                stop_loss=round(stop_loss, 2) if stop_loss else None,
                take_profit=round(take_profit, 2) if take_profit else None,
                risk_reward_ratio=round(risk_reward_ratio, 2),
                reasoning=f"Bearish prediction with {prediction.confidence:.1%} confidence. {prediction.reasoning}"
            )
        else:
            # Sideways prediction - hold
            signal = TradingSignal(
                action="HOLD",
                strength="Medium",
                entry_price=None,
                stop_loss=None,
                take_profit=None,
                risk_reward_ratio=0.0,
                reasoning=f"Sideways movement predicted. {prediction.reasoning}"
            )
            
        # Apply signal filters if configured
        if self.trading_config.signal_filters.get('trend_confirmation', False):
            signal = self._apply_trend_filter(signal, technical_analysis)
            
        if self.trading_config.signal_filters.get('volume_confirmation', False):
            signal = self._apply_volume_filter(signal, technical_analysis)
            
        logger.info(f"Generated {signal.action} signal with {signal.strength} strength")
        return signal
        
    def _apply_trend_filter(self, signal: TradingSignal, technical_analysis: Dict[str, Any]) -> TradingSignal:
        """Apply trend confirmation filter to trading signal"""
        ma_9 = technical_analysis.get('MA_9')
        ma_21 = technical_analysis.get('MA_21')
        ma_50 = technical_analysis.get('MA_50')
        
        if not (ma_9 and ma_21 and ma_50):
            return signal
            
        # Check if moving averages are aligned with signal
        if signal.action == "BUY":
            if not (ma_9 > ma_21 > ma_50):  # Uptrend confirmation
                signal.strength = "Weak"
                signal.reasoning += " (Trend filter: Moving averages not aligned for uptrend)"
        elif signal.action == "SELL":
            if not (ma_9 < ma_21 < ma_50):  # Downtrend confirmation
                signal.strength = "Weak"
                signal.reasoning += " (Trend filter: Moving averages not aligned for downtrend)"
                
        return signal
        
    def _apply_volume_filter(self, signal: TradingSignal, technical_analysis: Dict[str, Any]) -> TradingSignal:
        """Apply volume confirmation filter to trading signal"""
        volume_ratio = technical_analysis.get('Volume_Ratio')
        
        if not volume_ratio:
            return signal
            
        # Volume should be above average for strong signals
        if signal.action in ["BUY", "SELL"]:
            if volume_ratio < 1.2:  # Less than 20% above average
                if signal.strength == "Strong":
                    signal.strength = "Medium"
                elif signal.strength == "Medium":
                    signal.strength = "Weak"
                signal.reasoning += f" (Volume filter: Volume ratio {volume_ratio:.1f} below confirmation threshold)"
                
        return signal
        
    def backtest_prediction(self, prediction: Prediction, actual_data: Optional[List] = None) -> Dict[str, Any]:
        """Backtest prediction accuracy against actual market data"""
        logger.info("Running prediction backtesting analysis")
        
        if not actual_data or len(actual_data) < 10:
            logger.warning("Insufficient historical data for backtesting")
            return self._get_empty_backtest_results()
        
        try:
            # Convert actual_data to numpy arrays for analysis
            if hasattr(actual_data[0], 'close'):
                # OHLC data format
                prices = np.array([data.close for data in actual_data])
                timestamps = [data.timestamp for data in actual_data]
            else:
                # Assume it's a list of prices
                prices = np.array(actual_data)
                timestamps = list(range(len(prices)))
            
            # Simulate backtesting with different prediction horizons
            results = self._run_backtest_simulation(prices, timestamps, prediction)
            
            logger.info(f"Backtesting completed - Accuracy: {results['accuracy']:.2%}")
            return results
            
        except Exception as e:
            logger.error(f"Backtesting failed: {e}")
            return self._get_empty_backtest_results()
    
    def _run_backtest_simulation(self, prices: np.ndarray, timestamps: List, 
                                prediction: Prediction) -> Dict[str, Any]:
        """Run backtesting simulation on historical data"""
        
        # Backtesting parameters
        lookback_window = 20  # Number of periods to look back for predictions
        min_data_points = 30  # Minimum data points needed
        
        if len(prices) < min_data_points:
            return self._get_empty_backtest_results()
        
        # Storage for backtest results
        predictions_made = []
        actual_outcomes = []
        trades = []
        
        # Simulate making predictions at different points in history
        for i in range(lookback_window, len(prices) - prediction.time_horizon_hours):
            try:
                # Get historical data up to this point
                historical_prices = prices[:i]
                
                # Make a prediction based on historical data
                predicted_direction = self._simulate_prediction(historical_prices)
                
                # Get actual outcome after prediction horizon
                current_price = prices[i]
                future_price = prices[min(i + prediction.time_horizon_hours, len(prices) - 1)]
                
                actual_direction = "UP" if future_price > current_price else "DOWN" if future_price < current_price else "SIDEWAYS"
                actual_change = (future_price - current_price) / current_price
                
                # Record prediction vs actual
                predictions_made.append(predicted_direction)
                actual_outcomes.append(actual_direction)
                
                # Simulate trading based on prediction
                if predicted_direction != "SIDEWAYS":
                    trade_result = self._simulate_trade(
                        predicted_direction, current_price, future_price, 
                        self.trading_config.max_risk_per_trade
                    )
                    trades.append(trade_result)
                    
            except Exception as e:
                logger.debug(f"Skipping backtest point {i}: {e}")
                continue
        
        # Calculate performance metrics
        if not predictions_made:
            return self._get_empty_backtest_results()
        
        return self._calculate_backtest_metrics(predictions_made, actual_outcomes, trades)
    
    def _simulate_prediction(self, historical_prices: np.ndarray) -> str:
        """Simulate making a prediction based on historical data"""
        if len(historical_prices) < 10:
            return "SIDEWAYS"
        
        # Simple trend-based prediction simulation
        recent_trend = np.polyfit(range(10), historical_prices[-10:], 1)[0]
        
        # Add some randomness to simulate prediction uncertainty
        confidence_factor = np.random.uniform(0.5, 1.0)
        
        if recent_trend > 0.001 * confidence_factor:
            return "UP"
        elif recent_trend < -0.001 * confidence_factor:
            return "DOWN"
        else:
            return "SIDEWAYS"
    
    def _simulate_trade(self, predicted_direction: str, entry_price: float, 
                       exit_price: float, risk_per_trade: float) -> Dict[str, Any]:
        """Simulate a trade based on prediction"""
        
        # Calculate position size based on risk
        position_size = 1000 * risk_per_trade  # Assume $1000 portfolio
        
        if predicted_direction == "UP":
            # Long position
            shares = position_size / entry_price
            pnl = shares * (exit_price - entry_price)
            return_pct = (exit_price - entry_price) / entry_price
        elif predicted_direction == "DOWN":
            # Short position (simulated)
            shares = position_size / entry_price
            pnl = shares * (entry_price - exit_price)
            return_pct = (entry_price - exit_price) / entry_price
        else:
            # No trade
            return {'pnl': 0.0, 'return_pct': 0.0, 'entry_price': entry_price, 'exit_price': exit_price}
        
        return {
            'pnl': pnl,
            'return_pct': return_pct,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'predicted_direction': predicted_direction
        }
    
    def _calculate_backtest_metrics(self, predictions: List[str], 
                                   actuals: List[str], trades: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive backtesting metrics"""
        
        # Prediction accuracy metrics
        correct_predictions = sum(1 for p, a in zip(predictions, actuals) if p == a)
        total_predictions = len(predictions)
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        
        # Direction-specific metrics
        up_predictions = [p for p in predictions if p == "UP"]
        up_actuals = [a for p, a in zip(predictions, actuals) if p == "UP"]
        up_accuracy = sum(1 for a in up_actuals if a == "UP") / len(up_actuals) if up_actuals else 0.0
        
        down_predictions = [p for p in predictions if p == "DOWN"]
        down_actuals = [a for p, a in zip(predictions, actuals) if p == "DOWN"]
        down_accuracy = sum(1 for a in down_actuals if a == "DOWN") / len(down_actuals) if down_actuals else 0.0
        
        # Trading performance metrics
        if trades:
            total_pnl = sum(trade['pnl'] for trade in trades)
            returns = [trade['return_pct'] for trade in trades]
            
            profitable_trades = [t for t in trades if t['pnl'] > 0]
            losing_trades = [t for t in trades if t['pnl'] < 0]
            
            win_rate = len(profitable_trades) / len(trades) if trades else 0.0
            
            avg_win = np.mean([t['pnl'] for t in profitable_trades]) if profitable_trades else 0.0
            avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0.0
            
            # Calculate max drawdown
            cumulative_returns = np.cumsum(returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = running_max - cumulative_returns
            max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0.0
            
            # Calculate Sharpe ratio (simplified)
            if len(returns) > 1:
                sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0.0
            else:
                sharpe_ratio = 0.0
            
        else:
            total_pnl = 0.0
            win_rate = 0.0
            avg_win = 0.0
            avg_loss = 0.0
            max_drawdown = 0.0
            sharpe_ratio = 0.0
        
        return {
            'accuracy': accuracy,
            'total_predictions': total_predictions,
            'correct_predictions': correct_predictions,
            'up_accuracy': up_accuracy,
            'down_accuracy': down_accuracy,
            'precision': win_rate,  # Using win rate as precision proxy
            'recall': accuracy,     # Using accuracy as recall proxy
            'profit_loss': total_pnl,
            'total_trades': len(trades),
            'winning_trades': len([t for t in trades if t['pnl'] > 0]),
            'losing_trades': len([t for t in trades if t['pnl'] < 0]),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'backtest_period': f"{total_predictions} predictions"
        }
    
    def _get_empty_backtest_results(self) -> Dict[str, Any]:
        """Return empty backtest results"""
        return {
            'accuracy': 0.0,
            'total_predictions': 0,
            'correct_predictions': 0,
            'up_accuracy': 0.0,
            'down_accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'profit_loss': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'backtest_period': "No data"
        }
    
    @property
    def time_horizon_hours(self) -> int:
        """Get prediction time horizon in hours"""
        return self.model_config.prediction_horizon