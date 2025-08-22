#!/usr/bin/env python3
"""
Load Testing Suite - Main Entry Point

A powerful, professional-grade load testing solution.
Usage: python start.py [command] [options]

Commands:
  single    Run single instance load test
  multi     Run multi-instance load test  
  extract   Extract and analyze test results

Examples:
  python start.py single 10 30 --verbose
  python start.py multi 3 5 60 --api-key YOUR_KEY
  python start.py extract results_dir id message --sort id
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Ensure Python version compatibility
if sys.version_info < (3, 7):
    print("❌ This tool requires Python 3.7 or higher")
    print(f"   Current version: {sys.version}")
    sys.exit(1)

# Import our load testing package
try:
    from load_testing import (
        ConfigLoader, LoadTester, LoadTestDataExtractor, 
        MultiInstanceLoadTester
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required files are in the same directory")
    sys.exit(1)

# Constants
DEFAULT_API_URL = "https://api.example.com/v1/endpoint"


class LoadTestingSuite:
    """Unified interface for all load testing operations."""
    
    def __init__(self):
        self.results_dir = None
    
    async def run_single_instance(self, args) -> dict:
        """Run a single instance load test."""
        print("🚀 Running single instance load test...")
        
        # Initialize config loader
        config_loader = ConfigLoader()
        
        # Build dynamic flags based on config placeholders
        dynamic_flags = self._build_dynamic_flags(args, config_loader)
        
        # Get config with dynamic flags
        loaded_config = config_loader.get_config(dynamic_flags)
        
        # Build URL
        url = args.url or f"{loaded_config.get('target', {}).get('host', '')}{loaded_config.get('target', {}).get('endpoint', '')}"
        
        if not url:
            raise ValueError('No URL provided. Please specify URL as argument or in config.json')
        
        # Build configuration
        config = {
            'url': url,
            'concurrent': args.concurrent,
            'duration': args.duration,
            'max_errors': args.max_errors,
            'delay': args.delay,
            'verbose': args.verbose,
            'debug': args.debug,
            'request': args.request,
            'loaded_config': loaded_config
        }
        
        # Print configuration if debug enabled
        if args.debug:
            self._print_debug_info(config, loaded_config)
        
        # Run the test
        tester = LoadTester(config_loader)
        results = await tester.run_test(config)
        
        return {
            'mode': 'single_instance',
            'config': config,
            'results': results
        }
    
    async def run_multi_instance(self, args) -> dict:
        """Run a multi-instance load test."""
        print("🚀 Running multi-instance load test...")
        
        # Initialize config loader
        config_loader = ConfigLoader()
        
        # Build dynamic flags based on config placeholders
        dynamic_flags = self._build_dynamic_flags(args, config_loader)
        
        # Get config with dynamic flags
        loaded_config = config_loader.get_config(dynamic_flags)
        
        # Build URL: use args.url if provided, otherwise build from config
        if hasattr(args, 'url') and args.url and args.url != DEFAULT_API_URL:
            # URL was explicitly provided, use it
            url = args.url
        else:
            # Build URL from config
            url = f"{loaded_config.get('target', {}).get('host', '')}{loaded_config.get('target', {}).get('endpoint', '')}"
            if not url:
                # Fallback to default if config is incomplete
                url = DEFAULT_API_URL
        
        # Build configuration
        config = {
            'url': url,
            'instances': args.instances,
            'concurrent_per_instance': args.concurrent,
            'duration': args.duration,
            'max_errors': args.max_errors,
            'delay': args.delay,
            'verbose': args.verbose,
            'debug': args.debug,
            'request': args.request,
            'dynamic_flags': dynamic_flags,
            'loaded_config': loaded_config
        }
        
        # Run the test
        tester = MultiInstanceLoadTester()
        summary = await tester.run_test(config)
        self.results_dir = Path(summary['execution_info']['results_directory'])
        
        return summary
    
    def _build_dynamic_flags(self, args, config_loader: ConfigLoader = None) -> dict:
        """Build dynamic flags from command line arguments based on config placeholders."""
        dynamic_flags = {}
        
        # Get config loader if not provided
        if config_loader is None:
            config_loader = ConfigLoader()
        
        # Discover all placeholder variables in config
        placeholder_vars = config_loader.discover_placeholder_variables()
        
        # For each placeholder, check if there's a corresponding command line argument
        for placeholder_var in placeholder_vars:
            flag_name = config_loader.get_flag_name_from_placeholder(placeholder_var)
            arg_name = flag_name.replace('-', '_')  # Convert flag-name to arg_name
            
            # Check if this argument was provided
            if hasattr(args, arg_name) and getattr(args, arg_name):
                dynamic_flags[placeholder_var.lower()] = getattr(args, arg_name)
        
        return dynamic_flags
    
    def _print_debug_info(self, config: dict, loaded_config: dict):
        """Print debug information if debug mode is enabled."""
        print('🔍 DEBUG: Configuration Details')
        print('━' * 50)
        print('📝 Headers from config.json:')
        
        headers = loaded_config.get('headers', {})
        if headers:
            for key, value in headers.items():
                print(f"  {key}: {value}")
        else:
            print('  No headers configured')
        
        print('\n🎯 Target configuration:')
        target = loaded_config.get('target', {})
        if target:
            for key, value in target.items():
                print(f"  {key}: {value}")
        
        print('\n⚙️  Test configuration:')
        test_config = loaded_config.get('test', {})
        if test_config:
            for key, value in test_config.items():
                print(f"  {key}: {value}")
        
        print('━' * 50)
        print()
    
    def print_help(self):
        """Print comprehensive help information."""
        # Discover dynamic flags
        try:
            config_loader = ConfigLoader()
            placeholder_vars = config_loader.discover_placeholder_variables()
            dynamic_flags_help = []
            for var in placeholder_vars:
                flag_name = config_loader.get_flag_name_from_placeholder(var)
                dynamic_flags_help.append(f"  --{flag_name}           Value for [[{var}]] in config.json")
        except Exception:
            dynamic_flags_help = ["  (Dynamic flags based on config.json placeholders)"]
        
        dynamic_flags_text = "\n".join(dynamic_flags_help) if dynamic_flags_help else "  (No dynamic flags detected)"
        
        print(f"""
