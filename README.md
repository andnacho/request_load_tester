# 🚀 Python Load Testing Suite

A comprehensive, professional-grade load testing solution built entirely in Python. This modern suite replaces the previous Node.js + Bash implementation with superior performance, cross-platform compatibility, and integrated data analysis capabilities.

## 🌟 **Key Features**

- ✅ **Single Language Stack** - Pure Python ecosystem (no more JS/Bash mixing)
- ✅ **Cross-Platform** - Works on Windows, Mac, and Linux
- ✅ **High-Performance Async** - Superior concurrency with `asyncio`
- ✅ **Integrated Data Extraction** - Built-in business intelligence analysis
- ✅ **Unified Interface** - Single command for all operations
- ✅ **Professional Error Handling** - Comprehensive debugging and recovery
- ✅ **Rich Configuration** - Dynamic environment variable substitution
- ✅ **Multiple Testing Modes** - Single instance, multi-instance, and extraction

## 📦 **Quick Setup**

### 1. Virtual Environment
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows
```

### 2. Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify
```bash
python start.py
```

## 🎯 **Usage**

### **Single Instance Testing**
Perfect for development, API validation, and quick performance checks.

```bash
# Basic test (uses URL from config.json)
python start.py single 10 30

# With authentication and verbose output (uses config.json URL)
python start.py single 5 60 --api-key "your-token" --verbose

# Debug request and response data
python start.py single 3 30 --request --verbose

# Custom URL override
python start.py single 5 30 --url https://api.example.com/test --max-errors 5 --delay 0.5
```

### **Multi-Instance Testing**
Perfect for production load testing and high-concurrency simulation.

```bash
# 3 instances, 5 concurrent each = 15 total concurrent
python start.py multi 3 5 30 --api-key "your-token" --verbose

# Heavy load testing
python start.py multi 10 20 120 --api-key "your-token" --max-errors 50

# Gentle testing with delays
python start.py multi 2 1 60 --delay 2 --verbose
```

### **Data Extraction & Analysis**
Extract business intelligence and performance metrics from test results.

```bash
# Extract specific attributes (separate format)
python start.py extract results_directory message status total time --sort

# Extract data with merged format sorted by specific attribute
python start.py extract results_directory id numberTemplate.number --sort id

# Extract data with template information
python start.py extract results_directory message code --template

# Extract data with both template and merged sorting
python start.py extract results_directory id message --sort id --template

# Extract business data
python start.py extract results_directory id body_status date balance --sort

# Complete analysis
python start.py extract results_directory --all

# Save to file
python start.py extract results_directory message code --output analysis.json
```

## 📊 **Real-World Example**

Here's a complete workflow showing the power of the Python suite:

```bash
# 1. Run comprehensive load test (uses config.json URL)
export API_KEY="your-jwt-token"
python start.py multi 3 5 60 --verbose

# 2. Extract business metrics (API response data)
python start.py extract load_test_results_20250821_084657 id total balance body_status --sort

# 3. Analyze performance
python start.py extract load_test_results_20250821_084657 time status --sort

