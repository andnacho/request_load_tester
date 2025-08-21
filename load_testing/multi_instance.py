#!/usr/bin/env python3
"""
Multiple Instance Load Tester for API Endpoints

A Python-based multi-instance load testing orchestrator that:
- Runs multiple load testing instances in parallel
- Aggregates results from all instances
- Provides comprehensive reporting
- Works cross-platform (Windows, Mac, Linux)
"""

import os
import sys
import json
import time
import asyncio
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ProcessPoolExecutor
import signal


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color


class LoadTestInstance:
    """Represents a single load test instance."""
    
    def __init__(self, instance_id: int, config: Dict[str, Any]):
        self.instance_id = instance_id
        self.config = config
        self.log_file = None
        self.process = None
        self.return_code = None
        self.results = {}
    
    def get_command(self) -> List[str]:
        """Build the command to run the load tester."""
        script_path = Path(__file__).parent.parent / 'start.py'
        
        cmd = [
            sys.executable, str(script_path),
            'single',
            str(self.config['concurrent']),
            str(self.config['duration']),
            '--url', self.config['url']
        ]
        
        # Add flags
        if self.config.get('max_errors'):
            cmd.extend(['--max-errors', str(self.config['max_errors'])])
        
        if self.config.get('delay', 0) > 0:
            cmd.extend(['--delay', str(self.config['delay'])])
        
        if self.config.get('verbose'):
            cmd.append('--verbose')
        
        if self.config.get('debug'):
            cmd.append('--debug')
        
        # Add dynamic config flags
        for key, value in self.config.get('dynamic_flags', {}).items():
            flag_name = key.replace('_', '-')
            cmd.extend([f'--{flag_name}', str(value)])
        
        return cmd
    
    async def run(self, results_dir: Path) -> Dict[str, Any]:
        """Run this load test instance."""
        self.log_file = results_dir / f'instance_{self.instance_id}.log'
        cmd = self.get_command()
        
        try:
            # Run the subprocess
            with open(self.log_file, 'w', encoding='utf-8') as f:
                self.process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=Path(__file__).parent.parent
                )
                
                self.return_code = await self.process.wait()
            
            # Parse results from log file
            self.results = self._parse_results()
            
            return {
                'instance_id': self.instance_id,
                'success': self.return_code == 0,
                'return_code': self.return_code,
                'log_file': str(self.log_file),
                'results': self.results
            }
        
        except Exception as e:
            return {
                'instance_id': self.instance_id,
                'success': False,
                'error': str(e),
                'log_file': str(self.log_file) if self.log_file else None,
                'results': {}
            }
    
    def _parse_results(self) -> Dict[str, Any]:
        """Parse results from the log file."""
        if not self.log_file or not self.log_file.exists():
            return {}
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            results = {}
            
            # Extract key metrics using regex
            import re
            
            patterns = {
                'total_requests': r'Total Requests:\s*(\d+)',
                'successful': r'Successful:\s*(\d+)\s*\(([^)]+)\)',
                'failed': r'Failed:\s*(\d+)\s*\(([^)]+)\)',
                'requests_per_sec': r'Requests/sec:\s*([\d.]+)',
                'avg_response_time': r'Avg Response Time:\s*(\d+)ms',
                'min_response_time': r'Min Response Time:\s*(\d+)ms',
                'max_response_time': r'Max Response Time:\s*(\d+)ms'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, content)
                if match:
                    if key in ['successful', 'failed']:
                        results[key] = int(match.group(1))
                        results[f'{key}_percentage'] = match.group(2)
                    elif key == 'requests_per_sec':
                        results[key] = float(match.group(1))
                    else:
                        results[key] = int(match.group(1))
            
            # Extract errors
            errors_section = re.search(r'Errors:\s*\n((?:.*\n)*?)=+', content)
            if errors_section:
                error_lines = errors_section.group(1).strip().split('\n')
                results['errors'] = []
                for line in error_lines:
                    if line.strip():
                        results['errors'].append(line.strip())
            
            return results
        
        except Exception as e:
            print(f"⚠️  Could not parse results for instance {self.instance_id}: {e}")
            return {}


