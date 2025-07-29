"""
Application configuration and settings management
"""

from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import json
import os
from loguru import logger


class ModelConfig(BaseModel):
    """Machine learning model configuration"""
    pattern_recognition_model: str = "cnn_pattern_v1.h5"
    price_prediction_model: str = "lstm_predictor_v1.h5"
    ensemble_model: str = "ensemble_v1.pkl"
    confidence_threshold: float = Field(0.7, ge=0.0, le=1.0)
    prediction_horizon: int = Field(24, ge=1, le=168)  # hours
    
    

class TechnicalAnalysisConfig(BaseModel):
    """Technical analysis configuration"""
    indicators: Dict[str, bool] = {
        "rsi": True,
        "macd": True,
        "bollinger_bands": True,
        "moving_averages": True,
        "volume": True,
        "stochastic": True,
        "williams_r": True,
        "cci": False,
        "atr": False
    }
    rsi_period: int = Field(14, ge=2, le=50)
    macd_periods: tuple = (12, 26, 9)
    bb_period: int = Field(20, ge=5, le=50)
    bb_std_dev: float = Field(2.0, ge=1.0, le=3.0)
    ma_periods: list = [9, 21, 50, 200]
    

class TradingConfig(BaseModel):
    """Trading signal configuration"""
    risk_tolerance: str = Field("medium", pattern="^(low|medium|high)$")
    max_risk_per_trade: float = Field(0.02, ge=0.001, le=0.1)  # 2%
    stop_loss_multiplier: float = Field(2.0, ge=1.0, le=5.0)
    take_profit_multiplier: float = Field(3.0, ge=1.0, le=10.0)
    signal_filters: Dict[str, bool] = {
        "trend_confirmation": True,
        "volume_confirmation": True,
        "multiple_timeframe": False,
        "momentum_filter": True
    }
    

class UIConfig(BaseModel):
    """User interface configuration"""
    theme: str = Field("dark", pattern="^(light|dark|auto)$")
    window_geometry: Optional[tuple] = None
    recent_files_limit: int = Field(10, ge=1, le=50)
    auto_save_analysis: bool = True
    show_tooltips: bool = True
    animation_duration: int = Field(300, ge=0, le=1000)  # milliseconds
    

class AppSettings(BaseModel):
    """Main application settings"""
    
    # Application info
    app_version: str = "0.1.0"
    debug_mode: bool = False
    
    # UI settings
    dark_theme: bool = True
    window_width: int = Field(1200, ge=800, le=2560)
    window_height: int = Field(800, ge=600, le=1440)
    
    # File paths
    models_dir: Path = Path("data/models")
    cache_dir: Path = Path("data/cache")
    exports_dir: Path = Path("exports")
    logs_dir: Path = Path("logs")
    
    # Configuration objects
    ml_model_config: ModelConfig = ModelConfig()

    technical_config: TechnicalAnalysisConfig = TechnicalAnalysisConfig()
    trading_config: TradingConfig = TradingConfig()
    ui_config: UIConfig = UIConfig()
    
    # Performance settings
    max_concurrent_predictions: int = Field(3, ge=1, le=10)
    cache_predictions: bool = True
    auto_cleanup_cache: bool = True
    cache_retention_days: int = Field(7, ge=1, le=30)
    
    model_config = {"env_prefix": "CHARTPREDICTOR_", "case_sensitive": False}
        
    @field_validator('models_dir', 'cache_dir', 'exports_dir', 'logs_dir')
    @classmethod
    def ensure_path_exists(cls, v):
        """Create directory if it doesn't exist"""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v
        
    @classmethod
    def load_from_file(cls, config_path: str = "config.json") -> "AppSettings":
        """Load settings from JSON file"""
        config_file = Path(config_path)
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return cls(**config_data)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                logger.info("Using default configuration")
                
        # Return default config and save it
        default_config = cls()
        default_config.save_to_file(config_path)
        return default_config
        
    def save_to_file(self, config_path: str = "config.json") -> None:
        """Save settings to JSON file"""
        try:
            config_data = self.model_dump()
            # Convert Path objects to strings for JSON serialization
            for key, value in config_data.items():
                if isinstance(value, Path):
                    config_data[key] = str(value)
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, Path):
                            config_data[key][sub_key] = str(sub_value)
                            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, default=str)
            logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save config to {config_path}: {e}")
            
    def update_from_env(self) -> None:
        """Update settings from environment variables"""
        env_vars = {
            'CHARTPREDICTOR_DEBUG_MODE': 'debug_mode',
            'CHARTPREDICTOR_DARK_THEME': 'dark_theme',
            'CHARTPREDICTOR_MODELS_DIR': 'models_dir',
            'CHARTPREDICTOR_CACHE_DIR': 'cache_dir',
        }
        
        for env_var, setting_name in env_vars.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    # Handle boolean values
                    if setting_name in ['debug_mode', 'dark_theme']:
                        env_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    # Handle path values
                    elif setting_name.endswith('_dir'):
                        env_value = Path(env_value)
                        
                    setattr(self, setting_name, env_value)
                    logger.info(f"Updated {setting_name} from environment variable")
                except Exception as e:
                    logger.warning(f"Failed to set {setting_name} from env var {env_var}: {e}")


# Global settings instance
_settings_instance = None

def get_settings() -> AppSettings:
    """Get global settings instance"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = AppSettings.load_from_file()
        _settings_instance.update_from_env()
    return _settings_instance

def reload_settings() -> AppSettings:
    """Reload settings from file"""
    global _settings_instance
    _settings_instance = AppSettings.load_from_file()
    _settings_instance.update_from_env()
    return _settings_instance