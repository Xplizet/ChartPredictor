"""
Chart data extraction module
Calculates technical indicators for live market data analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logger.warning("TA-Lib not available. Using basic technical indicators implementation.")

from config.settings import AppSettings


@dataclass
class OHLCData:
    """OHLC (Open, High, Low, Close) data point"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass
class ChartData:
    """Container for extracted chart data"""
    ohlc_data: List[OHLCData]
    price_levels: Dict[str, float]  # Support/resistance levels
    timeframe: str  # e.g., "1h", "4h", "1d"
    symbol: str = "UNKNOWN"
    extraction_confidence: float = 0.0


class ChartExtractor:
    """Calculates technical indicators and performs market data analysis"""
    
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.tech_config = settings.technical_config
        
    def calculate_technical_indicators(self, chart_data: ChartData) -> Dict[str, Any]:
        """Calculate technical indicators from extracted OHLC data"""
        if not chart_data.ohlc_data:
            logger.warning("No OHLC data available for technical analysis")
            return {}
            
        logger.info("Calculating technical indicators")
        
        # Convert OHLC data to pandas DataFrame
        df = self._ohlc_to_dataframe(chart_data.ohlc_data)
        
        indicators = {}
        
        try:
            # Moving Averages
            if self.tech_config.indicators.get('moving_averages', False):
                for period in self.tech_config.ma_periods:
                    if len(df) >= period:
                        indicators[f'MA_{period}'] = df['close'].rolling(window=period).mean().iloc[-1]
                        
            # RSI
            if self.tech_config.indicators.get('rsi', False) and len(df) >= self.tech_config.rsi_period:
                if TALIB_AVAILABLE:
                    rsi_values = talib.RSI(df['close'].values, timeperiod=self.tech_config.rsi_period)
                    indicators['RSI'] = rsi_values[-1] if not np.isnan(rsi_values[-1]) else None
                else:
                    rsi_value = self._calculate_rsi_manual(df['close'], self.tech_config.rsi_period)
                    indicators['RSI'] = rsi_value
                
            # MACD
            if self.tech_config.indicators.get('macd', False):
                fast, slow, signal = self.tech_config.macd_periods
                if len(df) >= slow:
                    if TALIB_AVAILABLE:
                        macd, macd_signal, macd_hist = talib.MACD(
                            df['close'].values, fastperiod=fast, slowperiod=slow, signalperiod=signal
                        )
                        indicators['MACD'] = macd[-1] if not np.isnan(macd[-1]) else None
                        indicators['MACD_Signal'] = macd_signal[-1] if not np.isnan(macd_signal[-1]) else None
                        indicators['MACD_Histogram'] = macd_hist[-1] if not np.isnan(macd_hist[-1]) else None
                    else:
                        macd_data = self._calculate_macd_manual(df['close'], fast, slow, signal)
                        indicators.update(macd_data)
                    
            # Bollinger Bands
            if self.tech_config.indicators.get('bollinger_bands', False):
                if len(df) >= self.tech_config.bb_period:
                    if TALIB_AVAILABLE:
                        upper, middle, lower = talib.BBANDS(
                            df['close'].values,
                            timeperiod=self.tech_config.bb_period,
                            nbdevup=self.tech_config.bb_std_dev,
                            nbdevdn=self.tech_config.bb_std_dev
                        )
                        indicators['BB_Upper'] = upper[-1] if not np.isnan(upper[-1]) else None
                        indicators['BB_Middle'] = middle[-1] if not np.isnan(middle[-1]) else None
                        indicators['BB_Lower'] = lower[-1] if not np.isnan(lower[-1]) else None
                    else:
                        bb_data = self._calculate_bollinger_bands_manual(df['close'], self.tech_config.bb_period, self.tech_config.bb_std_dev)
                        indicators.update(bb_data)
                    
            # Volume indicators
            if self.tech_config.indicators.get('volume', False) and len(df) >= 10:
                indicators['Volume_MA'] = df['volume'].rolling(window=10).mean().iloc[-1]
                indicators['Volume_Ratio'] = df['volume'].iloc[-1] / indicators['Volume_MA']
                
            # Stochastic
            if self.tech_config.indicators.get('stochastic', False) and len(df) >= 14:
                if TALIB_AVAILABLE:
                    slowk, slowd = talib.STOCH(
                        df['high'].values, df['low'].values, df['close'].values,
                        fastk_period=14, slowk_period=3, slowd_period=3
                    )
                    indicators['Stoch_K'] = slowk[-1] if not np.isnan(slowk[-1]) else None
                    indicators['Stoch_D'] = slowd[-1] if not np.isnan(slowd[-1]) else None
                else:
                    stoch_data = self._calculate_stochastic_manual(df['high'], df['low'], df['close'])
                    indicators.update(stoch_data)
                
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            
        # Remove None values
        indicators = {k: v for k, v in indicators.items() if v is not None}
        
        logger.info(f"Calculated {len(indicators)} technical indicators")
        return indicators
        
    def _ohlc_to_dataframe(self, ohlc_data: List[OHLCData]) -> pd.DataFrame:
        """Convert OHLC data list to pandas DataFrame"""
        data = []
        for ohlc in ohlc_data:
            data.append({
                'timestamp': ohlc.timestamp,
                'open': ohlc.open,
                'high': ohlc.high,
                'low': ohlc.low,
                'close': ohlc.close,
                'volume': ohlc.volume
            })
            
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
        
    def validate_extracted_data(self, chart_data: ChartData) -> Dict[str, Any]:
        """Validate the quality of extracted chart data"""
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'quality_score': 0.0
        }
        
        # Check if we have any data
        if not chart_data.ohlc_data:
            validation_results['errors'].append("No OHLC data extracted")
            validation_results['is_valid'] = False
            return validation_results
            
        # Check for realistic price movements
        price_changes = []
        for i in range(1, len(chart_data.ohlc_data)):
            prev_close = chart_data.ohlc_data[i-1].close
            curr_open = chart_data.ohlc_data[i].open
            change_pct = abs(curr_open - prev_close) / prev_close
            price_changes.append(change_pct)
            
        # Flag unrealistic price jumps (>20% between consecutive points)
        extreme_changes = [x for x in price_changes if x > 0.20]
        if len(extreme_changes) > len(price_changes) * 0.1:  # More than 10% extreme changes
            validation_results['warnings'].append(
                f"High number of extreme price changes detected: {len(extreme_changes)}"
            )
            
        # Check OHLC consistency
        inconsistent_candles = 0
        for ohlc in chart_data.ohlc_data:
            if not (ohlc.low <= min(ohlc.open, ohlc.close) <= max(ohlc.open, ohlc.close) <= ohlc.high):
                inconsistent_candles += 1
                
        if inconsistent_candles > 0:
            validation_results['warnings'].append(
                f"Found {inconsistent_candles} candles with inconsistent OHLC values"
            )
            
        # Calculate quality score
        base_score = 1.0
        base_score -= len(extreme_changes) * 0.05  # Penalty for extreme changes
        base_score -= inconsistent_candles * 0.1   # Penalty for inconsistent candles
        base_score = max(0.0, min(1.0, base_score))  # Clamp between 0 and 1
        
        validation_results['quality_score'] = base_score
        
        if base_score < 0.5:
            validation_results['errors'].append("Data quality score below acceptable threshold")
            validation_results['is_valid'] = False
            
        logger.info(f"Data validation complete. Quality score: {base_score:.2f}")
        return validation_results
        
    def _calculate_rsi_manual(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate RSI manually without TA-Lib"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else None
        except Exception as e:
            logger.error(f"Error calculating RSI manually: {e}")
            return None
            
    def _calculate_macd_manual(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Optional[float]]:
        """Calculate MACD manually without TA-Lib"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            
            return {
                'MACD': round(macd_line.iloc[-1], 4) if not pd.isna(macd_line.iloc[-1]) else None,
                'MACD_Signal': round(signal_line.iloc[-1], 4) if not pd.isna(signal_line.iloc[-1]) else None,
                'MACD_Histogram': round(histogram.iloc[-1], 4) if not pd.isna(histogram.iloc[-1]) else None
            }
        except Exception as e:
            logger.error(f"Error calculating MACD manually: {e}")
            return {'MACD': None, 'MACD_Signal': None, 'MACD_Histogram': None}
            
    def _calculate_bollinger_bands_manual(self, prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> Dict[str, Optional[float]]:
        """Calculate Bollinger Bands manually without TA-Lib"""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            return {
                'BB_Upper': round(upper_band.iloc[-1], 2) if not pd.isna(upper_band.iloc[-1]) else None,
                'BB_Middle': round(sma.iloc[-1], 2) if not pd.isna(sma.iloc[-1]) else None,
                'BB_Lower': round(lower_band.iloc[-1], 2) if not pd.isna(lower_band.iloc[-1]) else None
            }
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands manually: {e}")
            return {'BB_Upper': None, 'BB_Middle': None, 'BB_Lower': None}
            
    def _calculate_stochastic_manual(self, high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Dict[str, Optional[float]]:
        """Calculate Stochastic oscillator manually without TA-Lib"""
        try:
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=d_period).mean()
            
            return {
                'Stoch_K': round(k_percent.iloc[-1], 2) if not pd.isna(k_percent.iloc[-1]) else None,
                'Stoch_D': round(d_percent.iloc[-1], 2) if not pd.isna(d_percent.iloc[-1]) else None
            }
        except Exception as e:
            logger.error(f"Error calculating Stochastic manually: {e}")
            return {'Stoch_K': None, 'Stoch_D': None}