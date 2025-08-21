"""
Load test results container and statistics.
"""

from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any, Optional


class LoadTestResults:
    """Container for load test results and statistics."""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = []
        self.error_counts = defaultdict(int)
        self.start_time = None
        self.end_time = None
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time."""
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0
    
    @property
    def min_response_time(self) -> float:
        """Get minimum response time."""
        return min(self.response_times) if self.response_times else 0
    
    @property
    def max_response_time(self) -> float:
        """Get maximum response time."""
        return max(self.response_times) if self.response_times else 0
    
    @property
    def requests_per_second(self) -> float:
        """Calculate requests per second."""
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            return self.total_requests / duration if duration > 0 else 0
        return 0
    
    @property
    def success_percentage(self) -> float:
        """Calculate success percentage."""
        return (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
    
    @property
    def failure_percentage(self) -> float:
        """Calculate failure percentage."""
        return (self.failed_requests / self.total_requests * 100) if self.total_requests > 0 else 0
    
    def print_results(self):
        """Print comprehensive test results."""
        print('\n' + '=' * 60)
        print('                    LOAD TEST RESULTS')
        print('=' * 60)
        print(f"Total Requests:       {self.total_requests}")
        print(f"Successful:           {self.successful_requests} ({self.success_percentage:.1f}%)")
        print(f"Failed:               {self.failed_requests} ({self.failure_percentage:.1f}%)")
        print(f"Requests/sec:         {self.requests_per_second:.2f}")
        print(f"Avg Response Time:    {self.average_response_time:.0f}ms")
        print(f"Min Response Time:    {self.min_response_time:.0f}ms")
        print(f"Max Response Time:    {self.max_response_time:.0f}ms")
        
        if self.error_counts:
            print('\nErrors:')
            for error, count in self.error_counts.items():
                print(f"  {count}x: {error}")
        
        print('=' * 60)
