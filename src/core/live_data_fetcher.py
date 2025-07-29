"""
Live market data fetcher for real-time chart analysis
Integrates with free APIs to get OHLC data directly
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

from config.settings import AppSettings
from .chart_extractor import OHLCData, ChartData


@dataclass
class MarketDataRequest:
    """Request parameters for market data"""
    symbol: str
    period: str = "1mo"  # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    interval: str = "1h"  # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    source: str = "yahoo"  # yahoo, alpha_vantage, polygon


class LiveDataFetcher:
    """Fetches live market data from various APIs"""
    
    def __init__(self, settings: AppSettings):
        self.settings = settings
        
    def fetch_chart_data(self, request: MarketDataRequest) -> ChartData:
        """Fetch live chart data and convert to ChartData format"""
        logger.info(f"Fetching live data for {request.symbol} ({request.period}, {request.interval})")
        
        try:
            if request.source == "yahoo":
                return self._fetch_yahoo_data(request)
            else:
                raise ValueError(f"Unsupported data source: {request.source}")
                
        except Exception as e:
            logger.error(f"Failed to fetch live data: {e}")
            raise
            
    def _fetch_yahoo_data(self, request: MarketDataRequest) -> ChartData:
        """Fetch data from Yahoo Finance"""
        try:
            # Create ticker object
            ticker = yf.Ticker(request.symbol)
            
            # Get historical data
            hist = ticker.history(period=request.period, interval=request.interval)
            
            if hist.empty:
                raise ValueError(f"No data found for symbol: {request.symbol}")
                
            # Convert to OHLC data format
            ohlc_data = []
            for timestamp, row in hist.iterrows():
                ohlc = OHLCData(
                    timestamp=timestamp,
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume']) if 'Volume' in row else 0.0
                )
                ohlc_data.append(ohlc)
                
            # Calculate price levels
            current_price = float(hist['Close'].iloc[-1])
            high_price = float(hist['High'].max())
            low_price = float(hist['Low'].min())
            
            price_levels = {
                'current_price': current_price,
                'high_52w': high_price,
                'low_52w': low_price,
                'support_1': current_price * 0.95,
                'resistance_1': current_price * 1.05,
            }
            
            # Determine timeframe
            timeframe = self._map_interval_to_timeframe(request.interval)
            
            chart_data = ChartData(
                ohlc_data=ohlc_data,
                price_levels=price_levels,
                timeframe=timeframe,
                symbol=request.symbol.upper(),
                extraction_confidence=1.0  # Perfect confidence for API data
            )
            
            logger.info(f"Successfully fetched {len(ohlc_data)} data points for {request.symbol}")
            return chart_data
            
        except Exception as e:
            logger.error(f"Yahoo Finance API error: {e}")
            raise
            
    def _map_interval_to_timeframe(self, interval: str) -> str:
        """Map API interval to our timeframe format"""
        mapping = {
            '1m': '1m', '2m': '2m', '5m': '5m', '15m': '15m', '30m': '30m',
            '60m': '1h', '90m': '1h30m', '1h': '1h',
            '1d': '1d', '5d': '5d', '1wk': '1w', '1mo': '1M', '3mo': '3M'
        }
        return mapping.get(interval, interval)
        
    def get_available_symbols(self, query: str) -> List[Dict[str, str]]:
        """Search for available symbols"""
        try:
            # This is a simplified version - in reality you'd use a proper symbol search API
            common_symbols = {
                'AAPL': 'Apple Inc.',
                'GOOGL': 'Alphabet Inc.',
                'MSFT': 'Microsoft Corporation',
                'TSLA': 'Tesla Inc.',
                'AMZN': 'Amazon.com Inc.',
                'BTC-USD': 'Bitcoin USD',
                'ETH-USD': 'Ethereum USD',
                'SPY': 'SPDR S&P 500 ETF',
                'QQQ': 'Invesco QQQ Trust',
                'NVDA': 'NVIDIA Corporation'
            }
            
            results = []
            query_upper = query.upper()
            
            for symbol, name in common_symbols.items():
                if query_upper in symbol or query_upper in name.upper():
                    results.append({
                        'symbol': symbol,
                        'name': name,
                        'exchange': 'NASDAQ' if not symbol.endswith('-USD') else 'Crypto'
                    })
                    
            return results[:10]  # Limit to top 10 results
            
        except Exception as e:
            logger.error(f"Symbol search error: {e}")
            return []
            
    def validate_symbol(self, symbol: str) -> bool:
        """Validate if a symbol exists and has data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return 'symbol' in info or 'shortName' in info
        except:
            return False
            
    def get_market_status(self) -> Dict[str, str]:
        """Get current market status"""
        try:
            # Simple market hours check (US Eastern Time)
            now = datetime.now()
            
            # Basic market hours (simplified)
            if now.weekday() < 5:  # Monday to Friday
                if 9 <= now.hour < 16:  # 9 AM to 4 PM EST (simplified)
                    return {"status": "open", "message": "Market is open"}
                else:
                    return {"status": "closed", "message": "Market is closed"}
            else:
                return {"status": "closed", "message": "Weekend - Market closed"}
                
        except Exception as e:
            logger.error(f"Market status check error: {e}")
            return {"status": "unknown", "message": "Unable to determine market status"}


class TradingViewURLParser:
    """Parse TradingView URLs to extract chart parameters"""
    
    @staticmethod
    def parse_url(url: str) -> Optional[MarketDataRequest]:
        """Parse TradingView URL and extract parameters"""
        try:
            # Example: https://www.tradingview.com/chart/?symbol=NASDAQ:AAPL
            # This is a simplified parser - real implementation would be more robust
            
            if 'tradingview.com' not in url:
                return None
                
            # Extract symbol
            if 'symbol=' in url:
                symbol_part = url.split('symbol=')[1].split('&')[0]
                # Remove exchange prefix (e.g., NASDAQ:AAPL -> AAPL)
                symbol = symbol_part.split(':')[-1]
                
                return MarketDataRequest(
                    symbol=symbol,
                    period="1mo",
                    interval="1h",
                    source="yahoo"
                )
                
        except Exception as e:
            logger.error(f"URL parsing error: {e}")
            
        return None


# End of live data fetcher implementation