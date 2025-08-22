# 📈 Changelog

All notable changes to the Python Load Testing Suite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-08-21

### ✨ Added

#### Request Body Debugging
- **`--request` Flag** - New command-line flag to print request body being sent to the API
- **Request Details Output** - Shows template name, HTTP method, URL, headers, and JSON body
- **Multi-Instance Support** - Request details are captured in individual instance log files
- **Combined Debugging** - Use `--request` with `--verbose` to see both request and response data

#### Enhanced Debugging Experience
- **Clear Separation** - Distinct output for request data (what you send) vs response data (what you receive)
- **Template Visibility** - See which request template is being used for each request
- **Header Inspection** - View processed headers with environment variable substitutions
- **JSON Formatting** - Pretty-printed JSON for easy reading and debugging

### 🔧 Fixed
- **Multi-Instance Configuration** - Request flag now properly passed to subprocess instances
- **Output Buffering** - Added `PYTHONUNBUFFERED=1` and `flush=True` for reliable log capture
- **Subprocess Communication** - Improved handling of subprocess output in multi-instance mode

### 📖 Enhanced
- **Documentation** - Added comprehensive request/response debugging examples to README
- **Command Reference** - Updated global options table with `--request` flag
- **Usage Examples** - Added debugging examples in Quick Start section

## [1.1.0] - 2025-08-21

### ✨ Added

#### Random Functions System
- **Dynamic Value Generation** - Complete random function system for realistic load testing
- **Memory Feature** - Named value storage to maintain consistency across related fields
- **Quote Flexibility** - Support for both single and double quotes in function parameters

#### New Random Functions
- **`randomString(length, name="optional")`** - Generate random alphanumeric strings
- **`randomInt(min, max, name="optional")`** - Generate random integers within range
- **`randomFloat(min, max, decimals, name="optional")`** - Generate random floats with precision
- **`randomFloat(min, max, decimals, **suffix, name="optional")`** - Generate floats with fixed suffix digits
- **`randomUuid(name="optional")`** - Generate random UUID v4 identifiers
- **`randomDatetime(start="optional", end="optional", format="optional", name="optional")`** - Generate random datetime values

#### Integration
- **Config.json Support** - Use random functions in configuration headers and values
- **Template Support** - Use random functions in request-templates.json for dynamic payloads
- **Memory Persistence** - Named values remain consistent within single request processing
- **Mixed Usage** - Combine named (remembered) and unnamed (always random) functions

### 🔧 Fixed
- **URL Configuration** - Multi-instance mode now properly reads from config.json by default
- **Config Loading** - Both single and multi-instance modes use consistent configuration loading
- **Quote Handling** - Improved regex patterns for reliable parameter parsing

### 📚 Enhanced
- **Documentation** - Comprehensive random functions documentation in README.md
- **Examples** - Real-world usage examples for all random function types
- **Testing** - Extensive test coverage for memory features and edge cases

## [1.0.0] - 2025-01-21

### 🎉 Initial Release

This marks the first public release of the Python Load Testing Suite, a complete rewrite and enhancement of the previous Node.js + Bash implementation.

### ✨ Added

#### Core Features
- **Async Load Testing Engine** - High-performance HTTP load testing with `asyncio`
- **Multi-Instance Support** - Parallel test execution across multiple instances
- **Data Extraction Engine** - Business intelligence and performance analytics
- **Dynamic Configuration** - Environment variable substitution and CLI overrides
- **Request Templates** - Configurable test scenarios and payloads

#### CLI Interface
- **Single Instance Mode** - `python start.py single [concurrent] [duration]`
- **Multi-Instance Mode** - `python start.py multi [instances] [concurrent] [duration]`
- **Data Extraction Mode** - `python start.py extract [results_dir] [attributes]`
- **Comprehensive Options** - API keys, delays, error limits, verbose output

#### Advanced Features
- **Cross-Platform Support** - Windows, macOS, and Linux compatibility
- **Professional Error Handling** - Graceful degradation and comprehensive logging
- **Rich Data Analysis** - Extract business metrics, performance data, and API analytics
- **Template System** - Support for multiple request templates with tracking