class MultiInstanceLoadTester:
    """Orchestrates multiple load testing instances."""
    
    def __init__(self):
        self.instances: List[LoadTestInstance] = []
        self.results_dir: Optional[Path] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.interrupted = False
    
    def create_instances(self, config: Dict[str, Any]) -> None:
        """Create load test instances based on configuration."""
        base_config = {
            'url': config['url'],
            'concurrent': config['concurrent_per_instance'],
            'duration': config['duration'],
            'max_errors': config.get('max_errors', 10),
            'delay': config.get('delay', 0),
            'verbose': config.get('verbose', False),
            'debug': config.get('debug', False),
            'dynamic_flags': config.get('dynamic_flags', {})
        }
        
        self.instances = []
        for i in range(1, config['instances'] + 1):
            instance = LoadTestInstance(i, base_config.copy())
            self.instances.append(instance)
    
    def setup_results_directory(self) -> Path:
        """Create and setup the results directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = Path(__file__).parent.parent / f'load_test_results_{timestamp}'
        self.results_dir.mkdir(exist_ok=True)
        return self.results_dir
    
    def print_configuration(self, config: Dict[str, Any]) -> None:
        """Print test configuration."""
        print(f"{Colors.BLUE}{'=' * 50}")
        print("  Python Multi-Instance Load Tester")
        print(f"{'=' * 50}{Colors.NC}")
        print(f"URL: {config['url']}")
        print(f"Instances: {config['instances']}")
        print(f"Concurrent per instance: {config['concurrent_per_instance']}")
        print(f"Duration: {config['duration']} seconds")
        print(f"Total concurrent requests: {config['instances'] * config['concurrent_per_instance']}")
        print(f"Max Errors: {config.get('max_errors', 10)}")
        print(f"Delay: {config.get('delay', 0)}s")
        
        if config.get('verbose'):
            print(f"Verbose: {Colors.GREEN}enabled{Colors.NC}")
        else:
            print("Verbose: disabled")
        
        if config.get('debug'):
            print(f"Debug: {Colors.GREEN}enabled{Colors.NC}")
        else:
            print("Debug: disabled")
        print()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            print(f"\n{Colors.YELLOW}Received interrupt signal. Stopping all instances...{Colors.NC}")
            self.interrupted = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the multi-instance load test."""
        self.print_configuration(config)
        self.create_instances(config)
        self.setup_results_directory()
        self.setup_signal_handlers()
        
        # Check dependencies
        self._check_dependencies()
        
        print(f"{Colors.GREEN}Starting {config['instances']} instances...{Colors.NC}")
        print()
        
        self.start_time = datetime.now()
        
        # Start all instances concurrently
        tasks = []
        for instance in self.instances:
            print(f"{Colors.BLUE}Starting instance {instance.instance_id}...{Colors.NC}")
            task = asyncio.create_task(instance.run(self.results_dir))
            tasks.append(task)
            
            # Small delay between starting instances
            await asyncio.sleep(0.5)
        
        print()
        print(f"{Colors.YELLOW}All instances started. Waiting for completion...{Colors.NC}")
        print(f"{Colors.YELLOW}Monitor progress in: {self.results_dir}{Colors.NC}")
        print()
        
        # Wait for all instances to complete
        results = []
        try:
            for i, task in enumerate(asyncio.as_completed(tasks)):
                result = await task
                instance_id = result['instance_id']
                
                if result['success']:
                    print(f"{Colors.GREEN}Instance {instance_id} completed successfully{Colors.NC}")
                else:
                    print(f"{Colors.RED}Instance {instance_id} failed{Colors.NC}")
                
                results.append(result)
        
        except asyncio.CancelledError:
            print(f"{Colors.YELLOW}Tests were interrupted{Colors.NC}")
        
        self.end_time = datetime.now()
        
        # Generate summary
        summary = self._generate_summary(results, config)
        self._print_summary(summary)
        self._save_summary(summary)
        
        return summary
    
    def _check_dependencies(self):
        """Check that required files exist."""
        load_tester_path = Path(__file__).parent.parent / 'start.py'
        templates_path = Path(__file__).parent.parent / 'request-templates.json'
        config_path = Path(__file__).parent.parent / 'config.json'
        
        if not load_tester_path.exists():
            print(f"{Colors.RED}Error: start.py not found{Colors.NC}")
            sys.exit(1)
        
        if not templates_path.exists():
            print(f"{Colors.RED}Error: request-templates.json not found{Colors.NC}")
            sys.exit(1)
        
        if not config_path.exists():
            print(f"{Colors.YELLOW}Warning: config.json not found{Colors.NC}")
        
        print(f"{Colors.GREEN}✓ Dependencies checked{Colors.NC}")
    
    def _generate_summary(self, results: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive summary of all test results."""
        successful_instances = [r for r in results if r['success']]
        failed_instances = [r for r in results if not r['success']]
        
        # Aggregate metrics
        total_requests = sum(r.get('results', {}).get('total_requests', 0) for r in successful_instances)
        total_successful = sum(r.get('results', {}).get('successful', 0) for r in successful_instances)
        total_failed = sum(r.get('results', {}).get('failed', 0) for r in successful_instances)
        
        # Calculate averages
        response_times = []
        requests_per_sec = []
        
        for result in successful_instances:
            instance_results = result.get('results', {})
            if 'avg_response_time' in instance_results:
                response_times.append(instance_results['avg_response_time'])
            if 'requests_per_sec' in instance_results:
                requests_per_sec.append(instance_results['requests_per_sec'])
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        total_rps = sum(requests_per_sec)
        
        # Test duration
        test_duration = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
        
        return {
            'test_config': config,
            'execution_info': {
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration_seconds': test_duration,
                'results_directory': str(self.results_dir)
            },
            'instances': {
                'total': len(self.instances),
                'successful': len(successful_instances),
                'failed': len(failed_instances)
            },
            'aggregated_metrics': {
                'total_requests': total_requests,
                'successful_requests': total_successful,
                'failed_requests': total_failed,
                'success_percentage': (total_successful / total_requests * 100) if total_requests > 0 else 0,
                'average_response_time_ms': avg_response_time,
                'total_requests_per_second': total_rps,
                'theoretical_max_concurrent': config['instances'] * config['concurrent_per_instance']
            },
            'instance_results': results
        }
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print the test summary."""
        print(f"\n{Colors.BLUE}{'=' * 50}")
        print("              MULTI-INSTANCE SUMMARY")
        print(f"{'=' * 50}{Colors.NC}")
        
        # Instance summary
        instances = summary['instances']
        print(f"Total instances: {instances['total']}")
        print(f"Successful: {instances['successful']}")
        print(f"Failed: {instances['failed']}")
        print()
        
        # Aggregated metrics
        metrics = summary['aggregated_metrics']
        print("Aggregated Metrics:")
        print(f"  Total Requests: {metrics['total_requests']}")
        print(f"  Successful: {metrics['successful_requests']} ({metrics['success_percentage']:.1f}%)")
        print(f"  Failed: {metrics['failed_requests']}")
        print(f"  Avg Response Time: {metrics['average_response_time_ms']:.0f}ms")
        print(f"  Total RPS: {metrics['total_requests_per_second']:.2f}")
        print(f"  Max Concurrent: {metrics['theoretical_max_concurrent']}")
        print()
        
        # Individual instance results
        print(f"{Colors.YELLOW}Individual Instance Results:{Colors.NC}")
        for result in summary['instance_results']:
            instance_id = result['instance_id']
            if result['success']:
                instance_results = result.get('results', {})
                print(f"\n{Colors.BLUE}Instance {instance_id}:{Colors.NC}")
                print(f"  Requests: {instance_results.get('total_requests', 'N/A')}")
                print(f"  Success Rate: {instance_results.get('successful_percentage', 'N/A')}")
                print(f"  Avg Response Time: {instance_results.get('avg_response_time', 'N/A')}ms")
                print(f"  RPS: {instance_results.get('requests_per_sec', 'N/A')}")
            else:
                print(f"\n{Colors.RED}Instance {instance_id}: FAILED{Colors.NC}")
                if 'error' in result:
                    print(f"  Error: {result['error']}")
        
        print(f"\n{Colors.BLUE}Results saved in: {summary['execution_info']['results_directory']}{Colors.NC}")
        
        if instances['failed'] > 0:
            print(f"{Colors.RED}Some instances failed. Check log files for details.{Colors.NC}")
        else:
            print(f"{Colors.GREEN}All instances completed successfully!{Colors.NC}")
    
    def _save_summary(self, summary: Dict[str, Any]):
        """Save summary to JSON file."""
        if self.results_dir:
            summary_file = self.results_dir / 'summary.json'
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            print(f"{Colors.CYAN}Summary saved to: {summary_file}{Colors.NC}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run multiple load testing instances')
    
    parser.add_argument('instances', nargs='?', type=int, default=3,
                       help='Number of instances to run (default: 3)')
    parser.add_argument('concurrent_per_instance', nargs='?', type=int, default=5,
                       help='Concurrent requests per instance (default: 5)')
    parser.add_argument('duration', nargs='?', type=int, default=30,
                       help='Test duration in seconds (default: 30)')
    
    parser.add_argument('--url', default='https://api.example.com/v1/endpoint',
                       help='Target URL (default: from config or api.example.com)')
    parser.add_argument('--max-errors', type=int, default=10,
                       help='Maximum errors per instance (default: 10)')
    parser.add_argument('--delay', type=float, default=0,
                       help='Delay between requests in seconds (default: 0)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    
    # Dynamic config flags (auto-detected from config.json placeholders)
    try:
        from .config import ConfigLoader
        config_loader = ConfigLoader()
        placeholder_vars = config_loader.discover_placeholder_variables()
        for var in placeholder_vars:
            flag_name = config_loader.get_flag_name_from_placeholder(var)
            parser.add_argument(f'--{flag_name}', help=f'Value for [[{var}]] in config.json')
    except Exception as e:
        # Fallback for common flags if config discovery fails
        parser.add_argument('--api-key', help='API key for authorization')
        parser.add_argument('--origin-host', help='Origin host for requests')
        parser.add_argument('--referer-host', help='Referer host for requests')
    
    return parser.parse_args()


async def main():
    """Main function."""
    args = parse_arguments()
    
    # Build dynamic flags dynamically from discovered placeholders
    dynamic_flags = {}
    try:
        from .config import ConfigLoader
        config_loader = ConfigLoader()
        placeholder_vars = config_loader.discover_placeholder_variables()
        
        # For each placeholder, check if there's a corresponding command line argument
        for placeholder_var in placeholder_vars:
            flag_name = config_loader.get_flag_name_from_placeholder(placeholder_var)
            arg_name = flag_name.replace('-', '_')  # Convert flag-name to arg_name
            
            # Check if this argument was provided
            if hasattr(args, arg_name) and getattr(args, arg_name):
                dynamic_flags[placeholder_var.lower()] = getattr(args, arg_name)
    except Exception as e:
        # Fallback for common flags if dynamic discovery fails
        if hasattr(args, 'api_key') and args.api_key:
            dynamic_flags['api_key'] = args.api_key
        if hasattr(args, 'origin_host') and args.origin_host:
            dynamic_flags['origin_host'] = args.origin_host
        if hasattr(args, 'referer_host') and args.referer_host:
            dynamic_flags['referer_host'] = args.referer_host
    
    # Build configuration
    config = {
        'url': args.url,
        'instances': args.instances,
        'concurrent_per_instance': args.concurrent_per_instance,
        'duration': args.duration,
        'max_errors': args.max_errors,
        'delay': args.delay,
        'verbose': args.verbose,
        'debug': args.debug,
        'dynamic_flags': dynamic_flags
    }
    
    # Run the test
    tester = MultiInstanceLoadTester()
    try:
        await tester.run_test(config)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error running multi-instance test: {e}{Colors.NC}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