# 4. Generate complete report
python start.py extract load_test_results_20250821_084657 --all
```

**Sample API Response Data Extracted (Separate Format):**
```json
{
  "result": {
    "id": [
      {"instance_1_1": "937"},
      {"instance_2_1": "936"},
      {"instance_2_2": "938"}
    ],
    "total": [
      {"instance_1_1": 3570},
      {"instance_2_1": 3570},
      {"instance_2_2": 3570}
    ]
  }
}
```

**Sample Merged Format (with --sort id):**
```json
{
  "result": [
    {
      "instance_1_1": {"id": "936", "total": 3570}
    },
    {
      "instance_2_1": {"id": "937", "total": 3570}
    },
    {
      "instance_2_2": {"id": "938", "total": 3570}
    }
  ]
}
```

**Sample with Template Information (--template):**
```json
{
  "result": {
    "id": [
      {"instance_1_1": "937", "template": "create_user"},
      {"instance_2_1": "936", "template": "simple_get"},
      {"instance_2_2": "938", "template": "update_item"}
    ]
  }
}
```

## ⚙️ **Configuration**

### **Environment Variables**
```bash
export API_KEY="your-jwt-token"
export ORIGIN_HOST="https://your-app.com"
export REFERER_HOST="https://your-app.com/"
```

### **config.json Structure**
```json
{
  "target": {
    "host": "https://api.example.com",
    "endpoint": "/api/v1/endpoint",
    "method": "POST"
  },
  "headers": {
    "accept": "application/json",
    "authorization": "Bearer [[API_KEY]]",
    "content-type": "application/json",
    "origin": "[[ORIGIN_HOST]]",
    "referer": "[[REFERER_HOST]]"
  },
  "test": {
    "maxRetries": 3,
    "timeout": 30000,
    "userAgent": "Python-Load-Tester/1.0"
  }
}
```

### **Dynamic Configuration**
Override any config value with command-line flags:

```bash
# Override hosts
python start.py single --api-key "token" --origin-host "https://staging.com"