#### Data Extraction Capabilities
- **Business Intelligence** - Entity IDs, amounts, balances, statuses
- **Performance Metrics** - Response times, success rates, throughput
- **API Analytics** - Rate limits, error patterns, HTTP headers
- **Flexible Output** - Separate format, merged format, template tracking, file output

### 🔧 Configuration
- **Dynamic Headers** - Environment variable substitution in configuration
- **CLI Overrides** - Override any configuration value via command line
- **Debug Mode** - Detailed configuration inspection and troubleshooting

### 📊 Performance Improvements
- **6x Faster Startup** - ~0.5 seconds vs ~3 seconds (Node.js + Bash)
- **Lower Memory Usage** - Single process vs multiple processes
- **Universal Platform Support** - All platforms vs Mac/Linux only
- **Professional Error Handling** - Comprehensive vs basic

### 📚 Documentation
- **Comprehensive README** - 500+ lines of detailed documentation
- **Usage Examples** - Real-world scenarios and best practices
- **API Reference** - Complete command and option documentation
- **Troubleshooting Guide** - Common issues and solutions

### 🤖 Development
- **Built with Cursor AI** - Enhanced development with AI assistance
- **Modern Python Architecture** - Clean, modular, and extensible design
- **Type Hints** - Improved code reliability and IDE support
- **Async/Await Patterns** - Modern Python concurrency

### 🗂️ Project Structure
```
load-testing/
├── start.py                  # Main CLI interface
├── load_testing/             # Core package
│   ├── tester.py             # Single instance async tester
│   ├── multi_instance.py     # Multi-instance orchestrator
│   ├── data_extractor.py     # Data extraction engine
│   ├── config.py             # Configuration loader
│   ├── templates.py          # Request template management
│   └── results.py            # Results container
├── config.json.example       # Configuration template
├── request-templates.json.example # Request templates
├── requirements.txt          # Python dependencies
├── README.md                 # Comprehensive documentation
├── LICENSE                   # MIT License
├── CONTRIBUTING.md           # Contribution guidelines
└── CHANGELOG.md              # This file
```

### 🔄 Migration from Legacy
Complete compatibility with previous Node.js + Bash version:

| Legacy Command | New Python Command |
|----------------|-------------------|
| `node loadTester.js URL 10 30` | `python start.py single 10 30 --url URL` |
| `./run-load-test.sh 3 5 30` | `python start.py multi 3 5 30` |
| Manual log parsing | `python start.py extract results_dir --all` |

### 🎯 Use Cases Supported
- **API Development** - Quick validation and integration testing
- **Performance Testing** - Load and stress testing
- **Business Intelligence** - Financial and operational data extraction
- **CI/CD Integration** - Automated testing with exit codes
- **Monitoring** - Health checks and uptime testing

### 📄 License
- **MIT License** - Free for commercial and personal use
- **Open Source** - Available on GitHub with full source code

### 🤝 Community
- **Contributing Guidelines** - Clear process for community contributions
- **Issue Templates** - Structured bug reports and feature requests
- **Documentation** - Comprehensive guides and examples

---

## 🚀 Future Releases

### Planned Features (Future Versions)

#### v1.1.0 (Planned)
- **Real-time Monitoring** - Live dashboards and metrics
- **Report Generation** - HTML/PDF performance reports
- **Plugin System** - Custom extractors and analyzers

#### v1.2.0 (Planned)
- **WebSocket Testing** - Real-time connection testing
- **gRPC Support** - Protocol buffer service testing
- **Docker Integration** - Containerized testing environments

#### v2.0.0 (Future)
- **Web UI** - Browser-based configuration and monitoring
- **Test Scenarios** - Complex multi-step test workflows
- **Load Balancing** - Distributed testing across multiple machines

---

## 📝 Release Notes Format

Each release follows this format:

### Version Number
- **Added** - New features and capabilities
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Now removed features
- **Fixed** - Bug fixes
- **Security** - Vulnerability fixes

---

## 🏷️ Version History

- **v1.0.0** - Initial public release (2025-01-21)
- **v0.x.x** - Internal development versions (Node.js + Bash)

---

*This project uses [Semantic Versioning](https://semver.org/) and was developed with assistance from [Cursor AI](https://cursor.sh).*
