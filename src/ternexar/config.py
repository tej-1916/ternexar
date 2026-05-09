import os
from pathlib import Path
import toml

CONFIG_DIR = Path.home() / ".config" / "ternexar"
CONFIG_FILE = CONFIG_DIR / "ternexar.toml"

DEFAULT_CONFIG = {
    "model": {
        "default": "gemma4:latest",
        "temperature": 0.7
    },
    "ui": {
        "show_splash": True
    },
    "workspaces": {
        "roots": []
    }
}

class ConfigManager:
    def __init__(self):
        self._config = None

    def ensure_config(self):
        """Ensures the config directory and file exist."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if not CONFIG_FILE.exists():
            self.save(DEFAULT_CONFIG)

    def load(self) -> dict:
        """Loads the configuration from file."""
        if not CONFIG_FILE.exists():
            self.ensure_config()
        
        try:
            with open(CONFIG_FILE, "r") as f:
                file_config = toml.load(f)
                # Merge file config with DEFAULT_CONFIG to handle missing keys
                self._config = DEFAULT_CONFIG.copy()
                for section, values in file_config.items():
                    if section in self._config:
                        self._config[section].update(values)
                    else:
                        self._config[section] = values
        except Exception:
            self._config = DEFAULT_CONFIG
        
        return self._config

    def save(self, config_data: dict):
        """Saves the configuration to file."""
        with open(CONFIG_FILE, "w") as f:
            toml.dump(config_data, f)
        self._config = config_data

    def get(self, section: str, key: str, default=None):
        """Gets a configuration value."""
        if self._config is None:
            self.load()
        return self._config.get(section, {}).get(key, default)

    def reset(self):
        """Resets the configuration to defaults."""
        self.save(DEFAULT_CONFIG)

config_manager = ConfigManager()
