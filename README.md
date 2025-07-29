# ChartPredictor - Live Market Data Analysis & Trading Tool

## Overview
ChartPredictor is a professional desktop application that provides real-time market data analysis, advanced pattern detection, and intelligent trading signals. Built with modern Python technologies, it offers comprehensive technical analysis, price predictions, and risk management tools for traders and investors.

## 🚀 Key Features

### 📊 Live Market Data Analysis
- **Real-Time Data**: Fetch live OHLC data from Yahoo Finance API
- **Multi-Asset Support**: Stocks, cryptocurrencies, ETFs, forex, and commodities
- **Multiple Timeframes**: From 1-minute to weekly charts
- **Historical Data**: Access comprehensive historical market data
- **Data Validation**: Automatic data quality checks and cleansing

### 🔍 Advanced Technical Analysis
- **15+ Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, Stochastic, Williams %R, CCI, ATR, and more
- **Custom Calculations**: Manual fallback implementations when TA-Lib is unavailable
- **Real-Time Updates**: Indicators calculated instantly as new data arrives
- **Volume Analysis**: Volume-based indicators and confirmations
- **Trend Analysis**: Multi-timeframe trend detection and confirmation

### 🎯 Intelligent Pattern Recognition
- **Algorithmic Detection**: Real pattern detection using mathematical analysis
- **6 Pattern Types**: Double Tops/Bottoms, Head & Shoulders, Triangles, Breakouts, Trend Channels
- **Dynamic Confidence**: Data-driven confidence scoring based on pattern quality
- **Pattern Validation**: Multiple confirmation criteria for reliable signals
- **Visual Indicators**: Clear pattern identification and classification

### 💰 Smart Trading Signals
- **Risk-Based Sizing**: Intelligent position sizing based on account risk
- **Stop-Loss Calculations**: Automatic stop-loss and take-profit levels
- **Risk/Reward Ratios**: Optimal risk-to-reward ratio analysis
- **Signal Strength**: Multi-factor signal strength assessment
- **Trend Confirmation**: Signal filtering based on trend analysis
- **Volume Confirmation**: Volume-based signal validation

### 📈 Professional Analysis Tools
- **Backtesting Engine**: Test strategy performance on historical data
- **Performance Metrics**: Accuracy, win rate, Sharpe ratio, maximum drawdown
- **Trade Simulation**: Realistic trading simulation with P&L tracking
- **Statistical Analysis**: Comprehensive performance statistics
- **Risk Assessment**: Detailed risk analysis and exposure calculations

### 📄 Comprehensive Export System
- **JSON Export**: Structured data export for API integration
- **CSV Export**: Multiple CSV files (OHLC data, indicators, analysis summary)
- **PDF Reports**: Professional reports with charts, analysis, and recommendations
- **Customizable Formats**: Flexible export options for different use cases

### ⚙️ Advanced Configuration
- **Settings Dialog**: 5-tab comprehensive settings interface
- **Real-Time Updates**: Settings apply immediately without restart
- **Theme Support**: Dark, light, and auto themes with instant switching
- **Parameter Tuning**: Fine-tune analysis parameters and thresholds
- **Profile Management**: Save and load different configuration profiles

## 🛠️ Technology Stack

### Desktop Framework
- **PyQt6**: Modern, native GUI framework with professional styling
- **Python 3.9+**: Modern Python with type hints and async support

### Data & Analysis
- **yfinance**: Real-time market data from Yahoo Finance
- **NumPy/Pandas**: High-performance numerical computing and data analysis
- **TA-Lib**: Industry-standard technical analysis library (with manual fallbacks)
- **Pydantic**: Data validation and settings management with type safety

### Additional Libraries
- **Loguru**: Structured logging with rotation and filtering
- **ReportLab**: Professional PDF report generation
- **Matplotlib**: Chart visualization and analysis plotting

## 🏗️ Architecture

