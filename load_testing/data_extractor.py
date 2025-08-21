#!/usr/bin/env python3
"""
Load Test Data Extractor

This script extracts Body information from load test log files when verbose mode is enabled.
It parses response details and aggregates the data by attributes for comprehensive analysis.
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict


class LoadTestDataExtractor:
    def __init__(self, results_directory: str):
        """Initialize the extractor with the results directory path."""
        self.results_directory = Path(results_directory)
        self.extracted_data = []
        self.aggregated_data = defaultdict(list)
        
    def is_verbose_enabled(self, content: str) -> bool:
        """Check if verbose mode is enabled in the log file."""
        # Check for either old Node.js format or new Python format
        return ("Verbose: enabled" in content or 
                "--- Response Details ---" in content)
    
    def extract_response_details(self, content: str, file_name: str) -> List[Dict[str, Any]]:
        """Extract all response details from log content."""
        responses = []
        
        # Pattern to match response blocks
        response_pattern = r'--- Response Details ---\s*\n(.*?)--- End Response ---'
        response_blocks = re.findall(response_pattern, content, re.DOTALL)
        
        for idx, block in enumerate(response_blocks, 1):
            response_data = {}
            
            # Add unique identifier for this response
            file_base = file_name.replace('.log', '')
            response_data['response_id'] = f"{file_base}_{idx}"
            
            # Extract status
            status_match = re.search(r'Status:\s*(\d+)', block)
            if status_match:
                response_data['http_status'] = int(status_match.group(1))
                response_data['status'] = int(status_match.group(1))  # Keep for backward compatibility
                response_data['code'] = int(status_match.group(1))  # Alias for status
            
            # Extract response time
            time_match = re.search(r'Response Time:\s*(\d+)ms', block)
            if time_match:
                response_data['response_time_ms'] = int(time_match.group(1))
                response_data['time'] = int(time_match.group(1))  # Alias for response time
            
            # Extract template used (if present)
            template_match = re.search(r'Template Used:\s*([^-]+?)\s*-', block)
            if template_match:
                response_data['template_name'] = template_match.group(1).strip()
            
            # Extract headers
            headers_match = re.search(r'Headers:\s*(\{.*?\})', block, re.DOTALL)
            if headers_match:
                try:
                    headers_str = headers_match.group(1)
                    # The headers are already in valid JSON format from Python aiohttp
                    response_data['headers'] = json.loads(headers_str)
                except json.JSONDecodeError:
                    # Fallback for malformed headers
                    response_data['headers'] = {}
            
            # Extract body (this is the main focus)
            body_match = re.search(r'Body:\s*(.+)', block)
            if body_match:
                body_str = body_match.group(1).strip()
                try:
                    # Try to parse as JSON
                    body_json = json.loads(body_str)
                    response_data['body'] = body_json
                    
                    # Extract individual fields from body for direct access
                    # Prefix body fields to avoid conflicts with HTTP response fields
                    if isinstance(body_json, dict):
                        # Flatten nested objects with dot notation
                        flattened_data = self._flatten_dict(body_json)
                        
                        for key, value in flattened_data.items():
                            # Avoid overwriting HTTP response fields
                            if key not in ['status', 'code', 'time', 'response_id', 'http_status', 'response_time_ms']:
                                response_data[key] = value
                            else:
                                # Use body_ prefix for conflicting fields
                                response_data[f'body_{key}'] = value
                            
                except json.JSONDecodeError:
                    # If not JSON, store as string
                    response_data['body'] = body_str
            
            if response_data:  # Only add if we extracted some data
                responses.append(response_data)
        
        return responses
    
    def _flatten_dict(self, data: Dict[str, Any], prefix: str = '', separator: str = '.') -> Dict[str, Any]:
        """Flatten a nested dictionary using dot notation."""
        flattened = {}
        
        for key, value in data.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key
            
            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                flattened.update(self._flatten_dict(value, new_key, separator))
            elif isinstance(value, list):
                # Handle arrays - for now, just store the list as-is
                # Could be extended to flatten array elements if needed
                flattened[new_key] = value
            else:
                # Store primitive values
                flattened[new_key] = value
        
        return flattened
    
    def extract_test_configuration(self, content: str) -> Dict[str, Any]:
        """Extract test configuration information from log content."""
        config = {}
        
        # Extract basic configuration
        url_match = re.search(r'URL:\s*(.+)', content)
        if url_match:
            config['url'] = url_match.group(1).strip()
        
        concurrent_match = re.search(r'Concurrent:\s*(\d+)', content)
        if concurrent_match:
            config['concurrent'] = int(concurrent_match.group(1))
        
        duration_match = re.search(r'Duration:\s*(.+)', content)
        if duration_match:
            config['duration'] = duration_match.group(1).strip()
        
        delay_match = re.search(r'Delay:\s*(.+)', content)
        if delay_match:
            config['delay'] = delay_match.group(1).strip()
        
        # Extract final results
        results_section = re.search(r'LOAD TEST RESULTS\s*=+\s*(.*?)=+', content, re.DOTALL)
        if results_section:
            results_text = results_section.group(1)
            
            total_match = re.search(r'Total Requests:\s*(\d+)', results_text)
            if total_match:
                config['total_requests'] = int(total_match.group(1))
            
            successful_match = re.search(r'Successful:\s*(\d+)\s*\(([^)]+)\)', results_text)
            if successful_match:
                config['successful_requests'] = int(successful_match.group(1))
                config['success_percentage'] = successful_match.group(2)
            
            failed_match = re.search(r'Failed:\s*(\d+)\s*\(([^)]+)\)', results_text)
            if failed_match:
                config['failed_requests'] = int(failed_match.group(1))
                config['failure_percentage'] = failed_match.group(2)
            
            rps_match = re.search(r'Requests/sec:\s*([\d.]+)', results_text)
            if rps_match:
                config['requests_per_second'] = float(rps_match.group(1))
            
            avg_time_match = re.search(r'Avg Response Time:\s*(\d+)ms', results_text)
            if avg_time_match:
                config['avg_response_time_ms'] = int(avg_time_match.group(1))
            
            min_time_match = re.search(r'Min Response Time:\s*(\d+)ms', results_text)
            if min_time_match:
                config['min_response_time_ms'] = int(min_time_match.group(1))
            
            max_time_match = re.search(r'Max Response Time:\s*(\d+)ms', results_text)
            if max_time_match:
                config['max_response_time_ms'] = int(max_time_match.group(1))
        
        return config
    
    def process_log_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single log file and extract all relevant data."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if verbose is enabled
            if not self.is_verbose_enabled(content):
                print(f"⚠️  Verbose mode not enabled in {file_path.name}, skipping Body extraction")
                return {}
            
            # Extract data
            file_data = {
                'file_name': file_path.name,
                'file_path': str(file_path),
                'timestamp': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'configuration': self.extract_test_configuration(content),
                'responses': self.extract_response_details(content, file_path.name)
            }
            
            return file_data
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return {}
        except PermissionError:
            print(f"❌ Permission denied: {file_path}")
            return {}
        except UnicodeDecodeError:
            print(f"❌ Unable to decode file (encoding issue): {file_path}")
            return {}
        except Exception as e:
            print(f"❌ Unexpected error processing {file_path}: {e}")
            return {}
    
    def aggregate_by_attributes(self) -> Dict[str, Any]:
        """Aggregate all extracted data by attributes for analysis."""
        aggregated = {
            'summary': {
                'total_files_processed': len(self.extracted_data),
                'total_responses': sum(len(data.get('responses', [])) for data in self.extracted_data),
                'files_with_verbose': len([d for d in self.extracted_data if d.get('responses')]),
            },
            'configurations': [],
            'responses_by_status': defaultdict(list),
            'responses_by_body_type': defaultdict(list),
            'response_times': [],
            'body_messages': defaultdict(int),
            'headers_analysis': defaultdict(int),
            'errors_summary': defaultdict(int)
        }
        
        for file_data in self.extracted_data:
            if not file_data:
                continue
                
            # Collect configurations
            if file_data.get('configuration'):
                config_with_file = file_data['configuration'].copy()
                config_with_file['source_file'] = file_data['file_name']
                aggregated['configurations'].append(config_with_file)
            
            # Process responses
            for response in file_data.get('responses', []):
                status = response.get('status')
                body = response.get('body')
                response_time = response.get('response_time_ms')
                headers = response.get('headers', {})
                
                # Group by status
                if status:
                    aggregated['responses_by_status'][str(status)].append({
                        'file': file_data['file_name'],
                        'response_time_ms': response_time,
                        'body': body,
                        'headers': headers
                    })
                
                # Group by body type/content
                if body:
                    if isinstance(body, dict):
                        body_type = 'json_object'
                        # Extract message if present
                        if 'message' in body:
                            aggregated['body_messages'][body['message']] += 1
                        # Count error types
                        if status and isinstance(status, (int, str)):
                            status_code = int(status) if isinstance(status, str) else status
                            if status_code >= 400:
                                error_key = f"HTTP {status_code}: {json.dumps(body) if isinstance(body, dict) else str(body)}"
                                aggregated['errors_summary'][error_key] += 1
                    else:
                        body_type = 'string'
                    
                    aggregated['responses_by_body_type'][body_type].append({
                        'file': file_data['file_name'],
                        'status': status,
                        'response_time_ms': response_time,
                        'body': body
                    })
                
                # Collect response times
                if response_time:
                    aggregated['response_times'].append({
                        'file': file_data['file_name'],
                        'status': status,
                        'time_ms': response_time,
                        'body': body
                    })
                
                # Analyze headers
                for header, value in headers.items():
                    aggregated['headers_analysis'][header] += 1
        
        # Calculate response time statistics
        if aggregated['response_times']:
            times = [r['time_ms'] for r in aggregated['response_times'] if isinstance(r.get('time_ms'), (int, float))]
            if times:
                aggregated['response_time_stats'] = {
                    'count': len(times),
                    'min_ms': min(times),
                    'max_ms': max(times),
                    'avg_ms': sum(times) / len(times),
                    'median_ms': sorted(times)[len(times) // 2]
                }
        
        return dict(aggregated)
    
    def extract_specific_attributes(self, attributes: List[str], sort_values: bool = False, 
                                  sort_by: str = None, include_template: bool = False) -> Dict[str, Any]:
        """Extract only specific attributes from all responses."""
        if not self.extracted_data:
            # Need to process files first
            self.extract_all_data()
        
        # If sort_by is specified, use merged format
        if sort_by:
            return self._extract_merged_format(attributes, sort_by, include_template)
        
        # Original separate format
        result = {"result": {}}
        
        for attribute in attributes:
            result["result"][attribute] = []
            
            # Collect all values for this attribute across all files
            for file_data in self.extracted_data:
                for response in file_data.get('responses', []):
                    if attribute in response:
                        response_entry = {response['response_id']: response[attribute]}
                        
                        # Add template info if requested
                        if include_template and 'template_name' in response:
                            response_entry['template'] = response['template_name']
                        
                        result["result"][attribute].append(response_entry)
            
            # Sort if requested
            if sort_values:
                try:
                    result["result"][attribute].sort(key=lambda x: list(x.values())[0])
                except TypeError:
                    # Handle mixed types by converting to string for sorting
                    result["result"][attribute].sort(key=lambda x: str(list(x.values())[0]))
        
        return result
    
    def _extract_merged_format(self, attributes: List[str], sort_by: str, include_template: bool = False) -> Dict[str, Any]:
        """Extract attributes in merged format, sorted by specific attribute."""
        if not self.extracted_data:
            self.extract_all_data()
        
        result = {"result": []}
        merged_data = []
        
        # Collect all responses with their attributes
        for file_data in self.extracted_data:
            for response in file_data.get('responses', []):
                # Check if the sort_by attribute exists
                if sort_by in response:
                    response_obj = {}
                    response_id = response['response_id']
                    
                    # Create the merged object
                    response_obj[response_id] = {}
                    
                    # Add requested attributes
                    for attribute in attributes:
                        if attribute in response:
                            response_obj[response_id][attribute] = response[attribute]
                    
                    # Add template info if requested
                    if include_template and 'template_name' in response:
                        response_obj[response_id]['template'] = response['template_name']
                    
                    # Add sort value for sorting
                    response_obj['_sort_value'] = response[sort_by]
                    merged_data.append(response_obj)
        
        # Sort by the specified attribute
        try:
            merged_data.sort(key=lambda x: x['_sort_value'])
        except TypeError:
            # Handle mixed types by converting to string for sorting
            merged_data.sort(key=lambda x: str(x['_sort_value']))
        
        # Remove the sort helper and format result
        for item in merged_data:
            item.pop('_sort_value', None)
            result["result"].append(item)
        
        return result
    
    def extract_all_data(self) -> Dict[str, Any]:
        """Extract data from all log files in the results directory."""
        if not self.results_directory.exists():
            raise FileNotFoundError(f"Results directory not found: {self.results_directory}")
        
        # Find all .log files
        log_files = list(self.results_directory.glob("*.log"))
        
        if not log_files:
            raise FileNotFoundError(f"No .log files found in: {self.results_directory}")
        
        print(f"🔍 Found {len(log_files)} log file(s) to process...")
        
        # Process each file
        for log_file in log_files:
            print(f"📁 Processing: {log_file.name}")
            file_data = self.process_log_file(log_file)
            if file_data:
                self.extracted_data.append(file_data)
        
        # Aggregate the data
        print("📊 Aggregating data...")
        aggregated = self.aggregate_by_attributes()
        
        return {
            'extraction_timestamp': datetime.now().isoformat(),
            'source_directory': str(self.results_directory),
            'raw_data': self.extracted_data,
            'aggregated_analysis': aggregated
        }
    
    def save_results(self, output_file: str = None) -> str:
        """Save the extracted and aggregated data to a JSON file."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"load_test_analysis_{timestamp}.json"
        
        results = self.extract_all_data()
        
        output_path = self.results_directory / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to: {output_path}")
        return str(output_path)
    
    def print_summary(self):
        """Print a summary of the extracted data to console."""
        results = self.extract_all_data()
        analysis = results['aggregated_analysis']
        
        print("\n" + "="*60)
        print("           LOAD TEST DATA EXTRACTION SUMMARY")
        print("="*60)
        
        # Summary
        summary = analysis['summary']
        print(f"📁 Files processed: {summary['total_files_processed']}")
        print(f"📝 Files with verbose data: {summary['files_with_verbose']}")
        print(f"📊 Total responses extracted: {summary['total_responses']}")
        
        # Response time stats
        if 'response_time_stats' in analysis:
            stats = analysis['response_time_stats']
            print(f"\n⏱️  Response Time Statistics:")
            print(f"   Count: {stats['count']}")
            print(f"   Min: {stats['min_ms']}ms")
            print(f"   Max: {stats['max_ms']}ms")
            print(f"   Average: {stats['avg_ms']:.1f}ms")
            print(f"   Median: {stats['median_ms']}ms")
        
        # Status codes
        print(f"\n📈 Responses by Status Code:")
        for status, responses in analysis['responses_by_status'].items():
            print(f"   {status}: {len(responses)} responses")
        
        # Body messages
        if analysis['body_messages']:
            print(f"\n💬 Body Messages:")
            for message, count in analysis['body_messages'].items():
                print(f"   '{message}': {count} times")
        
        # Errors summary
        if analysis['errors_summary']:
            print(f"\n❌ Errors Summary:")
            for error, count in analysis['errors_summary'].items():
                print(f"   {error}: {count} times")
        
        # Most common headers
        if analysis['headers_analysis']:
            print(f"\n🔗 Most Common Headers:")
            sorted_headers = sorted(analysis['headers_analysis'].items(), 
                                  key=lambda x: x[1], reverse=True)[:5]
            for header, count in sorted_headers:
                print(f"   {header}: {count} times")
        
        print("="*60)


# Remove the main function as this will be accessed through the package
# The CLI functionality will be provided by the main.py entry point
