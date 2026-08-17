# Configuration utilities
"""
Configuration loading and management utilities.
"""
import os
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from .env file.
    
    Args:
        config_path: Path to .env file (default: project root .env)
    
    Returns:
        Dictionary of configuration values
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / ".env"
    
    config = {}
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    
    return config


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_data_dir() -> Path:
    """Get the data directory."""
    return get_project_root() / "DATA"


def get_raw_data_dir() -> Path:
    """Get the raw data directory."""
    return get_data_dir() / "raw" / "CERT_R6.2" / "data"


def get_processed_data_dir() -> Path:
    """Get the processed data directory."""
    return get_data_dir() / "processed"


def get_features_dir() -> Path:
    """Get the features directory."""
    return get_data_dir() / "features"


def get_models_dir() -> Path:
    """Get the models directory."""
    return get_project_root() / "MODELS"


def get_output_dir() -> Path:
    """Get the output directory."""
    return get_project_root() / "OUTPUT"


def get_logs_dir() -> Path:
    """Get the logs directory."""
    return get_project_root() / "LOGS"
