"""
Random functions for dynamic value generation in load testing.
Supports randomString, randomInt, randomFloat, randomUuid, and randomDatetime functions.
"""

import re
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Union, Dict, List


class RandomFunctionProcessor:
    """Processes random functions in strings and data structures with memory support."""
    
    def __init__(self):
        # Memory storage for named values
        self.memory = {}
        
        # Regex patterns for different function types (updated to support optional name parameter with both single and double quotes)
        self.patterns = {
            'randomString': r'randomString\((\d+)(?:,\s*name\s*=\s*(["\'])([^"\']+)\2)?\)',
            'randomInt': r'randomInt\((\d+),\s*(\d+)(?:,\s*name\s*=\s*(["\'])([^"\']+)\3)?\)',
            'randomFloat': r'randomFloat\((\d+(?:\.\d+)?),\s*(\d+(?:\.\d+)?),\s*(\d+)(?:,\s*\*\*(\d+))?(?:,\s*name\s*=\s*(["\'])([^"\']+)\5)?\)',
            'randomUuid': r'randomUuid\((?:name\s*=\s*(["\'])([^"\']+)\1)?\)',
            'randomDatetime': r'randomDatetime\((?:[^)]*)\)'
        }
    
    def generate_random_string(self, length: int) -> str:
        """Generate a random string of specified length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def generate_random_int(self, min_val: int, max_val: int) -> int:
        """Generate a random integer between min_val and max_val (inclusive)."""
        return random.randint(min_val, max_val)
    
    def generate_random_float(self, min_val: float, max_val: float, decimals: int, 
                            fixed_suffix: str = None) -> float:
        """
        Generate a random float between min_val and max_val with specified decimal places.
        
        Args:
            min_val: Minimum value
            max_val: Maximum value
            decimals: Number of decimal places
            fixed_suffix: Fixed suffix for last decimals (e.g., "00" or "05")
        """
        # Generate base random float
        base_value = random.uniform(min_val, max_val)
        
        if fixed_suffix is None:
            # Normal random float
            return round(base_value, decimals)
        else:
            # Apply fixed suffix to last decimals
            multiplier = 10 ** decimals
            int_part = int(base_value * multiplier)
            
            # Calculate how many digits to replace
            suffix_digits = len(fixed_suffix)
            
            # Remove last digits and append fixed suffix
            if suffix_digits > 0:
                divisor = 10 ** suffix_digits
                base_part = (int_part // divisor) * divisor
                suffix_value = int(fixed_suffix)
                final_int = base_part + suffix_value
            else:
                final_int = int_part
            
            return final_int / multiplier
    
    def generate_random_uuid(self) -> str:
        """Generate a random UUID."""
        return str(uuid.uuid4())
    
    def generate_random_datetime(self, start: str = None, end: str = None, format_str: str = None) -> str:
        """
        Generate a random datetime between start and end with specified format.
        
        Args:
            start: Start datetime string (default: 30 days ago)
            end: End datetime string (default: now)
            format_str: Output format string (default: '%Y-%m-%d %H:%M:%S')
        """
        # Default format
        if format_str is None:
            format_str = '%Y-%m-%d %H:%M:%S'
        
        # Parse format string from user-friendly to Python format
        format_str = self._convert_format_string(format_str)
        
        # Default time range (last 30 days to now)
        now = datetime.now()
        if start is None:
            start_dt = now - timedelta(days=30)
        else:
            start_dt = self._parse_datetime_string(start)
        
        if end is None:
            end_dt = now
        else:
            end_dt = self._parse_datetime_string(end)
        
        # Ensure start is before end
        if start_dt > end_dt:
            start_dt, end_dt = end_dt, start_dt
        
        # Generate random datetime between start and end
        time_diff = end_dt - start_dt
        random_seconds = random.uniform(0, time_diff.total_seconds())
        random_dt = start_dt + timedelta(seconds=random_seconds)
        
        return random_dt.strftime(format_str)
    
    def _convert_format_string(self, format_str: str) -> str:
        """Convert user-friendly format to Python datetime format."""
        # Common format conversions
        conversions = {
            'YYYY': '%Y',
            'YY': '%y',
            'MM': '%m',
            'mm': '%M',  # minutes
            'DD': '%d',
            'dd': '%d',
            'HH': '%H',
            'hh': '%I',
            'SS': '%S',
            'ss': '%S'
        }
        
        result = format_str
        for user_format, python_format in conversions.items():
            result = result.replace(user_format, python_format)
        
        return result
    
    def _parse_datetime_string(self, dt_string: str) -> datetime:
        """Parse datetime string using common formats."""
        common_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%m/%d/%Y',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y'
        ]
        
        for fmt in common_formats:
            try:
                return datetime.strptime(dt_string, fmt)
            except ValueError:
                continue
        
        # If no format works, try to parse as ISO format
        try:
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Unable to parse datetime string: {dt_string}")
    
    def remember_value(self, name: str, value: Any) -> Any:
        """Store a value in memory with the given name."""
        self.memory[name] = value
        return value
    
    def recall_value(self, name: str) -> Any:
        """Retrieve a value from memory by name, or None if not found."""
        return self.memory.get(name)
    
    def clear_memory(self, name: str = None):
        """Clear memory. If name is provided, clear only that entry, otherwise clear all."""
        if name:
            self.memory.pop(name, None)
        else:
            self.memory.clear()
    
    def process_random_string(self, match) -> str:
        """Process randomString function with optional memory."""
        length = int(match.group(1))
        name = match.group(3) if match.group(3) else None
        
        if name:
            # Check if we already have this value in memory
            remembered = self.recall_value(name)
            if remembered is not None:
                return str(remembered)
            # Generate new value and remember it
            value = self.generate_random_string(length)
            self.remember_value(name, value)
            return value
        else:
            # No memory, just generate
            return self.generate_random_string(length)
    
    def process_random_int(self, match) -> str:
        """Process randomInt function with optional memory."""
        min_val = int(match.group(1))
        max_val = int(match.group(2))
        name = match.group(4) if match.group(4) else None
        
        if name:
            # Check if we already have this value in memory
            remembered = self.recall_value(name)
            if remembered is not None:
                return str(remembered)
            # Generate new value and remember it
            value = self.generate_random_int(min_val, max_val)
            self.remember_value(name, value)
            return str(value)
        else:
            # No memory, just generate
            return str(self.generate_random_int(min_val, max_val))
    
    def process_random_float(self, match) -> str:
        """Process randomFloat function with optional memory."""
        min_val = float(match.group(1))
        max_val = float(match.group(2))
        decimals = int(match.group(3))
        fixed_suffix = match.group(4) if match.group(4) else None
        name = match.group(6) if match.group(6) else None
        
        if name:
            # Check if we already have this value in memory
            remembered = self.recall_value(name)
            if remembered is not None:
                return f"{float(remembered):.{decimals}f}"
            # Generate new value and remember it
            value = self.generate_random_float(min_val, max_val, decimals, fixed_suffix)
            self.remember_value(name, value)
            return f"{value:.{decimals}f}"
        else:
            # No memory, just generate
            result = self.generate_random_float(min_val, max_val, decimals, fixed_suffix)
            return f"{result:.{decimals}f}"
    
    def process_random_uuid(self, match) -> str:
        """Process randomUuid function with optional memory."""
        name = match.group(2) if match.group(2) else None
        
        if name:
            # Check if we already have this value in memory
            remembered = self.recall_value(name)
            if remembered is not None:
                return str(remembered)
            # Generate new value and remember it
            value = self.generate_random_uuid()
            self.remember_value(name, value)
            return value
        else:
            # No memory, just generate
            return self.generate_random_uuid()
    
    def process_random_datetime(self, match) -> str:
        """Process randomDatetime function with optional memory."""
        # Parse the function parameters manually
        params_str = match.group(0)[len('randomDatetime('):-1]  # Remove function name and parentheses
        
        # Default values
        start = None
        end = None
        format_str = None
        name = None
        
        # Parse parameters
        if params_str.strip():
            # Simple parameter parsing
            import re
            
            # Extract start parameter
            start_match = re.search(r'start\s*=\s*(["\'])([^"\']*)\1', params_str)
            if start_match:
                start = start_match.group(2)
            
            # Extract end parameter
            end_match = re.search(r'end\s*=\s*(["\'])([^"\']*)\1', params_str)
            if end_match:
                end = end_match.group(2)
            
            # Extract format parameter
            format_match = re.search(r'format\s*=\s*(["\'])([^"\']*)\1', params_str)
            if format_match:
                format_str = format_match.group(2)
            
            # Extract name parameter
            name_match = re.search(r'name\s*=\s*(["\'])([^"\']+)\1', params_str)
            if name_match:
                name = name_match.group(2)
        
        if name:
            # Check if we already have this value in memory
            remembered = self.recall_value(name)
            if remembered is not None:
                return str(remembered)
            # Generate new value and remember it
            value = self.generate_random_datetime(start, end, format_str)
            self.remember_value(name, value)
            return value
        else:
            # No memory, just generate
            return self.generate_random_datetime(start, end, format_str)
    
    def process_string(self, text: str) -> str:
        """Process a string and replace all random functions with generated values."""
        if not isinstance(text, str):
            return text
        
        result = text
        
        # Process each function type
        for func_name, pattern in self.patterns.items():
            if func_name == 'randomString':
                result = re.sub(pattern, self.process_random_string, result)
            elif func_name == 'randomInt':
                result = re.sub(pattern, self.process_random_int, result)
            elif func_name == 'randomFloat':
                result = re.sub(pattern, self.process_random_float, result)
            elif func_name == 'randomUuid':
                result = re.sub(pattern, self.process_random_uuid, result)
            elif func_name == 'randomDatetime':
                result = re.sub(pattern, self.process_random_datetime, result)
        
        return result
    
    def process_value(self, value: Any) -> Any:
        """Process any value (string, dict, list, etc.) and replace random functions."""
        if isinstance(value, str):
            return self.process_string(value)
        elif isinstance(value, dict):
            return {k: self.process_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.process_value(item) for item in value]
        else:
            return value
    
    def process_data(self, data: Union[Dict, List, str, Any]) -> Any:
        """Process any data structure and replace random functions."""
        return self.process_value(data)


# Global instance for easy access
random_processor = RandomFunctionProcessor()


def process_random_functions(data: Any) -> Any:
    """Convenience function to process random functions in any data structure."""
    return random_processor.process_data(data)
