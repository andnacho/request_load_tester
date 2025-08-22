"""
Core load testing functionality with async HTTP requests.
"""

import json
import time
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Any, Optional

from .config import ConfigLoader
from .templates import TemplateLoader, RequestTemplate
from .results import LoadTestResults


class LoadTester:
    """Main load testing class with async HTTP requests."""
    
    def __init__(self, config_loader: ConfigLoader = None, template_filter: str = None):
        self.config_loader = config_loader or ConfigLoader()
        self.template_loader = TemplateLoader(template_filter=template_filter)
        self.results = LoadTestResults()
        self.session: Optional[aiohttp.ClientSession] = None
    
    def get_random_template(self) -> RequestTemplate:
        """Get a random request template."""
        return self.template_loader.get_random_template()
    
    async def make_request(self, url: str, template: RequestTemplate, verbose: bool = False, 
                          show_request: bool = False, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a single HTTP request."""
        start_time = time.time()
        
        try:
            # Use provided config or default
            request_config = config or self.config_loader.config
            
            # Build headers from config
            headers = request_config.get('headers', {}).copy()
            headers['Content-Type'] = 'application/json'
            
            # Get method from config
            method = request_config.get('target', {}).get('method', 'POST').upper()
            
            # Get processed body with random functions
            processed_body = template.get_processed_body()
            
            # Make the request
            async with self.session.request(
                method=method,
                url=url,
                json=processed_body,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                response_body = await response.text()
                
                # Print request details if requested (after response to keep them together)
                if show_request:
                    print(f"\n--- Request Details ---", flush=True)
                    print(f"Template: {template.name} - {template.description}", flush=True)
                    print(f"Method: {method}", flush=True)
                    print(f"URL: {url}", flush=True)
                    print(f"Headers: {json.dumps(headers, indent=2)}", flush=True)
                    print(f"Body: {json.dumps(processed_body, indent=2)}", flush=True)
                    print(f"--- End Request ---\n", flush=True)
                
                # Log response details if verbose
                if verbose:
                    print(f"\n--- Response Details ---", flush=True)
                    print(f"Template Used: {template.name} - {template.description}", flush=True)
                    print(f"Status: {response.status}", flush=True)
                    print(f"Response Time: {response_time:.0f}ms", flush=True)
                    print(f"Headers: {json.dumps(dict(response.headers), indent=2)}", flush=True)
                    print(f"Body: {response_body}", flush=True)
                    print(f"--- End Response ---\n", flush=True)
                
                # Determine success
                success = 200 <= response.status < 400
                
                return {
                    'success': success,
                    'response_time': response_time,
                    'status_code': response.status,
                    'response_body': response_body,
                    'error': None if success else f"HTTP {response.status}: {response_body[:200]}"
                }
        
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return {
                'success': False,
                'response_time': response_time,
                'status_code': None,
                'response_body': '',
                'error': 'Request timeout'
            }
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                'success': False,
                'response_time': response_time,
                'status_code': None,
                'response_body': '',
                'error': str(e)
            }
    
    def update_results(self, result: Dict[str, Any]):
        """Update results with a single request result."""
        self.results.total_requests += 1
        self.results.response_times.append(result['response_time'])
        
        if result['success']:
            self.results.successful_requests += 1
        else:
            self.results.failed_requests += 1
            if result['error']:
                self.results.error_counts[result['error']] += 1
    
    async def run_test(self, config: Dict[str, Any]) -> LoadTestResults:
        """Run the load test with specified configuration."""
        print(f"Starting load test with {config['concurrent']} concurrent connections for {config['duration']} seconds")
        print(f"Target URL: {config['url']}")
        print(f"Max errors allowed: {config['max_errors']}")
        if config['delay'] > 0:
            print(f"Delay between requests: {config['delay']}s")
        print()
        
        self.results.start_time = datetime.now()
        
        # Create HTTP session
        connector = aiohttp.TCPConnector(limit=config['concurrent'] * 2)
        self.session = aiohttp.ClientSession(connector=connector)
        
        try:
            if config['delay'] > 0:
                # Sequential processing with delay
                await self._run_sequential_test(config)
            else:
                # Concurrent processing
                await self._run_concurrent_test(config)
        
        finally:
            await self.session.close()
            self.results.end_time = datetime.now()
        
        self.results.print_results()
        return self.results
    
    async def _run_sequential_test(self, config: Dict[str, Any]):
        """Run test with sequential requests and delay."""
        print(f"Using sequential processing with {config['delay']}s delay between requests")
        
        start_time = time.time()
        end_time = start_time + config['duration']
        
        while time.time() < end_time:
            # Check max errors
            if self.results.failed_requests >= config['max_errors']:
                print(f"\n⚠️  Stopping test: Maximum errors ({config['max_errors']}) reached")
                break
            
            # Make one request
            template = self.get_random_template()
            result = await self.make_request(
                config['url'], 
                template, 
                config['verbose'], 
                config.get('request', False),
                config['loaded_config']
            )
            self.update_results(result)
            
            # Progress logging
            if self.results.total_requests % 10 == 0:
                print(f"\rRequests completed: {self.results.total_requests} "
                      f"(Success: {self.results.successful_requests}, "
                      f"Failed: {self.results.failed_requests})", end='', flush=True)
            
            # Apply delay if we still have time
            if time.time() < end_time:
                await asyncio.sleep(config['delay'])
    
    async def _run_concurrent_test(self, config: Dict[str, Any]):
        """Run test with concurrent requests."""
        start_time = time.time()
        end_time = start_time + config['duration']
        
        # Semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(config['concurrent'])
        
        async def make_single_request():
            """Make a single request with semaphore control."""
            async with semaphore:
                template = self.get_random_template()
                result = await self.make_request(
                    config['url'], 
                    template, 
                    config['verbose'], 
                    config.get('request', False),
                    config['loaded_config']
                )
                self.update_results(result)
                
                # Progress logging
                if self.results.total_requests % 10 == 0:
                    print(f"\rRequests completed: {self.results.total_requests} "
                          f"(Success: {self.results.successful_requests}, "
                          f"Failed: {self.results.failed_requests})", end='', flush=True)
        
        # Start initial batch
        tasks = []
        for _ in range(config['concurrent']):
            task = asyncio.create_task(make_single_request())
            tasks.append(task)
        
        # Keep creating new tasks until time runs out or max errors hit
        while time.time() < end_time:
            # Check max errors
            if self.results.failed_requests >= config['max_errors']:
                print(f"\n⚠️  Stopping test: Maximum errors ({config['max_errors']}) reached")
                break
            
            # Wait for at least one task to complete
            if tasks:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                tasks = list(pending)
            
            # Start new tasks to maintain concurrency
            while len(tasks) < config['concurrent'] and time.time() < end_time:
                task = asyncio.create_task(make_single_request())
                tasks.append(task)
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.01)
        
        # Wait for remaining tasks
        if tasks:
            print('\n\nWaiting for remaining requests to complete...')
            await asyncio.gather(*tasks, return_exceptions=True)
