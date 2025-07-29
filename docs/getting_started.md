# Getting Started with ChartPredictor

## Quick Start Guide

ChartPredictor is a professional desktop application that provides real-time market data analysis, advanced pattern detection, and intelligent trading signals. This guide will help you get up and running quickly with live market analysis.

## Installation

### Prerequisites

Before installing ChartPredictor, ensure you have:

- **Python 3.9 or later** installed on your system
- **4GB+ RAM** for optimal performance
- **Internet connection** for live market data
- **Modern operating system** (Windows 10+, macOS 10.14+, or Ubuntu 18.04+)

### Step 1: Clone the Repository

```bash
git clone https://github.com/xplizet/ChartPredictor.git
cd ChartPredictor
```

### Step 2: Set Up Virtual Environment (Recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install all required dependencies
pip install -r requirements.txt
```

### Step 4: Optional - Install TA-Lib

TA-Lib provides additional technical indicators (ChartPredictor includes manual fallbacks):

**Windows:**
```bash
# Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
# Install the downloaded .whl file
pip install TA_Lib-0.4.28-cp311-cp311-win_amd64.whl
```

**macOS:**
```bash
brew install ta-lib
pip install TA-Lib
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libta-lib-dev
pip install TA-Lib
```

*Note: If TA-Lib installation fails, ChartPredictor will use built-in implementations for all indicators.*

## First Launch

### Running the Application

```bash
python src/main.py
```

On first launch, ChartPredictor will:
- Create necessary directories (`logs/`, `data/`, `exports/`)
- Generate a default configuration file (`config.json`)
- Display the main application window with dark theme
- Initialize all analysis components

## Using ChartPredictor

### 1. Enter Market Symbol

In the main window, you'll see a **Symbol** input field. Enter any valid market symbol:

**Stock Examples:**
- `AAPL` - Apple Inc.
- `MSFT` - Microsoft Corporation
- `GOOGL` - Alphabet Inc.
- `TSLA` - Tesla Inc.

**Cryptocurrency Examples:**
- `BTC-USD` - Bitcoin
- `ETH-USD` - Ethereum
- `BNB-USD` - Binance Coin
- `ADA-USD` - Cardano

**ETF Examples:**
- `SPY` - S&P 500 ETF
- `QQQ` - NASDAQ 100 ETF
- `VTI` - Total Stock Market ETF

**Forex Examples:**
- `EURUSD=X` - Euro/US Dollar
- `GBPUSD=X` - British Pound/US Dollar

**Commodities Examples:**
- `GC=F` - Gold Futures
- `CL=F` - Crude Oil Futures
- `SI=F` - Silver Futures

### 2. Select Timeframe and Period

**Timeframe Options:**
- `1m` - 1 minute (intraday trading)
- `5m` - 5 minutes (scalping)
- `15m` - 15 minutes (short-term)
- `30m` - 30 minutes (short-term)
- `1h` - 1 hour (day trading)
- `4h` - 4 hours (swing trading)
- `1d` - 1 day (position trading)
- `1w` - 1 week (long-term)

**Period Options:**
- `1d` - 1 day of data
- `5d` - 5 days of data
- `1mo` - 1 month of data
- `3mo` - 3 months of data
- `6mo` - 6 months of data
- `1y` - 1 year of data
- `2y` - 2 years of data

### 3. Run Analysis

1. Click the **"Analyze"** button (or press `Ctrl+A`)
2. Watch the progress bar as ChartPredictor:
   - Fetches live market data
   - Calculates technical indicators
   - Detects chart patterns
   - Generates predictions
   - Creates trading signals
3. Analysis typically completes in 2-5 seconds

### 4. Review Results

The analysis results appear in organized sections:

#### Technical Analysis
- **15+ Indicators**: RSI, MACD, Bollinger Bands, Moving Averages, etc.
- **Current Values**: Real-time indicator calculations
- **Interpretations**: Bullish, bearish, or neutral signals

#### Chart Patterns
- **Detected Patterns**: Double tops/bottoms, head & shoulders, triangles, etc.
- **Confidence Levels**: Mathematical confidence scoring (0-100%)
- **Pattern Types**: Reversal, continuation, or neutral patterns
- **Descriptions**: Detailed pattern analysis

#### Price Predictions
- **Direction**: UP, DOWN, or SIDEWAYS prediction
- **Target Price**: Calculated target based on analysis
- **Confidence Level**: Prediction reliability (0-100%)
- **Time Horizon**: Expected timeframe for prediction
- **Reasoning**: Analysis methodology explanation

#### Trading Signals
- **Action**: BUY, SELL, or HOLD recommendation
- **Signal Strength**: Strong, Medium, or Weak
- **Entry Price**: Recommended entry level
- **Stop Loss**: Risk management exit level
- **Take Profit**: Profit target level
- **Risk/Reward Ratio**: Expected risk-to-reward ratio

## Advanced Features

### Export Analysis Results

1. **File → Export Results** (or `Ctrl+E`)
2. Choose format:
   - **JSON**: Structured data for APIs
   - **CSV**: Multiple spreadsheet files
   - **PDF**: Professional report
3. Select save location
4. View exported files

### Run Backtesting

1. **File → Run Backtest** (or `Ctrl+B`)
2. Wait for historical analysis
3. Review performance metrics:
   - Prediction accuracy
   - Win rate statistics
   - Risk metrics (Sharpe ratio, max drawdown)
   - Trade simulation results

### Customize Settings

1. **Tools → Settings** (or `Ctrl+,`)
2. Navigate through 5 tabs:
   - **📊 Analysis**: Technical indicator parameters
   - **💰 Trading**: Risk management settings
   - **🎨 Display**: Theme and UI preferences
   - **📁 Data**: Data sources and caching
   - **⚙️ Advanced**: Logging and performance
3. **Apply** changes (no restart required)

### Change Theme

1. Open **Tools → Settings**
2. Go to **🎨 Display** tab
3. Select **Theme**: Dark, Light, or Auto
4. Click **Apply** - theme changes instantly!

## Sample Workflow

### Example: Analyzing Apple Stock (AAPL)

1. **Enter Symbol**: Type `AAPL` in the symbol field
2. **Select Timeframe**: Choose `1h` for hourly analysis
3. **Select Period**: Choose `1mo` for one month of data
4. **Click Analyze**: Wait 2-3 seconds for results
5. **Review Results**:
   - Technical Analysis: RSI = 58, MACD bullish crossover
   - Patterns: Ascending triangle detected (78% confidence)
   - Prediction: UP direction, 72% confidence, target $185.50
   - Signal: BUY at $180.25, stop loss $175.00, take profit $188.00
6. **Export Report**: Save as PDF for records
7. **Run Backtest**: Validate strategy performance

### Example: Cryptocurrency Analysis (BTC-USD)

1. **Enter Symbol**: Type `BTC-USD`
2. **Select Timeframe**: Choose `4h` for swing trading
3. **Select Period**: Choose `3mo` for three months
4. **Analyze**: Review Bitcoin's technical patterns
5. **Export Data**: Save CSV files for spreadsheet analysis

## Configuration

### Settings File

ChartPredictor creates a `config.json` file with customizable settings:

```json
{
  "ui_config": {
    "theme": "dark",
    "window_geometry": null,
    "recent_files_limit": 10
  },
  "technical_config": {
    "rsi_period": 14,
    "macd_periods": [12, 26, 9],
    "bb_period": 20,
    "bb_std_dev": 2.0
  },
  "trading_config": {
    "risk_tolerance": "medium",
    "max_risk_per_trade": 0.02,
    "stop_loss_multiplier": 2.0
  },
  "ml_model_config": {
    "confidence_threshold": 0.6,
    "prediction_horizon": 4
  }
}
```

### Environment Variables

Configure ChartPredictor using environment variables:

```bash
export CHARTPREDICTOR_DEBUG_MODE=true
export CHARTPREDICTOR_THEME=light
export CHARTPREDICTOR_MODELS_DIR=/path/to/models
```

## Tips for Best Results

### Symbol Selection
- **Use Correct Format**: Follow Yahoo Finance symbol conventions
- **Check Liquidity**: Popular symbols have better data quality
- **Verify Trading Hours**: Some markets have limited hours

### Timeframe Selection
- **Day Trading**: Use 1m, 5m, 15m, 30m
- **Swing Trading**: Use 1h, 4h, 1d
- **Position Trading**: Use 1d, 1w
- **Match Period to Timeframe**: Longer periods for longer timeframes

### Data Quality
- **Market Hours**: Analysis during market hours provides better results
- **Recent Data**: Fresh data gives more accurate signals
- **Volume**: High-volume assets provide more reliable patterns

## Keyboard Shortcuts

- **Ctrl+A**: Analyze current symbol
- **Ctrl+E**: Export results
- **Ctrl+B**: Run backtest
- **Ctrl+,**: Open settings
- **F5**: Refresh analysis
- **Ctrl+Q**: Quit application

## Troubleshooting

### Common Issues

**"No data found for symbol"**
- Check symbol spelling and format
- Verify the symbol exists on Yahoo Finance
- Try alternative symbol formats (e.g., add -USD for crypto)

**"Failed to fetch data"**
- Check internet connection
- Verify Yahoo Finance is accessible
- Try a different symbol to test connectivity

**"Analysis failed"**
- Check logs in `logs/chartpredictor.log`
- Ensure sufficient historical data exists
- Try a shorter analysis period

**Slow Performance**
- Use shorter time periods for analysis
- Close other resource-intensive applications
- Check available RAM (4GB+ recommended)

### Error Logging

ChartPredictor maintains detailed logs in the `logs/` directory:
- `chartpredictor.log` - Main application log
- Debug information for troubleshooting
- Error details with timestamps

## Getting Help

### Documentation
- **README.md**: Overview and features
- **PROJECT_SUMMARY.md**: Technical implementation details
- **CHANGELOG.md**: Recent updates and changes

### Support Channels
- **GitHub Issues**: Report bugs and request features
- **Community Discussions**: User tips and strategies
- **Email Support**: support@chartpredictor.com (if available)

### Contributing
- See **CONTRIBUTING.md** for development guidelines
- Fork the repository for improvements
- Submit pull requests for bug fixes and features

## Legal Disclaimer

**⚠️ IMPORTANT**: ChartPredictor is for educational and informational purposes only.

- **Not Financial Advice**: All analysis and signals are educational tools
- **Trading Risks**: Trading involves substantial risk of financial loss
- **Due Diligence**: Always conduct your own research and analysis
- **Professional Advice**: Consult qualified financial advisors before trading
- **No Guarantees**: Past performance does not predict future results

## Next Steps

Once you're comfortable with the basics:

1. **Experiment** with different symbols and timeframes
2. **Customize** settings for your trading style
3. **Use Backtesting** to validate strategies
4. **Export Reports** for record keeping
5. **Integrate** into your trading workflow
6. **Share Feedback** to help improve the application

### Pro Tips

- Start with well-known symbols like AAPL, SPY, or BTC-USD
- Use longer timeframes (1h, 4h, 1d) for more reliable patterns
- Always review backtesting results before relying on signals
- Export analysis for later review and learning
- Customize settings gradually as you learn the application

Happy Trading! 📈

---

*For the latest updates and features, check our [CHANGELOG.md](../CHANGELOG.md)*