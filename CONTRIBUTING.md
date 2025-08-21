# 🤝 Contributing to Python Load Testing Suite

Thank you for your interest in contributing to the Python Load Testing Suite! We welcome contributions from the community and appreciate your help in making this project better.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## 📜 Code of Conduct

This project adheres to a simple code of conduct:

- **Be respectful** and inclusive in all interactions
- **Be constructive** in feedback and discussions
- **Focus on the code**, not the person
- **Help others** learn and grow

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- Git
- Basic understanding of async/await patterns
- Familiarity with HTTP APIs and load testing concepts

### Quick Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/load-testing.git
   cd load-testing
   ```

3. **Set up development environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Verify setup**:
   ```bash
   python start.py single 1 5 --url https://httpbin.org/post --verbose
   ```

## 💡 How to Contribute

### 🐛 Bug Reports

Found a bug? Please:

1. **Check existing issues** to avoid duplicates
2. **Create a detailed issue** with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS)
   - Relevant logs or error messages

### ✨ Feature Requests

Have an idea? We'd love to hear it:

1. **Check existing issues** for similar requests
2. **Create an issue** describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Why this would benefit other users
   - Implementation considerations

### 🔧 Code Contributions

Ready to code? Here's how:

1. **Choose an issue** to work on (or create one)
2. **Comment on the issue** to let others know you're working on it
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** following our coding standards
5. **Test thoroughly** 
6. **Submit a pull request**

## 🛠️ Development Setup

### Project Structure

```
load_testing/
├── __init__.py           # Package initialization
├── tester.py             # Core load testing engine
├── multi_instance.py     # Multi-instance orchestration
├── data_extractor.py     # Data extraction and analysis
├── config.py             # Configuration management
├── templates.py          # Request template handling
└── results.py            # Results data structures
```

### Key Components

- **`LoadTester`**: Async HTTP load testing engine
- **`MultiInstanceLoadTester`**: Parallel instance management
- **`ConfigLoader`**: Dynamic configuration handling
- **`LoadTestDataExtractor`**: Business intelligence extraction

### Development Commands

```bash
# Run a quick test
python start.py single 1 5 --url https://httpbin.org/post

# Test multi-instance functionality
python start.py multi 2 2 10 --url https://httpbin.org/post

# Test data extraction
python start.py extract load_test_results_* message status --sort
```

## 📝 Coding Standards

### Python Style

- **Follow PEP 8** for code formatting
- **Use type hints** where appropriate
- **Write docstrings** for classes and functions
- **Keep functions focused** and single-purpose

### Example Code Style

```python
import asyncio
from typing import Optional, Dict, Any

class LoadTester:
    """Async HTTP load testing engine."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the load tester.
        
        Args:
            config: Configuration dictionary containing test parameters
        """
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def run_test(self, concurrent: int, duration: int) -> Dict[str, Any]:
        """Run load test with specified parameters.
        
        Args:
            concurrent: Number of concurrent requests
            duration: Test duration in seconds
            
        Returns:
            Test results dictionary
        """
        # Implementation here
        pass
```

### Async/Await Patterns

- **Use async/await** for all I/O operations
- **Properly handle** `aiohttp.ClientSession` lifecycle
- **Include error handling** with try/except blocks
- **Use asyncio.gather()** for concurrent operations

## 🧪 Testing Guidelines

### Manual Testing

Before submitting a PR, test your changes:

```bash
# Test single instance mode
python start.py single 5 30 --url https://httpbin.org/post --verbose

# Test multi-instance mode  
python start.py multi 3 2 20 --url https://httpbin.org/post --verbose

# Test data extraction
python start.py extract load_test_results_* message code --sort

# Test error handling
python start.py single 1 5 --url https://invalid-url.com --max-errors 1
```

### Configuration Testing

Test with different configurations:

```bash
# Test with custom headers
python start.py single 1 5 --api-key "test-token" --debug

# Test environment variable substitution
export API_KEY="test-value"
python start.py single 1 5 --debug
```

### Edge Cases

Test edge cases and error conditions:

- Invalid URLs
- Network timeouts
- Missing configuration files
- Invalid command line arguments
- Large concurrent loads

## 📮 Pull Request Process

### Before Submitting

1. **Ensure your code works** with the existing test suite
2. **Update documentation** if you've changed functionality
3. **Add comments** for complex logic
4. **Keep commits focused** - one feature/fix per commit

### PR Description Template

```markdown
## 🎯 Description
Brief description of what this PR does.

## 🔧 Changes Made
- List of specific changes
- New features added
- Bugs fixed

## 🧪 Testing
- [ ] Tested single instance mode
- [ ] Tested multi-instance mode  
- [ ] Tested data extraction
- [ ] Tested edge cases
- [ ] Updated documentation

## 📝 Notes
Any additional context or considerations.
```

### Review Process

1. **Automated checks** will run on your PR
2. **Maintainers will review** your code
3. **Address feedback** promptly
4. **Squash commits** if requested before merge

## 🐛 Issue Reporting

### Bug Report Template

```markdown
## 🐛 Bug Description
Clear description of the bug.

## 🔄 Steps to Reproduce
1. Step one
2. Step two
3. Expected result vs actual result

## 💻 Environment
- OS: (e.g., macOS 12.0, Ubuntu 20.04)
- Python version: (e.g., 3.9.0)
- Project version: (e.g., 1.0.0)

## 📋 Additional Context
Any other relevant information.
```

### Feature Request Template

```markdown
## ✨ Feature Description
What feature would you like to see?

## 🎯 Problem Statement
What problem does this solve?

## 💡 Proposed Solution
How would you implement this?

## 🔄 Alternatives Considered
What other approaches did you consider?

## 📊 Additional Context
Any other relevant information.
```

## 🏆 Recognition

Contributors will be recognized in:

- **README.md** - Contributors section
- **CHANGELOG.md** - Release notes
- **GitHub releases** - Release descriptions

## 📞 Getting Help

Need help contributing?

- **GitHub Issues**: For technical questions
- **GitHub Discussions**: For general questions
- **Code Comments**: For specific implementation questions

## 🙏 Thank You

Thank you for contributing to the Python Load Testing Suite! Your efforts help make this tool better for everyone.

---

*This project was built with assistance from [Cursor AI](https://cursor.sh), and we welcome both human and AI-assisted contributions that improve the codebase.*