```
ChartPredictor/
├── src/
│   ├── main.py                    # Application entry point
│   ├── gui/                       # User interface components
│   │   ├── main_window.py         # Main application window
│   │   └── settings_dialog.py     # Advanced settings interface
│   ├── core/                      # Core business logic
│   │   ├── live_data_fetcher.py   # Real-time data acquisition
│   │   ├── chart_extractor.py     # Technical analysis engine
│   │   └── predictor.py           # Pattern detection & predictions
│   ├── models/                    # Data models and structures
│   │   └── market_data.py         # OHLC, patterns, signals models
│   ├── utils/                     # Utility functions
│   │   └── export_manager.py      # Export functionality
│   └── config/                    # Configuration management
│       └── settings.py            # Settings validation & persistence
├── data/                          # Data storage
├── exports/                       # Generated reports and exports
├── logs/                          # Application logs
└── docs/                          # Documentation
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+** installed on your system
- **4GB+ RAM** for optimal performance
- **Internet connection** for live market data

### Installation

```bash
# Clone the repository
git clone https://github.com/xplizet/ChartPredictor.git
cd ChartPredictor

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch the application
python src/main.py
```

### Basic Usage

1. **Launch ChartPredictor** and wait for the interface to load
2. **Enter a symbol** (e.g., AAPL, BTC-USD, EURUSD=X) in the symbol field
3. **Select timeframe and period** using the dropdown menus
4. **Click "Analyze"** to fetch data and run analysis
5. **Review results** in the comprehensive results panel
6. **Export reports** using File → Export Results
7. **Run backtests** using File → Run Backtest

## 📊 Supported Assets

### Stock Markets
- **US Stocks**: AAPL, MSFT, GOOGL, TSLA, etc.
- **International Stocks**: Global market support through Yahoo Finance
- **ETFs**: SPY, QQQ, VTI, and thousands more
- **Indices**: ^GSPC (S&P 500), ^IXIC (NASDAQ), ^DJI (Dow Jones)

### Cryptocurrencies
- **Major Pairs**: BTC-USD, ETH-USD, BNB-USD, ADA-USD
- **Stablecoins**: USDT-USD, USDC-USD, BUSD-USD
- **DeFi Tokens**: UNI-USD, LINK-USD, AAVE-USD

### Forex & Commodities
- **Currency Pairs**: EURUSD=X, GBPUSD=X, USDJPY=X
- **Commodities**: GC=F (Gold), CL=F (Crude Oil), SI=F (Silver)

## 🎯 Use Cases

### For Day Traders
- Real-time technical analysis with 1-5 minute data
- Quick pattern recognition for entry/exit signals
- Risk management with automatic stop-loss calculations
- Multi-timeframe confirmation for higher probability trades

### For Swing Traders
- Daily and 4-hour analysis for medium-term positions
- Pattern-based entry signals with defined targets
- Backtesting for strategy validation
- Export functionality for trade journaling

### For Investors
- Weekly and monthly trend analysis
- Long-term pattern recognition
- Risk assessment for portfolio positions
- Professional reports for investment documentation

### For Analysts
- Comprehensive technical analysis toolkit
- Data export for further analysis
- Backtesting capabilities for research
- Professional reporting for client presentations

## ⚠️ Important Notes

### Performance Considerations
- Analysis typically completes in 2-5 seconds
- Larger datasets (2+ years) may take longer to process
- Internet connection speed affects data fetching time
- Multiple concurrent analyses are handled efficiently

### Data Limitations
- Market data sourced from Yahoo Finance (delays may apply)
- Some assets may have limited historical data
- Data quality depends on Yahoo Finance data accuracy
- Real-time data subject to exchange reporting delays

## 🔧 Configuration

### Default Settings
ChartPredictor works great out of the box with sensible defaults:
- **Theme**: Dark mode for comfortable viewing
- **Confidence Threshold**: 60% for pattern detection
- **Risk Management**: 2% maximum risk per trade
- **Technical Indicators**: Standard periods (RSI 14, MACD 12/26/9)

### Customization
Access comprehensive settings via **Tools → Settings**:
- **Analysis Tab**: Technical indicator parameters
- **Trading Tab**: Risk management and signal filtering
- **Display Tab**: Theme, opacity, and UI preferences
- **Data Tab**: Data sources, caching, and timeouts
- **Advanced Tab**: Logging, performance, and export settings

## 📈 Getting Help

### Documentation
- **User Guide**: Complete feature walkthrough
- **API Reference**: Technical implementation details
- **Troubleshooting**: Common issues and solutions

### Support
- **GitHub Issues**: Bug reports and feature requests
- **Community Forum**: User discussions and tips

## 🤝 Contributing
We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License
This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer
**IMPORTANT**: ChartPredictor is for educational and informational purposes only.

- **Not Financial Advice**: Predictions and signals should not be considered as professional financial advice
- **Trading Risks**: All trading involves substantial risk of loss
- **Due Diligence**: Always conduct your own research and analysis
- **Professional Consultation**: Consult qualified financial advisors before making investment decisions
- **No Guarantees**: Past performance does not guarantee future results

## 🚀 What's Next?

Check out our [CHANGELOG.md](CHANGELOG.md) to see the latest updates and our development roadmap.

---

**Made with ❤️ for the trading community**

*Happy Trading! 📈*