"""
Random utility functions for dynamic content generation in load testing.

Supports functions like:
- randomString(length) -> str
- randomInt(min, max, isString=false) -> int|str  
- randomFloat(min, max, decimals, pattern, separator, isString=false) -> float|str
- randomUuid() -> str

By default, randomInt and randomFloat return numeric values for proper JSON compatibility.
Use isString=true to force string output when needed.
"""

import random
import string
import uuid
import re
import json
from datetime import datetime, timedelta
from typing import Any, Union


class RandomFunctionProcessor:
    """Processes and executes random functions in strings."""
    
    def __init__(self):
        self.function_patterns = {
            'randomString': r'randomString\((\d+)\)',
            'randomInt': r'randomInt\(([^)]+)\)',
            'randomFloat': r'randomFloat\(([^)]+)\)',
            'randomUuid': r'randomUuid\(\)',
            'randomDatetime': r'randomDatetime\(([^)]*)\)'
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
    
    def _process_string(self, text: str) -> Union[str, int, float]:
        """Process a string and replace random function calls with their results."""
        if not isinstance(text, str):
            return text
        
        # Check if the entire string is just one function call
        original_text = text
        for func_name, pattern in self.function_patterns.items():
            match = re.fullmatch(pattern, text)
            if match:
                # If the entire string is just this function, return the raw result
                return self._execute_function(func_name, match)
        
        # If not a single function call, process normally and convert to string
        for func_name, pattern in self.function_patterns.items():
            text = re.sub(pattern, lambda m: str(self._execute_function(func_name, m)), text)
        
        return text
    
    def _execute_function(self, func_name: str, match: re.Match) -> Union[str, int, float]:
        """Execute a specific random function based on its name and parameters."""
        if func_name == 'randomString':
            length = int(match.group(1))
            return self.random_string(length)
        
        elif func_name == 'randomInt':
            params = match.group(1)
            return self.random_int(params)
        
        elif func_name == 'randomFloat':
            params = match.group(1)
            return self.random_float(params)
        
        elif func_name == 'randomUuid':
            return self.random_uuid()
        
        elif func_name == 'randomDatetime':
            params = match.group(1)
            return self.random_datetime(params)
        
        return match.group(0)  # Return original if function not found
    
    def random_string(self, length: int) -> str:
        """Generate a random string of specified length."""
        if length <= 0:
            return ""
        
        # Use letters and digits for random strings
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def random_int(self, params: str) -> Union[int, str]:
        """
        Generate a random integer based on parameters.
        
        Formats:
        - "min, max" -> random integer (returns int)
        - "min, max, isString=true" -> random integer as string (returns str)
        
        Examples:
        - "1, 10" -> 5 (int)
        - "1, 10, isString=true" -> "5" (str)
        """
        # Split and clean parameters
        parts = [p.strip() for p in params.split(',')]
        
        if len(parts) < 2:
            raise ValueError(f"randomInt requires at least 2 parameters: min, max. Got: {params}")
        
        min_val = int(parts[0])
        max_val = int(parts[1])
        
        # Check for isString parameter
        is_string = False
        for i in range(2, len(parts)):
            part = parts[i].strip()
            if part.lower() in ['isstring=true', 'isstring="true"', "isstring='true'"]:
                is_string = True
                break
        
        result = random.randint(min_val, max_val)
        return str(result) if is_string else result
    
    def random_float(self, params: str) -> Union[float, str]:
        """
        Generate a random float based on parameters.
        
        Formats:
        - "min, max, decimals" -> random float (returns float)
        - "min, max, decimals, **pattern" -> random float with fixed ending digits (returns float)
        - "min, max, decimals, separator" -> random float with custom decimal separator (returns str)
        - "min, max, decimals, isString=true" -> random float as string (returns str)
        - "min, max, decimals, **pattern, separator" -> random float with pattern and custom separator (returns str)
        - "min, max, decimals, **pattern, isString=true" -> random float with pattern as string (returns str)
        
        Examples:
        - "1, 10, 2" -> 1.23 (float)
        - "1, 10, 2, isString=true" -> "1.23" (str)
        - "1, 10, 2, ," -> "1,23" (str with comma separator)
        - "1, 10, 4, **00" -> 1.2300 (float)
        - "1, 10, 4, **00, isString=true" -> "1.2300" (str)
        - "1, 10, 4, **00, ," -> "1,2300" (str with comma separator)
        """
        # Split and clean parameters
        parts = [p.strip() for p in params.split(',')]
        
        if len(parts) < 3:
            raise ValueError(f"randomFloat requires at least 3 parameters: min, max, decimals. Got: {params}")
        
        min_val = float(parts[0])
        max_val = float(parts[1])
        decimals = int(parts[2])
        
        # Default values
        separator = "."
        pattern = None
        is_string = False
        
        # Parse optional parameters (pattern, separator, and/or isString)
        # Special handling for comma separator: double comma ",," means comma separator
        # Look for two consecutive empty parts which indicate ",,"
        for i in range(3, len(parts) - 1):
            if parts[i] == '' and parts[i + 1] == '':
                separator = ","
                is_string = True  # Custom separator forces string output
                break
        
        for i in range(3, len(parts)):
            part = parts[i].strip()
            if not part:  # Skip empty parts
                continue
            part_lower = part.lower()
            if part.startswith('**'):
                pattern = part[2:]  # Remove ** prefix
            elif part in [',', '.']:
                separator = part
                is_string = True  # Custom separator forces string output
            elif part_lower in ['isstring=true', 'isstring="true"', "isstring='true'"]:
                is_string = True
            else:
                # If it's not a pattern or isString, it might be a separator without quotes
                if len(part) == 1 and part in [',', '.']:
                    separator = part
                    is_string = True  # Custom separator forces string output
        
        # Generate base random float
        base_value = random.uniform(min_val, max_val)
        
        # Handle pattern for ending digits
        if pattern is not None:
            # Round to base decimals first
            base_rounded = round(base_value, decimals - len(pattern))
            
            # Add the pattern digits
            pattern_value = int(pattern) / (10 ** len(pattern))
            final_value = base_rounded + pattern_value
            
            # Ensure we don't exceed max_val
            if final_value > max_val:
                final_value = base_rounded - pattern_value
            
            result_float = round(final_value, decimals)
        else:
            result_float = round(base_value, decimals)
        
        # Return as float or string based on parameters
        if is_string or separator != ".":
            # Format the result with the specified separator
            result_str = f"{result_float:.{decimals}f}"
            if separator != ".":
                result_str = result_str.replace(".", separator)
            return result_str
        else:
            return result_float
    
    def random_uuid(self) -> str:
        """Generate a random UUID string."""
        return str(uuid.uuid4())
    
    def random_datetime(self, params: str) -> str:
        """
        Generate a random datetime based on parameters.
        
        Formats:
        - "" -> random datetime between now and 30 days from now
        - "start='2025-08-01', end='2025-08-20'" -> random datetime between dates
        - "format='YYYY-MM-DD'" -> format output (default: YYYY-MM-DD HH:mm:ss)
        - "start='...', end='...', format='...'" -> all parameters
        
        Examples:
        - "" -> "2025-08-15 14:30:25"
        - "format='YYYY-MM-DD'" -> "2025-08-15"
        - "start='2025-08-01', end='2025-08-20', format='YYYY-MM-DD'" -> "2025-08-12"
        """
        # Default values
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        date_format = 'YYYY-MM-DD HH:mm:ss'
        
        if params.strip():
            # Parse parameters
            # Remove extra spaces and split by comma
            param_parts = [p.strip() for p in params.split(',')]
            
            for part in param_parts:
                if 'start=' in part:
                    # Extract start date
                    start_str = part.split('start=')[1].strip().strip("'\"")
                    start_date = self._parse_datetime_string(start_str)
                elif 'end=' in part:
                    # Extract end date
                    end_str = part.split('end=')[1].strip().strip("'\"")
                    end_date = self._parse_datetime_string(end_str)
                elif 'format=' in part:
                    # Extract format
                    date_format = part.split('format=')[1].strip().strip("'\"")
        
        # Generate random datetime between start and end
        time_diff = end_date - start_date
        random_seconds = random.randint(0, int(time_diff.total_seconds()))
        random_datetime = start_date + timedelta(seconds=random_seconds)
        
        # Format the datetime
        return self._format_datetime(random_datetime, date_format)
    
    def _parse_datetime_string(self, date_str: str) -> datetime:
        """Parse a datetime string in various formats."""
        # Try different formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%d/%m/%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # If no format works, default to today
        return datetime.now()
    
    def _format_datetime(self, dt: datetime, format_str: str) -> str:
        """Format datetime according to specified format."""
        # Convert custom format to Python strftime format
        format_map = {
            'YYYY': '%Y',
            'MM': '%m',
            'DD': '%d',
            'HH': '%H',
            'mm': '%M',
            'ss': '%S'
        }
        
        python_format = format_str
        for custom, python in format_map.items():
            python_format = python_format.replace(custom, python)
        
        return dt.strftime(python_format)


# Global instance for easy access
random_processor = RandomFunctionProcessor()


def process_random_functions(value: Any) -> Any:
    """
    Convenience function to process random functions in any value.
    
    Args:
        value: The value to process (can be dict, list, string, or JSON string)
        
    Returns:
        The processed value with random functions executed
    """
    # If it's a string that looks like JSON, try to parse it first
    if isinstance(value, str):
        try:
            # Try to parse as JSON
            import json
            parsed = json.loads(value)
            processed = random_processor.process_value(parsed)
            return json.dumps(processed)
        except (json.JSONDecodeError, ValueError):
            # Not valid JSON, process as regular string
            return random_processor.process_value(value)
    else:
        return random_processor.process_value(value)