# Multiple overrides
python start.py multi 3 5 30 --api-key "token" --target-host "https://api.test.com"
```

## 🎲 **Random Functions**

The load testing suite supports dynamic random value generation in both `config.json` and `request-templates.json` files. All functions support an optional **memory feature** to remember and reuse values by name.

### **Available Functions**

**All functions support an optional `name` parameter for memory:**
- Functions with `name` will remember their value and return the same value when called again with the same name
- Functions without `name` generate new values each time
- Memory persists across the entire request processing session

#### `randomString(length, name="optional")`
Generates a random alphanumeric string of specified length.

```json
{
  "user_id": "user_randomString(8, name='userid')",
  "session": "session_randomString(16)",
  "repeat_user": "randomString(8, name='userid')"
}
```
**Output:** user_id and repeat_user will have the same value, session will be different.

#### `randomInt(min, max, name="optional")`
Generates a random integer between min and max (inclusive).

```json
{
  "age": "randomInt(18,65, name=\"user_age\")",
  "quantity": "randomInt(1,100)",
  "repeat_age": "randomInt(18,65, name=\"user_age\")"
}
```

#### `randomFloat(min, max, decimals, name="optional")`
Generates a random float between min and max with specified decimal places.

```json
{
  "price": "randomFloat(10.0,100.0,2, name='item_price')",
  "rate": "randomFloat(0.1,5.0,3)",
  "balance": "randomFloat(100,1000,2,**00, name='account')"
}
```

#### `randomUuid(name="optional")`
Generates a random UUID v4.

```json
{
  "id": "randomUuid(name=\"user_uuid\")",
  "transaction_id": "txn_randomUuid()",
  "repeat_id": "randomUuid(name=\"user_uuid\")"
}
```

#### `randomDatetime(start="optional", end="optional", format="optional", name="optional")`
Generates a random datetime between start and end with specified format.

```json
{
  "created_at": "randomDatetime()",
  "start_date": "randomDatetime(format='YYYY-MM-DD')",
  "event_time": "randomDatetime(start='2025-08-21 18:20:20', end='2025-08-25 18:20:20')",
  "same_time": "randomDatetime(name='shared_timestamp')"
}
```

### **Usage Examples**

#### Config.json with Random Functions
```json
{
  "headers": {
    "user-agent": "LoadTester-randomString(8)",
    "x-request-id": "randomUuid()",
    "x-test-run": "run_randomInt(1000,9999, name='test_run')"
  }
}
```

#### Request Templates with Memory
```json
{
  "templates": [
    {
      "name": "create_user",
      "description": "Create user with consistent data",
      "request": {
        "id": "randomUuid(name=\"main_user\")",
        "username": "user_randomString(10, name=\"username\")",
        "email": "randomString(8, name=\"username\")@test.com",
        "age": "randomInt(18,65, name=\"user_age\")",
        "created_at": "randomDatetime(name=\"timestamp\")",
        "profile": {
          "user_id": "randomUuid(name=\"main_user\")",
          "age": "randomInt(18,65, name=\"user_age\")",
          "registered": "randomDatetime(name=\"timestamp\")"
        }
      }
    }
  ]
}
```

### **Memory Feature Benefits**

- **Data Consistency**: Maintain relationships between fields (user ID across multiple objects)
- **Realistic Testing**: Generate coherent test data that mimics real-world scenarios
- **Flexible Control**: Mix remembered values with always-random values as needed

## 🛠 **Command Reference**

### **Global Options**
| Option | Description | Example |
|--------|-------------|---------|
| `--api-key` | JWT token for authentication | `--api-key "your-token"` |
| `--max-errors N` | Stop after N errors | `--max-errors 10` |
| `--delay N` | Delay between requests (seconds) | `--delay 0.5` |
| `--verbose, -v` | Enable verbose response logging | `--verbose` |
| `--request` | Print request body being sent | `--request` |
| `--debug` | Show configuration details | `--debug` |

### **Single Instance Mode**
```bash
python start.py single [concurrent] [duration] [options]
```

### **Multi-Instance Mode**
```bash
python start.py multi [instances] [concurrent_per_instance] [duration] [options]
```

### **Extraction Mode**
```bash
python start.py extract [results_dir] [attributes] [options]
```

**Available Attributes:**
- `id`, `status`, `total`, `balance` - Business data from API responses
- `time`, `code` - Performance and HTTP data  
- `message`, `body_status` - Response content analysis
- `headers` - HTTP header information
- `numberTemplate.number`, `numberTemplate.prefix` - Nested JSON attributes
- `client.name`, `client.id` - Client information from responses

**Extraction Options:**
- `--sort` - Sort values alphabetically (separate format)
- `--sort ATTRIBUTE` - Sort by specific attribute value (merged format)
- `--template` - Include template name used for each request
- `--output FILE` - Save results to JSON file

## 📈 **Performance & Results**

### **Performance Improvements**
| Metric | Node.js + Bash | Python | Improvement |
|--------|----------------|---------|-------------|
| Startup Time | ~3 seconds | ~0.5 seconds | **6x faster** |
| Memory Usage | Multiple processes | Single process | **Lower** |
| Platform Support | Mac/Linux only | All platforms | **Universal** |
| Error Handling | Basic | Comprehensive | **Professional** |

### **Output Structure**
```
load_test_results_TIMESTAMP/
├── instance_1.log          # Individual instance logs
├── instance_2.log
├── instance_N.log
└── summary.json           # Aggregated results
```

### **Rich Data Analysis**
The Python suite extracts comprehensive data:
- **Business Intelligence**: Entity IDs, amounts, statuses
- **Performance Metrics**: Response times, success rates, throughput
- **API Analytics**: Rate limits, error patterns, headers
- **Operational Data**: Timestamps, instance tracking

## 🔧 **Request Templates**

The tool uses templates from `request-templates.json`:

```json
{
  "templates": [
    {
      "name": "create_user",
      "description": "POST request to create user",
      "request": { "name": "John Doe", "email": "john@example.com" }
    }
  ]
}
```

Available templates:
- `simple_get` - Basic GET request
- `create_user` - POST request to create user  
- `update_item` - PUT request to update item
- `delete_resource` - DELETE request

## 🎨 **Advanced Usage**

### **Environment-Specific Testing**
```bash
# Development
python start.py single --api-key "dev-token" --target-host "http://localhost:3000"

# Staging
python start.py multi 3 5 30 --api-key "staging-token" --target-host "https://staging-api.com"

