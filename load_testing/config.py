"""
Configuration loader with environment variable substitution and random functions.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any
from .random_functions import process_random_functions


class ConfigLoader:
    """Handles configuration loading with environment variable substitution."""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config_path = Path(__file__).parent.parent / config_path
        self.config = self.load_config()
        self._placeholder_vars = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load and parse the configuration file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return self.substitute_environment_variables(config)
        except FileNotFoundError:
            print(f"❌ Could not load config file {self.config_path}")
            print("💥 Config file is required! Please ensure config.json exists.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file {self.config_path}: {e}")
            sys.exit(1)
    
    def substitute_environment_variables(self, obj: Any, flags: Dict[str, str] = None) -> Any:
        """Recursively substitute environment variables and random functions in configuration."""
        if flags is None:
            flags = {}
        
        if isinstance(obj, str):
            # First process random functions
            result = process_random_functions(obj)
            
            # Then check for [[VARIABLE]] pattern (supports letters, numbers, and underscores)
            matches = re.findall(r'\[\[([A-Z_0-9]+)\]\]', result)
            if matches:
                for var_name in matches:
                    replacement = None
                    
                    # Priority: flag value > environment variable > keep placeholder
                    if var_name.lower() in flags:
                        replacement = flags[var_name.lower()]
                    else:
                        replacement = os.getenv(var_name)
                    
                    if replacement is not None:
                        result = result.replace(f'[[{var_name}]]', replacement)
                    else:
                        print(f"⚠️  Environment variable {var_name} not found, keeping placeholder")
                
                return result
            return result
        
        elif isinstance(obj, list):
            return [self.substitute_environment_variables(item, flags) for item in obj]
        
        elif isinstance(obj, dict):
            return {
                key: self.substitute_environment_variables(value, flags)
                for key, value in obj.items()
            }
        
        return obj
    
    def get_config(self, flags: Dict[str, str] = None) -> Dict[str, Any]:
        """Get configuration with current flags and environment variables."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw_config = json.load(f)
            return self.substitute_environment_variables(raw_config, flags or {})
        except Exception as e:
            print(f"❌ Could not re-load config file {self.config_path}: {e}")
            return self.config  # fallback to initial config
    
    def discover_placeholder_variables(self) -> List[str]:
        """Discover all [[VARIABLE]] placeholders in the config file."""
        if self._placeholder_vars is not None:
            return self._placeholder_vars
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_text = f.read()
            
            # Find all [[VARIABLE]] patterns (supports letters, numbers, and underscores)
            placeholder_matches = re.findall(r'\[\[([A-Z_0-9]+)\]\]', config_text)
            self._placeholder_vars = list(set(placeholder_matches))  # Remove duplicates
            return self._placeholder_vars
        except Exception as e:
            print(f"⚠️  Could not discover placeholders from {self.config_path}: {e}")
            return []
    
    def get_flag_name_from_placeholder(self, placeholder: str) -> str:
        """Convert a placeholder variable to a flag name."""
        # Convert API_KEY -> api-key, ORIGIN_HOST -> origin-host
        return placeholder.lower().replace('_', '-')