🔥 Load Testing Suite - Professional Load Testing Tool

MODES:
  single    Run a single load testing instance
  multi     Run multiple load testing instances in parallel
  extract   Extract data from previous test results

EXAMPLES:

# Single instance test (uses URL from config.json)
python start.py single 10 30 --verbose

# Single instance test with custom URL
python start.py single 10 30 --url https://api.example.com/test --verbose

# Multi-instance test (3 instances, 5 concurrent each)
python start.py multi 3 5 30 --api-key YOUR_KEY --verbose

# Extract specific data from results
python start.py extract path/to/results message code --sort

# Extract data with merged format and templates
python start.py extract path/to/results id message --sort id --template

# Extract all data
python start.py extract path/to/results --all

SINGLE INSTANCE OPTIONS:
  concurrent           Number of concurrent requests (default: 5)
  duration            Test duration in seconds (default: 30)
  --url URL            Target URL (overrides config.json)
  
MULTI INSTANCE OPTIONS:
  instances           Number of instances (default: 3)
  concurrent          Concurrent requests per instance (default: 5)  
  duration            Test duration in seconds (default: 30)

EXTRACTION OPTIONS:
  results_dir         Path to results directory
  attributes          Specific attributes to extract (message, code, time, etc.)
  --sort [ATTR]       Sort values. If ATTR specified, use merged format sorted by that attribute
  --template          Include template information in the output
  --all               Extract all data (comprehensive analysis)

COMMON OPTIONS:
  --max-errors N      Maximum errors before stopping (default: 10)
  --delay N           Delay between requests in seconds (default: 0)
  --verbose, -v       Enable verbose output with response details
  --debug             Enable debug output
  --request           Print request body being sent

DYNAMIC CONFIG FLAGS (auto-detected from config.json):
{dynamic_flags_text}