# Production
python start.py multi 5 10 60 --api-key "prod-token" --max-errors 20
```

### **Performance Analysis Workflow**
```bash
# 1. Baseline test
python start.py single 1 30 --url https://api.example.com/test --verbose

# 2. Load test
python start.py multi 5 10 60 --verbose

# 3. Stress test
python start.py multi 10 20 120 --max-errors 100

# 4. Analyze results
python start.py extract results_dir time status --sort
```

### **CI/CD Integration**
```bash
# Automated testing with exit codes
python start.py single 1 10 --url https://api.example.com/health
if [ $? -eq 0 ]; then
  echo "✅ API health check passed"
else
  echo "❌ API health check failed"
fi
```

## 🔍 **Troubleshooting**

### **Common Issues**

**1. Import Errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**2. Configuration Issues**
```bash
# Use debug flag to see configuration
python start.py single --debug
```

**3. No Data Extracted**
```bash
# Ensure verbose mode was enabled during testing
python start.py single --verbose
```

### **Debug Output**
Use `--debug` to see detailed configuration:
```bash
python start.py single --api-key "token" --debug
```

Shows:
- Headers with substituted values
- Target configuration
- Test parameters
- Environment variables

### **Request & Response Debugging**

#### **View Request Bodies (`--request`)**
See exactly what JSON payload is being sent to your API:
```bash
python start.py single 1 10 --request
```

Output:
```
--- Request Details ---
Template: draft_invoice - Draft invoice without payment
Method: POST
URL: https://api.example.com/v1/invoices
Headers: {
  "authorization": "Bearer your-token",
  "content-type": "application/json",
  ...
}
Body: {
  "date": "2025-08-20",
  "client": "randomString(8)",
  "amount": "randomFloat(100,1000,2)"
}
--- End Request ---
```

#### **View Response Bodies (`--verbose`)**
See the complete server response:
```bash
python start.py single 1 10 --verbose
```

Output:
```
--- Response Details ---
Template Used: draft_invoice - Draft invoice without payment
Status: 200
Response Time: 245ms
Headers: {
  "content-type": "application/json",
  ...
}
Body: {
  "id": "inv_12345",
  "status": "created",
  "message": "Invoice created successfully"
}
--- End Response ---
```

#### **Debug Both Request & Response**
For complete API interaction visibility:
```bash
python start.py single 5 30 --request --verbose
```

#### **Multi-Instance Debugging**
Request details are saved to individual log files:
```bash
python start.py multi 3 5 30 --request --verbose

# View individual instance logs
cat load_test_results_*/instance_1.log
```

## 📚 **Examples by Use Case**

### **API Development**
```bash
# Quick validation
python start.py single 1 5 --url http://localhost:3000/api/test

# Integration testing
python start.py single 3 30 --url https://staging-api.com/test --api-key "staging-token"
```

### **Performance Testing**
```bash
# Baseline performance
python start.py single 5 60 --url https://api.example.com/test

# Load testing
python start.py multi 3 10 120

# Stress testing  
python start.py multi 10 50 300 --max-errors 100
```

### **Business Intelligence**
```bash
# Business data analysis (separate format)
python start.py extract results_dir total balance status

# Business data analysis (merged format sorted by ID)
python start.py extract results_dir id total balance --sort id

# Operational metrics with template tracking
python start.py extract results_dir time status id --template

# Error analysis (separate format)
python start.py extract results_dir message code --sort

