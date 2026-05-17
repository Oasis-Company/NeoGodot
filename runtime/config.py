import os
from typing import Optional
from dotenv import load_dotenv


class ConfigError(Exception):
    pass


class ConfigManager:
    def __init__(self, env_path: Optional[str] = None):
        env_loaded = False
        if env_path and os.path.exists(env_path):
            load_dotenv(env_path)
            env_loaded = True
        else:
            default_env_path = os.path.join(os.path.dirname(__file__), ".env")
            if os.path.exists(default_env_path):
                load_dotenv(default_env_path)
                env_loaded = True
        
        self.host: str = os.getenv("HOST", "0.0.0.0")
        
        try:
            port_str = os.getenv("PORT", "8000")
            self.port: int = int(port_str)
            if self.port < 1 or self.port > 65535:
                raise ConfigError(f"Invalid PORT value: {port_str}, must be between 1 and 65535")
        except ValueError:
            raise ConfigError(f"Invalid PORT value: {port_str}, must be a valid integer")
        
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_log_levels:
            raise ConfigError(f"Invalid LOG_LEVEL: {log_level}, must be one of {valid_log_levels}")
        self.log_level: str = log_level
        
        self.version: str = os.getenv("VERSION", "1.0.0")
        
        allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
        self.allowed_origins: list = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key, default)


_config: Optional[ConfigManager] = None


def get_config(env_path: Optional[str] = None) -> ConfigManager:
    global _config
    if _config is None:
        _config = ConfigManager(env_path)
    return _config