For more detailed help on a specific mode:
  python start.py <mode> --help
        """)


def create_parser():
    """Create the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description='Load Testing Suite - Professional Load Testing Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # We'll handle help manually
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Testing mode')
    
    # Discover dynamic flags from config
    try:
        config_loader = ConfigLoader()
        placeholder_vars = config_loader.discover_placeholder_variables()
    except Exception:
        # If config loading fails, use empty list
        placeholder_vars = []
    
    # Single instance parser
    single_parser = subparsers.add_parser('single', help='Run single instance test')
    single_parser.add_argument('concurrent', nargs='?', type=int, default=5,
                              help='Concurrent requests (default: 5)')
    single_parser.add_argument('duration', nargs='?', type=int, default=30,
                              help='Duration in seconds (default: 30)')
    single_parser.add_argument('--url', help='Target URL (overrides config.json)')
    
    # Multi instance parser
    multi_parser = subparsers.add_parser('multi', help='Run multi-instance test')
    multi_parser.add_argument('instances', nargs='?', type=int, default=3,
                             help='Number of instances (default: 3)')
    multi_parser.add_argument('concurrent', nargs='?', type=int, default=5,
                             help='Concurrent per instance (default: 5)')
    multi_parser.add_argument('duration', nargs='?', type=int, default=30,
                             help='Duration in seconds (default: 30)')
    multi_parser.add_argument('--url', help='Target URL (overrides config.json)')
    
    # Extraction parser
    extract_parser = subparsers.add_parser('extract', help='Extract data from results')
    extract_parser.add_argument('results_dir', help='Results directory path')
    extract_parser.add_argument('attributes', nargs='*',
                               help='Attributes to extract (message, code, time, etc.)')
    extract_parser.add_argument('--sort', '-s', nargs='?', const=True, default=False,
                               help='Sort values. Optionally specify attribute to sort by for merged format.')
    extract_parser.add_argument('--template', action='store_true',
                               help='Include template information in the output')
    extract_parser.add_argument('--all', action='store_true',
                               help='Extract all data (full analysis)')
    extract_parser.add_argument('--output', '-o', help='Output file name')
    
    # Common options for single and multi
    for subparser in [single_parser, multi_parser]:
        subparser.add_argument('--max-errors', type=int, default=10,
                              help='Maximum errors before stopping (default: 10)')
        subparser.add_argument('--delay', type=float, default=0,
                              help='Delay between requests in seconds (default: 0)')
        subparser.add_argument('--verbose', '-v', action='store_true',
                              help='Enable verbose output')
        subparser.add_argument('--debug', action='store_true',
                              help='Enable debug output')
        subparser.add_argument('--request', action='store_true',
                              help='Print request body being sent')
        
        # Dynamically add arguments for all config placeholders
        for placeholder_var in placeholder_vars:
            try:
                config_loader = ConfigLoader()
                flag_name = config_loader.get_flag_name_from_placeholder(placeholder_var)
                help_text = f'Value for [[{placeholder_var}]] placeholder in config.json'
                subparser.add_argument(f'--{flag_name}', help=help_text)
            except Exception:
                # Skip if there's an issue with this placeholder
                continue
    
    return parser


async def main():
    """Main function."""
    parser = create_parser()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        suite = LoadTestingSuite()
        suite.print_help()
        return
    
    # Handle help manually
    if len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help', 'help']:
        suite = LoadTestingSuite()
        suite.print_help()
        return
    
    args = parser.parse_args()
    
    if not args.mode:
        suite = LoadTestingSuite()
        suite.print_help()
        return
    
    suite = LoadTestingSuite()
    
    try:
        if args.mode == 'single':
            await suite.run_single_instance(args)
        
        elif args.mode == 'multi':
            await suite.run_multi_instance(args)
        
        elif args.mode == 'extract':
            import json
            
            if args.all:
                # Extract all data
                extractor = LoadTestDataExtractor(args.results_dir)
                if args.output:
                    results_file = extractor.save_results(args.output)
                    print(f"📁 Complete analysis saved to: {results_file}")
                else:
                    extractor.print_summary()
            else:
                # Extract specific attributes
                if not args.attributes:
                    print("❌ Please specify attributes to extract or use --all for complete analysis")
                    print("Available attributes: message, code, status, time, response_time_ms, body, headers")
                    return
                
                extractor = LoadTestDataExtractor(args.results_dir)
                sort_by = args.sort if isinstance(args.sort, str) else None
                sort_values = bool(args.sort)
                result = extractor.extract_specific_attributes(args.attributes, sort_values, sort_by, args.template)
                
                if args.output:
                    output_path = Path(args.results_dir) / args.output
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    print(f"📁 Extracted data saved to: {output_path}")
                else:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
        
        else:
            print(f"❌ Unknown mode: {args.mode}")
            return
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
