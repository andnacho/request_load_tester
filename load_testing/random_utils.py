"""
Random utility functions for dynamic content generation in load testing.

Supports functions like:
- randomString(length)
- randomInt(min, max)
- randomFloat(min, max, decimals, pattern)
- randomUuid()
"""

import random
import string
import uuid
import re
from typing import Any, Dict, Union


class RandomFunctionProcessor:
    """Processes and executes random functions in strings."""
    
    def __init__(self):
        self.function_patterns = {
            'randomString': r'randomString\((\d+)\)',
            'randomInt': r'randomInt\((\d+),\s*(\d+)\)',
            'randomFloat': r'randomFloat\(([^)]+)\)',
            'randomUuid': r'randomUuid\(\)'
        }
    
    def process_value(self, value: Any) -> Any:
        """
        Process any value (string, dict, list, etc.) and replace random functions.
        
        Args:
            value: The value to process
            
        Returns:
            The processed value with random functions executed
        """
        if isinstance(value, str):
            return self._process_string(value)
        elif isinstance(value, dict):
            return {k: self.process_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.process_value(item) for item in value]
        else:
            return value
    
    def _process_string(self, text: str) -> str:
        """Process a string and replace random function calls with their results."""
        if not isinstance(text, str):
            return text
            
        # Process each function type
        for func_name, pattern in self.function_patterns.items():
            text = re.sub(pattern, lambda m: str(self._execute_function(func_name, m)), text)
        
        return text
    
    def _execute_function(self, func_name: str, match: re.Match) -> Union[str, int, float]:
        """Execute a specific random function based on its name and parameters."""
        if func_name == 'randomString':
            length = int(match.group(1))
            return self.random_string(length)
        
        elif func_name == 'randomInt':
            min_val = int(match.group(1))
            max_val = int(match.group(2))
            return self.random_int(min_val, max_val)
        
        elif func_name == 'randomFloat':
            params = match.group(1)
            return self.random_float(params)
        
        elif func_name == 'randomUuid':
            return self.random_uuid()
        
        return match.group(0)  # Return original if function not found
    
    def random_string(self, length: int) -> str:
        """Generate a random string of specified length."""
        if length <= 0:
            return ""
        
        # Use letters and digits for random strings
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def random_int(self, min_val: int, max_val: int) -> int:
        """Generate a random integer between min_val and max_val (inclusive)."""
        return random.randint(min_val, max_val)
    
    def random_float(self, params: str) -> float:
        """
        Generate a random float based on parameters.
        
        Formats:
        - "min, max, decimals" -> random float with specified decimal places
        - "min, max, decimals, **pattern" -> random float with fixed ending digits
        
        Examples:
        - "1, 10, 2" -> 1.23, 5.67, etc.
        - "1, 10, 4, **00" -> 1.2300, 5.6700, etc.
        - "1, 10, 4, **05" -> 1.2305, 5.6705, etc.
        """
        # Split and clean parameters
        parts = [p.strip() for p in params.split(',')]
        
        if len(parts) < 3:
            raise ValueError(f"randomFloat requires at least 3 parameters: min, max, decimals. Got: {params}")
        
        min_val = float(parts[0])
        max_val = float(parts[1])
        decimals = int(parts[2])
        
        # Generate base random float
        base_value = random.uniform(min_val, max_val)
        
        # Handle pattern for ending digits
        if len(parts) >= 4 and parts[3].startswith('**'):
            pattern = parts[3][2:]  # Remove ** prefix
            
            # Round to base decimals first
            base_rounded = round(base_value, decimals - len(pattern))
            
            # Add the pattern digits
            pattern_value = int(pattern) / (10 ** len(pattern))
            final_value = base_rounded + pattern_value
            
            # Ensure we don't exceed max_val
            if final_value > max_val:
                final_value = base_rounded - pattern_value
            
            return round(final_value, decimals)
        else:
            return round(base_value, decimals)
    
    def random_uuid(self) -> str:
        """Generate a random UUID string."""
        return str(uuid.uuid4())


# Global instance for easy access
random_processor = RandomFunctionProcessor()


def process_random_functions(value: Any) -> Any:
    """
    Convenience function to process random functions in any value.
    
    Args:
        value: The value to process
        
    Returns:
        The processed value with random functions executed
    """
    return random_processor.process_value(value)