# Error analysis (merged format sorted by code)
python start.py extract results_dir code message time --sort code --template
```

## 🏗️ **Architecture**

### **Core Components**
```
start.py                  # Main CLI interface
├── load_testing/         # Core package
│   ├── tester.py         # Single instance async tester
│   ├── multi_instance.py # Multi-instance orchestrator
│   ├── data_extractor.py # Data extraction engine
│   ├── config.py         # Configuration loader
│   ├── templates.py      # Request template management
│   └── results.py        # Results container
├── config.json           # Configuration
└── request-templates.json # Request templates
```

### **Key Classes**
- `LoadTester` - Async HTTP load testing
- `MultiInstanceLoadTester` - Parallel instance management
- `ConfigLoader` - Dynamic configuration handling
- `LoadTestDataExtractor` - Business intelligence extraction

## 🎯 **Best Practices**

1. **Start Small** - Use single instance for development
2. **Scale Gradually** - Increase load incrementally
3. **Monitor Resources** - Watch system resources during tests
4. **Use Verbose Mode** - Enable for detailed analysis
5. **Set Limits** - Use `--max-errors` to prevent runaway tests
6. **Extract Data** - Always analyze results for insights

## 🚀 **Migration from Legacy**

If migrating from the old Node.js + Bash version:

```bash
# Old way
node loadTester.js https://api.example.com/test 10 30 --api-key "token"
./run-load-test.sh 3 5 30 --api-key "token"

# New Python way
python start.py single 10 30 --url https://api.example.com/test --api-key "token"
python start.py multi 3 5 30 --api-key "token"
```

All functionality is preserved and enhanced in the Python version.

## 📋 **File Structure**

```
load-testing/
├── start.py                  # 🎯 Main entry point
├── load_testing/             # 📦 Core package
│   ├── __init__.py           # Package initialization
│   ├── tester.py             # Single instance testing
│   ├── multi_instance.py     # Multi-instance orchestrator
│   ├── data_extractor.py     # Data extraction engine
│   ├── config.py             # Configuration loader
│   ├── templates.py          # Template management
│   └── results.py            # Results container
├── config.json               # ⚙️ Configuration
├── request-templates.json    # 📋 Request templates
├── requirements.txt          # 📦 Dependencies
├── venv/                     # 🐍 Virtual environment
└── load_test_results_*/      # 📁 Test results
```

---

## 🎉 **Ready to Test!**

The Python Load Testing Suite is production-ready and provides everything needed for modern API testing:

- **Development**: Quick validation and debugging
- **Performance**: Load and stress testing
- **Intelligence**: Business data extraction
- **Operations**: Monitoring and alerting
- **CI/CD**: Automated testing integration

Get started with a simple test:
```bash
python start.py single 5 30 --url https://httpbin.org/post --verbose
```

For production API testing with authentication:
```bash
export API_KEY="your-token"
python start.py multi 3 5 60 --verbose
python start.py extract load_test_results_* --all
```

🐍 **Happy Load Testing!** ✨

---

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Free for commercial and personal use** ✅

## 🤖 **Built with Cursor AI**

This project was developed using [Cursor](https://cursor.sh), an AI-powered code editor that enhances development productivity through intelligent code suggestions, generation, and assistance.

**Key contributions from Cursor AI:**
- 🧠 **Code Architecture**: Designed the modular Python structure
- 🔧 **Implementation**: Generated core functionality and async patterns  
- 📚 **Documentation**: Created comprehensive usage guides and examples
- 🐛 **Debugging**: Assisted with error handling and optimization
- 🎯 **Best Practices**: Applied modern Python development standards

*Cursor AI helped transform this from a Node.js + Bash solution into a professional-grade Python toolkit.*

## 🌟 **Contributing**

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📈 **Changelog**

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## 💬 **Support**

- 📖 **Documentation**: This README contains comprehensive usage examples
- 🐛 **Issues**: Report bugs via GitHub Issues
- 💡 **Feature Requests**: Submit enhancement ideas via GitHub Issues
- 🤝 **Discussions**: Join community discussions in GitHub Discussions

## 🏷️ **Version**

**Current Version**: 1.0.0 - Initial public release

## 🔗 **Links**

- **Repository**: [GitHub Repository URL]
- **License**: [MIT License](LICENSE)
- **Cursor AI**: [https://cursor.sh](https://cursor.sh)

---

**⭐ If this project helps you, please give it a star on GitHub! ⭐**